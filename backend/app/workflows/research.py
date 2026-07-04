import asyncio
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
    NewsAnalysis,
    ResearchPlan,
    TechnicalIndicators,
)

logger = logging.getLogger(__name__)


class ResearchState(TypedDict, total=False):
    ticker: str
    planner: ResearchPlan
    financial: FinancialData
    news: NewsAnalysis
    technical: TechnicalIndicators
    report: InvestmentReport


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
        ticker = state["ticker"]
        logger.info("Step: collecting financial data for %s", ticker)
        result = await financial_agent.run(ticker)
        return {"financial": result}

    async def news_step(state: ResearchState) -> ResearchState:
        ticker = state["ticker"]
        logger.info("Step: analyzing news for %s", ticker)
        result = await news_agent.run(ticker)
        return {"news": result}

    async def technical_step(state: ResearchState) -> ResearchState:
        ticker = state["ticker"]
        logger.info("Step: computing technical indicators for %s", ticker)
        result = await technical_agent.run(ticker)
        return {"technical": result}

    async def report_step(state: ResearchState) -> ResearchState:
        ticker = state["ticker"]
        logger.info("Step: writing investment report for %s", ticker)
        result = await report_agent.run(
            ticker=ticker,
            financial=state["financial"],
            news=state["news"],
            technical=state["technical"],
        )
        return {"report": result}

    graph = StateGraph(ResearchState)

    graph.add_node("planner", plan_step)
    graph.add_node("financial", financial_step)
    graph.add_node("news", news_step)
    graph.add_node("technical", technical_step)
    graph.add_node("report_writer", report_step)

    # Planner runs first
    graph.add_edge(START, "planner")

    # After planner, fan out to three parallel research agents
    graph.add_edge("planner", "financial")
    graph.add_edge("planner", "news")
    graph.add_edge("planner", "technical")

    # All three converge into the report writer
    graph.add_edge("financial", "report_writer")
    graph.add_edge("news", "report_writer")
    graph.add_edge("technical", "report_writer")

    # Report writer is the final step
    graph.add_edge("report_writer", END)

    return graph


async def run_research(llm: ChatAnthropic, ticker: str) -> AnalysisResponse:
    graph = build_research_graph(llm)
    compiled = graph.compile()

    initial_state: ResearchState = {"ticker": ticker}
    final_state = await compiled.ainvoke(initial_state)

    return AnalysisResponse(
        ticker=ticker,
        planner=final_state.get("planner"),
        financial=final_state.get("financial"),
        news=final_state.get("news"),
        technical=final_state.get("technical"),
        report=final_state.get("report"),
    )
