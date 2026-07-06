import logging

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
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
        "indicators into a clear investment recommendation.\n\n"
        "You have access to tools for quantitative analysis:\n"
        "- calculate_valuation: Assess whether the stock is over/undervalued\n"
        "- assess_risk_level: Compute a risk score based on financial health and volatility\n"
        "- compute_price_target: Compute a blended 12-month price target\n\n"
        "Use ALL THREE tools FIRST to gather quantitative signals, then write your report "
        "referencing both the tool outputs and the raw data. "
        "Include the computed price target in your report. Be balanced.",
    ),
    (
        "human",
        "Write an investment report for {ticker} ({company_name}) "
        "based on the following research:\n\n"
        "## Financial Data\n{financial_summary}\n\n"
        "## News Analysis\n{news_summary}\n\n"
        "## Technical Indicators\n{technical_summary}\n\n"
        "First use your tools to analyze valuation, risk, and compute a price target, "
        "then provide your investment recommendation with a confidence score and 12-month target price.",
    ),
])


@tool
def calculate_valuation(
    pe_ratio: float | None,
    profit_margin: float | None,
    revenue_growth: float | None,
    debt_to_equity: float | None,
) -> str:
    """Assess stock valuation based on fundamental metrics.
    Returns a valuation assessment with reasoning."""
    signals: list[str] = []

    if pe_ratio is not None:
        if pe_ratio < 15:
            signals.append(f"P/E of {pe_ratio:.1f} suggests undervaluation")
        elif pe_ratio > 30:
            signals.append(f"P/E of {pe_ratio:.1f} indicates premium valuation")
        else:
            signals.append(f"P/E of {pe_ratio:.1f} is in fair value range")

    if profit_margin is not None:
        if profit_margin > 20:
            signals.append(f"Strong profit margin of {profit_margin:.1f}%")
        elif profit_margin < 5:
            signals.append(f"Thin profit margin of {profit_margin:.1f}%")
        else:
            signals.append(f"Moderate profit margin of {profit_margin:.1f}%")

    if revenue_growth is not None:
        if revenue_growth > 15:
            signals.append(f"High revenue growth of {revenue_growth:.1f}% YoY")
        elif revenue_growth < 0:
            signals.append(f"Revenue declining at {revenue_growth:.1f}% YoY")
        else:
            signals.append(f"Moderate revenue growth of {revenue_growth:.1f}% YoY")

    if debt_to_equity is not None:
        if debt_to_equity > 2.0:
            signals.append(f"High leverage with D/E ratio of {debt_to_equity:.2f}")
        elif debt_to_equity < 0.5:
            signals.append(f"Conservative leverage with D/E ratio of {debt_to_equity:.2f}")

    return "Valuation Assessment:\n" + "\n".join(f"- {s}" for s in signals) if signals else "Insufficient data for valuation assessment."


@tool
def assess_risk_level(
    debt_to_equity: float | None,
    rsi: float | None,
    atr: float | None,
    current_price: float | None,
    free_cash_flow: float | None,
) -> str:
    """Assess investment risk based on financial health and market volatility.
    Returns a risk score (1-10) with detailed breakdown."""
    risk_score = 5.0
    factors: list[str] = []

    if debt_to_equity is not None:
        if debt_to_equity > 2.0:
            risk_score += 2
            factors.append(f"High debt burden (D/E: {debt_to_equity:.2f}) +2 risk")
        elif debt_to_equity < 0.5:
            risk_score -= 1
            factors.append(f"Low leverage (D/E: {debt_to_equity:.2f}) -1 risk")

    if rsi is not None:
        if rsi > 75:
            risk_score += 1.5
            factors.append(f"Overbought territory (RSI: {rsi:.0f}) +1.5 risk")
        elif rsi < 25:
            risk_score += 1
            factors.append(f"Oversold territory (RSI: {rsi:.0f}) +1 risk")

    if atr is not None and current_price is not None and current_price > 0:
        volatility_pct = (atr / current_price) * 100
        if volatility_pct > 3:
            risk_score += 1
            factors.append(f"High volatility (ATR: {volatility_pct:.1f}% of price) +1 risk")
        elif volatility_pct < 1:
            risk_score -= 0.5
            factors.append(f"Low volatility (ATR: {volatility_pct:.1f}% of price) -0.5 risk")

    if free_cash_flow is not None:
        if free_cash_flow < 0:
            risk_score += 1.5
            factors.append("Negative free cash flow +1.5 risk")
        elif free_cash_flow > 0:
            risk_score -= 0.5
            factors.append("Positive free cash flow -0.5 risk")

    clamped = max(1, min(10, round(risk_score)))
    level = "Low" if clamped <= 3 else "Moderate" if clamped <= 6 else "High"

    return (
        f"Risk Score: {clamped}/10 ({level})\n"
        + "\n".join(f"- {f}" for f in factors)
    )


@tool
def compute_price_target(
    current_price: float | None,
    eps: float | None,
    pe_ratio: float | None,
    revenue_growth: float | None,
    profit_margin: float | None,
    sma_50: float | None,
    sma_200: float | None,
    fifty_two_week_high: float | None,
    fifty_two_week_low: float | None,
    technical_score: int | None,
    piotroski_score: int | None,
) -> str:
    """Compute a 12-month price target using multiple valuation methods.
    Blends PE-based, technical, and mean-reversion approaches into a weighted target."""
    if current_price is None or current_price <= 0:
        return "Cannot compute target: current price unavailable."

    estimates: list[tuple[str, float, float]] = []

    # Method 1: PE-based forward target
    if eps is not None and eps > 0 and pe_ratio is not None and pe_ratio > 0:
        growth = (revenue_growth or 5.0) / 100
        forward_eps = eps * (1 + growth)
        target_pe = pe_ratio * 0.95 if pe_ratio > 25 else pe_ratio * 1.05
        pe_target = forward_eps * target_pe
        if pe_target > 0:
            estimates.append(("PE-forward", pe_target, 0.35))

    # Method 2: Technical momentum target
    if sma_50 is not None and sma_200 is not None:
        if current_price > sma_50 > sma_200:
            momentum_target = current_price * 1.15
        elif current_price > sma_50:
            momentum_target = current_price * 1.08
        elif current_price < sma_50 < sma_200:
            momentum_target = current_price * 0.90
        else:
            momentum_target = current_price * 1.02
        estimates.append(("Technical-momentum", momentum_target, 0.20))

    # Method 3: 52-week mean reversion
    if fifty_two_week_high is not None and fifty_two_week_low is not None:
        midpoint = (fifty_two_week_high + fifty_two_week_low) / 2
        range_target = midpoint + (fifty_two_week_high - midpoint) * 0.3
        estimates.append(("52W-reversion", range_target, 0.15))

    # Method 4: Score-adjusted target
    if technical_score is not None and piotroski_score is not None:
        combined = (technical_score / 100 + piotroski_score / 9) / 2
        multiplier = 0.85 + (combined * 0.30)
        score_target = current_price * multiplier
        estimates.append(("Score-adjusted", score_target, 0.30))

    if not estimates:
        return "Insufficient data to compute a reliable price target."

    total_weight = sum(w for _, _, w in estimates)
    weighted_target = sum(t * w for _, t, w in estimates) / total_weight
    upside = ((weighted_target - current_price) / current_price) * 100

    lines = [
        f"Blended 12-Month Target: {weighted_target:.2f} ({upside:+.1f}% from {current_price:.2f})",
        "",
        "Method Breakdown:",
    ]
    for name, target, weight in estimates:
        pct = ((target - current_price) / current_price) * 100
        lines.append(f"  - {name}: {target:.2f} ({pct:+.1f}%) [weight: {weight:.0%}]")

    return "\n".join(lines)


ANALYSIS_TOOLS = [calculate_valuation, assess_risk_level, compute_price_target]


class ReportWriterAgent:
    def __init__(self, llm: ChatAnthropic) -> None:
        self.llm_with_tools = llm.bind_tools(ANALYSIS_TOOLS)
        self.llm_structured = llm.with_structured_output(InvestmentReport)

    async def run(
        self,
        ticker: str,
        financial: FinancialData,
        news: NewsAnalysis,
        technical: TechnicalIndicators,
        currency: str = "USD",
    ) -> InvestmentReport:
        logger.info("Report writer agent starting for ticker=%s", ticker)

        prompt_input = {
            "ticker": ticker,
            "company_name": financial.company_name,
            "financial_summary": self._format_financial(financial),
            "news_summary": self._format_news(news),
            "technical_summary": self._format_technical(technical),
        }
        messages = await REPORT_PROMPT.ainvoke(prompt_input)

        response = await self.llm_with_tools.ainvoke(messages)

        tool_results = []
        for tool_call in response.tool_calls:
            tool_fn = {t.name: t for t in ANALYSIS_TOOLS}.get(tool_call["name"])
            if tool_fn:
                result = tool_fn.invoke(tool_call["args"])
                tool_results.append(
                    ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                )
                logger.info("Tool %s executed for %s", tool_call["name"], ticker)

        if tool_results:
            followup_messages = messages.messages + [response] + tool_results
            followup_messages.append(
                HumanMessage(
                    content="Now write the final investment report based on all the data and your tool analysis. "
                    "Include the computed price target, the upside/downside percentage, "
                    "and a brief methodology explanation in your response."
                )
            )
            result = await self.llm_structured.ainvoke(followup_messages)
        else:
            result = await self.llm_structured.ainvoke(messages)

        result.ticker = ticker
        result.company_name = financial.company_name
        logger.info(
            "Report writer completed: recommendation=%s confidence=%.2f",
            result.recommendation,
            result.confidence_score,
        )
        return result

    def _format_financial(self, data: FinancialData) -> str:
        sym = "₹" if data.currency == "INR" else "$"

        def fmt(val: float | None, prefix: str = sym, suffix: str = "") -> str:
            if val is None:
                return "N/A"
            return f"{prefix}{val:,.2f}{suffix}"

        lines = [
            f"Company: {data.company_name} ({data.sector} / {data.industry})",
            f"Current Price: {fmt(data.current_price)}",
            f"Market Cap: {fmt(data.market_cap)}",
            f"Revenue: {fmt(data.revenue)}",
            f"Revenue Growth YoY: {fmt(data.revenue_growth, '', '%')}",
            f"Net Income: {fmt(data.net_income)}",
            f"Profit Margin: {fmt(data.profit_margin, '', '%')}",
            f"P/E Ratio: {fmt(data.pe_ratio, '')}",
            f"EPS: {fmt(data.eps)}",
            f"Cash: {fmt(data.cash)}",
            f"Debt: {fmt(data.debt)}",
            f"Debt-to-Equity: {fmt(data.debt_to_equity, '')}",
            f"Free Cash Flow: {fmt(data.free_cash_flow)}",
            f"ROE: {fmt(data.roe, '', '%')}",
            f"Dividend Yield: {fmt(data.dividend_yield, '', '%')}",
            f"Price-to-Book: {fmt(data.price_to_book, '')}",
            f"Piotroski F-Score: {data.piotroski_score}/9 ({data.fundamental_signal})",
            f"52W High: {fmt(data.fifty_two_week_high)}",
            f"52W Low: {fmt(data.fifty_two_week_low)}",
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
        def fmt(val: float | None, decimals: int = 2, prefix: str = "") -> str:
            if val is None:
                return "N/A"
            return f"{prefix}{val:.{decimals}f}"

        lines = [
            f"Trend: {data.trend}",
            f"RSI (14): {fmt(data.rsi)}",
            f"MACD: {fmt(data.macd, 4)}",
            f"MACD Signal: {fmt(data.macd_signal, 4)}",
            f"EMA 20: {fmt(data.ema_20)}",
            f"SMA 50: {fmt(data.sma_50)}",
            f"SMA 200: {fmt(data.sma_200)}",
            f"Bollinger Upper: {fmt(data.bollinger_upper)}",
            f"Bollinger Lower: {fmt(data.bollinger_lower)}",
            f"ATR: {fmt(data.atr)}",
            f"Technical Score: {data.technical_score}/100",
        ]
        return "\n".join(lines)
