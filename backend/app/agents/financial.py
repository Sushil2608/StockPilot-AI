import logging

import yfinance as yf

from app.schemas import FinancialData

logger = logging.getLogger(__name__)


class FinancialAgent:
    async def run(self, ticker: str) -> FinancialData:
        logger.info("Financial agent starting for ticker=%s", ticker)
        info = await self._fetch_info(ticker)
        result = FinancialData(
            ticker=ticker,
            company_name=info.get("longName", info.get("shortName", ticker)),
            revenue=info.get("totalRevenue"),
            market_cap=info.get("marketCap"),
            pe_ratio=info.get("trailingPE"),
            eps=info.get("trailingEps"),
            cash=info.get("totalCash"),
            debt=info.get("totalDebt"),
            roe=self._compute_roe(info),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            current_price=info.get("currentPrice", info.get("regularMarketPrice")),
        )
        logger.info("Financial agent completed for ticker=%s", ticker)
        return result

    async def _fetch_info(self, ticker: str) -> dict:
        stock = yf.Ticker(ticker)
        return stock.info

    def _compute_roe(self, info: dict) -> float | None:
        net_income = info.get("netIncomeToCommon")
        equity = info.get("totalStockholderEquity")
        if net_income is not None and equity and equity != 0:
            return round((net_income / equity) * 100, 2)
        return info.get("returnOnEquity")
