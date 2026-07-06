import logging
from typing import TypedDict

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END

from app.agents import (
    FinancialAgent,
    NewsAgent,
    PlannerAgent,
    ReportWriterAgent,
    TechnicalAgent,
)
from app.schemas import (
    AnalysisResponse,
    FinancialData,
    InvestmentReport,
    Market,
    NewsAnalysis,
    ResearchPlan,
    TechnicalIndicators,
)

logger = logging.getLogger(__name__)

MARKET_CONFIG = {
    Market.US: {"suffix": "", "currency": "USD", "currency_symbol": "$"},
    Market.INDIA: {"suffix": ".NS", "currency": "INR", "currency_symbol": "₹"},
}


class ResearchState(TypedDict, total=False):
    ticker: str
    market: str
    yf_ticker: str
    currency: str
    planner: ResearchPlan
    financial: FinancialData
    news: NewsAnalysis
    technical: TechnicalIndicators
    report: InvestmentReport
    errors: dict[str, str]


def _merge_errors(existing: dict[str, str], new: dict[str, str]) -> dict[str, str]:
    merged = dict(existing)
    merged.update(new)
    return merged


def build_research_graph(llm: ChatAnthropic) -> StateGraph:
    planner_agent = PlannerAgent(llm)
    financial_agent = FinancialAgent()
    news_agent = NewsAgent(llm)
    technical_agent = TechnicalAgent()
    report_agent = ReportWriterAgent(llm)

    async def plan_step(state: ResearchState) -> ResearchState:
        ticker = state["ticker"]
        logger.info("Step: planning research for %s", ticker)
        result = await planner_agent.run(ticker)
        return {"planner": result}

    async def financial_step(state: ResearchState) -> ResearchState:
        yf_ticker = state["yf_ticker"]
        market = state["market"]
        currency = state["currency"]
        try:
            logger.info("Step: collecting financial data for %s", yf_ticker)
            result = await financial_agent.run(yf_ticker, market, currency)
            result.ticker = state["ticker"]
            return {"financial": result}
        except Exception as e:
            logger.error("Financial agent failed for %s: %s", yf_ticker, e)
            fallback = FinancialData(
                ticker=state["ticker"], market=market,
                currency=currency, company_name=state["ticker"],
            )
            return {
                "financial": fallback,
                "errors": _merge_errors(state.get("errors", {}), {"financial": str(e)}),
            }

    async def news_step(state: ResearchState) -> ResearchState:
        yf_ticker = state["yf_ticker"]
        try:
            logger.info("Step: analyzing news for %s", yf_ticker)
            result = await news_agent.run(yf_ticker)
            result.ticker = state["ticker"]
            return {"news": result}
        except Exception as e:
            logger.error("News agent failed for %s: %s", yf_ticker, e)
            fallback = NewsAnalysis(
                ticker=state["ticker"], overall_sentiment="neutral",
                positive_developments=["News analysis unavailable"],
            )
            return {
                "news": fallback,
                "errors": _merge_errors(state.get("errors", {}), {"news": str(e)}),
            }

    async def technical_step(state: ResearchState) -> ResearchState:
        yf_ticker = state["yf_ticker"]
        try:
            logger.info("Step: computing technical indicators for %s", yf_ticker)
            result = await technical_agent.run(yf_ticker)
            result.ticker = state["ticker"]
            return {"technical": result}
        except Exception as e:
            logger.error("Technical agent failed for %s: %s", yf_ticker, e)
            fallback = TechnicalIndicators(ticker=state["ticker"])
            return {
                "technical": fallback,
                "errors": _merge_errors(state.get("errors", {}), {"technical": str(e)}),
            }

    async def report_step(state: ResearchState) -> ResearchState:
        ticker = state["ticker"]
        currency = state["currency"]
        try:
            logger.info("Step: writing investment report for %s", ticker)
            result = await report_agent.run(
                ticker=ticker,
                financial=state["financial"],
                news=state["news"],
                technical=state["technical"],
                currency=currency,
            )
            return {"report": result}
        except Exception as e:
            logger.error("Report writer failed for %s: %s", ticker, e)
            fallback = InvestmentReport(
                ticker=ticker, summary=f"Report generation failed: {e}",
                recommendation="Hold", confidence_score=0.0,
            )
            return {
                "report": fallback,
                "errors": _merge_errors(state.get("errors", {}), {"report": str(e)}),
            }

    graph = StateGraph(ResearchState)

    graph.add_node("planner", plan_step)
    graph.add_node("financial", financial_step)
    graph.add_node("news", news_step)
    graph.add_node("technical", technical_step)
    graph.add_node("report_writer", report_step)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "financial")
    graph.add_edge("planner", "news")
    graph.add_edge("planner", "technical")
    graph.add_edge("financial", "report_writer")
    graph.add_edge("news", "report_writer")
    graph.add_edge("technical", "report_writer")
    graph.add_edge("report_writer", END)

    return graph


async def run_research(
    llm: ChatAnthropic, ticker: str, market: Market
) -> AnalysisResponse:
    config = MARKET_CONFIG[market]
    yf_ticker = f"{ticker}{config['suffix']}"

    graph = build_research_graph(llm)
    compiled = graph.compile()

    initial_state: ResearchState = {
        "ticker": ticker,
        "market": market.value,
        "yf_ticker": yf_ticker,
        "currency": config["currency"],
        "errors": {},
    }
    final_state = await compiled.ainvoke(initial_state)

    return AnalysisResponse(
        ticker=ticker,
        market=market.value,
        currency=config["currency"],
        planner=final_state.get("planner"),
        financial=final_state.get("financial"),
        news=final_state.get("news"),
        technical=final_state.get("technical"),
        report=final_state.get("report"),
    )
