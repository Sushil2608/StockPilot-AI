import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.config import get_settings
from app.schemas import (
    AgentStatus,
    AgentStatusEnum,
    AnalysisRequest,
    AnalysisResponse,
)
from app.services.llm import get_llm
from app.workflows.research import build_research_graph, run_research

logger = logging.getLogger(__name__)

router = APIRouter()

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


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest) -> AnalysisResponse:
    ticker = request.ticker.upper()
    logger.info("Analysis requested for ticker=%s", ticker)
    llm = get_llm()
    return await run_research(llm, ticker)


@router.post("/analyze/stream")
async def analyze_stream(request: AnalysisRequest) -> EventSourceResponse:
    ticker = request.ticker.upper()
    logger.info("Streaming analysis requested for ticker=%s", ticker)
    return EventSourceResponse(
        _stream_analysis(ticker),
        media_type="text/event-stream",
    )


async def _stream_analysis(ticker: str) -> AsyncGenerator[dict, None]:
    llm = get_llm()
    graph = build_research_graph(llm)
    compiled = graph.compile()

    accumulated_state: dict = {"ticker": ticker}

    async for chunk in compiled.astream(
        {"ticker": ticker}, stream_mode="updates"
    ):
        for node_name, node_output in chunk.items():
            display_name = NODE_DISPLAY_NAMES.get(node_name)
            if not display_name:
                continue

            status = AgentStatus(
                agent=display_name,
                status=AgentStatusEnum.COMPLETED,
            )
            yield {"event": "agent_status", "data": status.model_dump_json()}

            if isinstance(node_output, dict):
                accumulated_state.update(node_output)
                for key, value in node_output.items():
                    if hasattr(value, "model_dump_json"):
                        yield {
                            "event": f"result_{key}",
                            "data": value.model_dump_json(),
                        }

    response = AnalysisResponse(
        ticker=ticker,
        planner=accumulated_state.get("planner"),
        financial=accumulated_state.get("financial"),
        news=accumulated_state.get("news"),
        technical=accumulated_state.get("technical"),
        report=accumulated_state.get("report"),
    )
    yield {"event": "complete", "data": response.model_dump_json()}
