import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException, Path, Request
from sse_starlette.sse import EventSourceResponse

from app.config import get_settings
import yfinance as yf

from app.agents.technical import TechnicalAgent
from app.schemas import (
    AgentStatus,
    AgentStatusEnum,
    AnalysisRequest,
    AnalysisResponse,
    Market,
    PriceHistoryResponse,
)
from app.services.llm import get_llm
from app.services.rate_limit import InMemoryRateLimiter, RateLimitExceeded
from app.services.ticker import InvalidTickerError, validate_ticker
from app.workflows.research import MARKET_CONFIG, build_research_graph, run_research

PERIOD_MAP = {
    "5d": ("5d", "5m"),
    "1mo": ("1mo", "1d"),
    "3mo": ("3mo", "1d"),
    "6mo": ("6mo", "1d"),
    "1y": ("1y", "1d"),
    "5y": ("5y", "1wk"),
}

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()
analysis_limiter = InMemoryRateLimiter(
    settings.analysis_rate_limit_count,
    settings.analysis_rate_limit_window_seconds,
)

NODE_DISPLAY_NAMES = {
    "planner": "Planner",
    "financial": "Financial Agent",
    "news": "News Agent",
    "technical": "Technical Agent",
    "report_writer": "Report Writer",
}


@router.get("/")
async def root() -> dict[str, str]:
    settings = get_settings()
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "An Agentic AI-powered Stock Research Assistant",
    }


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "healthy",
        "version": settings.app_version,
    }


def _limit_analysis_request(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    try:
        analysis_limiter.check(client_ip)
    except RateLimitExceeded as error:
        raise HTTPException(
            status_code=429,
            detail="Too many analyses. Please wait before trying again.",
            headers={"Retry-After": str(error.retry_after)},
        ) from error


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: Request, body: AnalysisRequest) -> AnalysisResponse:
    _limit_analysis_request(request)
    ticker = body.ticker
    market = body.market
    config = MARKET_CONFIG[market]
    yf_ticker = f"{ticker}{config['suffix']}"
    logger.info("Analysis requested for ticker=%s market=%s", ticker, market.value)
    try:
        async with asyncio.timeout(settings.analysis_timeout_seconds):
            async with asyncio.timeout(settings.ticker_validation_timeout_seconds):
                await validate_ticker(yf_ticker)
            llm = get_llm()
            return await run_research(llm, ticker, market)
    except InvalidTickerError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except TimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail="The analysis timed out. Please try again later.",
        ) from e


@router.post("/analyze/stream")
async def analyze_stream(request: Request, body: AnalysisRequest) -> EventSourceResponse:
    _limit_analysis_request(request)
    ticker = body.ticker
    market = body.market
    config = MARKET_CONFIG[market]
    yf_ticker = f"{ticker}{config['suffix']}"
    logger.info("Streaming analysis requested for ticker=%s market=%s", ticker, market.value)
    try:
        async with asyncio.timeout(settings.ticker_validation_timeout_seconds):
            await validate_ticker(yf_ticker)
    except InvalidTickerError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except TimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail="Ticker validation timed out. Please try again later.",
        ) from e
    return EventSourceResponse(
        _stream_analysis(ticker, market),
        media_type="text/event-stream",
    )


async def _stream_analysis(ticker: str, market: Market) -> AsyncGenerator[dict, None]:
    try:
        yield {
            "event": "agent_status",
            "data": AgentStatus(
                agent="Planner", status=AgentStatusEnum.RUNNING
            ).model_dump_json(),
        }

        llm = get_llm()
        config = MARKET_CONFIG[market]
        yf_ticker = f"{ticker}{config['suffix']}"
        graph = build_research_graph(llm)
        compiled = graph.compile()
        accumulated_state: dict = {
            "ticker": ticker,
            "market": market.value,
            "currency": config["currency"],
        }

        async with asyncio.timeout(settings.analysis_timeout_seconds):
            async for chunk in compiled.astream(
                {"ticker": ticker, "market": market.value, "yf_ticker": yf_ticker, "currency": config["currency"], "errors": {}},
                stream_mode="updates",
            ):
                for node_name, node_output in chunk.items():
                    display_name = NODE_DISPLAY_NAMES.get(node_name)
                    if not display_name:
                        continue

                    errors = node_output.get("errors", {}) if isinstance(node_output, dict) else {}
                    agent_had_error = node_name in errors or (
                        isinstance(node_output, dict)
                        and node_name in node_output.get("errors", {})
                    )

                    status = AgentStatus(
                        agent=display_name,
                        status=AgentStatusEnum.ERROR if agent_had_error else AgentStatusEnum.COMPLETED,
                        message=errors.get(node_name, ""),
                    )
                    yield {"event": "agent_status", "data": status.model_dump_json()}

                    if isinstance(node_output, dict):
                        accumulated_state.update(node_output)
                        for key, value in node_output.items():
                            if key == "errors":
                                continue
                            if hasattr(value, "model_dump_json"):
                                yield {
                                    "event": f"result_{key}",
                                    "data": value.model_dump_json(),
                                }
    except TimeoutError:
        yield {
            "event": "error",
            "data": json.dumps("The analysis timed out. Please try again later."),
        }
        return
    except Exception:
        logger.exception("Streaming analysis failed for ticker=%s", ticker)
        yield {
            "event": "error",
            "data": json.dumps(
                "Analysis failed. Check the backend logs for details."
            ),
        }
        return

    response = AnalysisResponse(
        ticker=ticker,
        market=market.value,
        currency=config["currency"],
        planner=accumulated_state.get("planner"),
        financial=accumulated_state.get("financial"),
        news=accumulated_state.get("news"),
        technical=accumulated_state.get("technical"),
        report=accumulated_state.get("report"),
    )
    yield {"event": "complete", "data": response.model_dump_json()}


@router.get("/price-history/{ticker}", response_model=PriceHistoryResponse)
async def price_history(
    ticker: str = Path(
        ..., min_length=1, max_length=15, pattern=r"^[A-Za-z0-9][A-Za-z0-9.&-]*$"
    ),
    period: str = "1mo",
    market: str = "US",
) -> PriceHistoryResponse:
    if period not in PERIOD_MAP:
        raise HTTPException(status_code=400, detail=f"Invalid period. Use: {', '.join(PERIOD_MAP)}")

    try:
        market_enum = Market(market)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid market. Use: US or IN")

    config = MARKET_CONFIG[market_enum]
    yf_ticker = f"{ticker.upper()}{config['suffix']}"
    yf_period, yf_interval = PERIOD_MAP[period]

    try:
        async with asyncio.timeout(settings.ticker_validation_timeout_seconds):
            df = await asyncio.to_thread(
                _load_price_history, yf_ticker, yf_period, yf_interval
            )
    except TimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail="Price history lookup timed out. Please try again later.",
        ) from e

    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data for {ticker}")

    date_fmt = "%Y-%m-%d %H:%M" if yf_interval in ("5m", "15m", "1h") else "%Y-%m-%d"
    points = [
        {
            "date": idx.strftime(date_fmt),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": round(float(row.get("Volume", 0))),
        }
        for idx, row in df.iterrows()
    ]

    return PriceHistoryResponse(
        ticker=ticker.upper(),
        period=period,
        currency=config["currency"],
        data=points,
    )


def _load_price_history(ticker: str, period: str, interval: str):
    return yf.Ticker(ticker).history(period=period, interval=interval)
