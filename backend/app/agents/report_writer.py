import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

from app.schemas import (
    FinancialData,
    InvestmentReport,
    NewsAnalysis,
    TechnicalIndicators,
)

logger = logging.getLogger(__name__)

REPORT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a senior investment analyst writing a comprehensive report. "
        "Synthesize the provided financial data, news analysis, and technical "
        "indicators into a clear investment recommendation. "
        "Reference specific evidence from each data source. "
        "Be balanced — acknowledge both strengths and risks.",
    ),
    (
        "human",
        "Write an investment report for {ticker} ({company_name}) "
        "based on the following research:\n\n"
        "## Financial Data\n{financial_summary}\n\n"
        "## News Analysis\n{news_summary}\n\n"
        "## Technical Indicators\n{technical_summary}\n\n"
        "Provide your investment recommendation with a confidence score.",
    ),
])


class ReportWriterAgent:
    def __init__(self, llm: ChatAnthropic) -> None:
        self.chain = REPORT_PROMPT | llm.with_structured_output(
            InvestmentReport
        )

    async def run(
        self,
        ticker: str,
        financial: FinancialData,
        news: NewsAnalysis,
        technical: TechnicalIndicators,
    ) -> InvestmentReport:
        logger.info("Report writer agent starting for ticker=%s", ticker)
        result = await self.chain.ainvoke({
            "ticker": ticker,
            "company_name": financial.company_name,
            "financial_summary": self._format_financial(financial),
            "news_summary": self._format_news(news),
            "technical_summary": self._format_technical(technical),
        })
        result.ticker = ticker
        result.company_name = financial.company_name
        logger.info(
            "Report writer completed: recommendation=%s confidence=%.2f",
            result.recommendation,
            result.confidence_score,
        )
        return result

    def _format_financial(self, data: FinancialData) -> str:
        lines = [
            f"Company: {data.company_name}",
            f"Current Price: ${data.current_price:,.2f}" if data.current_price else "Current Price: N/A",
            f"Market Cap: ${data.market_cap:,.0f}" if data.market_cap else "Market Cap: N/A",
            f"Revenue: ${data.revenue:,.0f}" if data.revenue else "Revenue: N/A",
            f"P/E Ratio: {data.pe_ratio:.2f}" if data.pe_ratio else "P/E Ratio: N/A",
            f"EPS: ${data.eps:.2f}" if data.eps else "EPS: N/A",
            f"Cash: ${data.cash:,.0f}" if data.cash else "Cash: N/A",
            f"Debt: ${data.debt:,.0f}" if data.debt else "Debt: N/A",
            f"ROE: {data.roe:.2f}%" if data.roe else "ROE: N/A",
        ]
        return "\n".join(lines)

    def _format_news(self, data: NewsAnalysis) -> str:
        lines = [f"Overall Sentiment: {data.overall_sentiment}"]
        if data.positive_developments:
            lines.append("Positive:")
            lines.extend(f"  - {d}" for d in data.positive_developments)
        if data.negative_developments:
            lines.append("Negative:")
            lines.extend(f"  - {d}" for d in data.negative_developments)
        return "\n".join(lines)

    def _format_technical(self, data: TechnicalIndicators) -> str:
        lines = [
            f"Trend: {data.trend}",
            f"RSI (14): {data.rsi:.2f}" if data.rsi else "RSI: N/A",
            f"MACD: {data.macd:.4f}" if data.macd else "MACD: N/A",
            f"MACD Signal: {data.macd_signal:.4f}" if data.macd_signal else "MACD Signal: N/A",
            f"SMA 50: ${data.sma_50:,.2f}" if data.sma_50 else "SMA 50: N/A",
            f"SMA 200: ${data.sma_200:,.2f}" if data.sma_200 else "SMA 200: N/A",
        ]
        return "\n".join(lines)
