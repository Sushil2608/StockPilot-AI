import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

from app.schemas import ResearchPlan

logger = logging.getLogger(__name__)

PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a senior equity research analyst. "
        "Given a stock ticker, create a structured research plan. "
        "Identify the company name and list the concrete research steps needed "
        "to produce a comprehensive investment report.",
    ),
    (
        "human",
        "Create a research plan for the stock ticker: {ticker}",
    ),
])


class PlannerAgent:
    def __init__(self, llm: ChatAnthropic) -> None:
        self.chain = PLANNER_PROMPT | llm.with_structured_output(ResearchPlan)

    async def run(self, ticker: str) -> ResearchPlan:
        logger.info("Planner agent starting for ticker=%s", ticker)
        result = await self.chain.ainvoke({"ticker": ticker})
        logger.info(
            "Planner agent completed: %d steps planned", len(result.steps)
        )
        return result
