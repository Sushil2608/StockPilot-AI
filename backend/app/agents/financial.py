import logging

import yfinance as yf
import pandas as pd

from app.schemas import FinancialData

logger = logging.getLogger(__name__)


def _safe_row(df: pd.DataFrame, label: str) -> pd.Series | None:
    try:
        row = df.loc[label].dropna().sort_index(ascending=False)
        return row if not row.empty else None
    except KeyError:
        return None


class FinancialAgent:
    async def run(
        self, ticker: str, market: str = "US", currency: str = "USD"
    ) -> FinancialData:
        logger.info("Financial agent starting for ticker=%s market=%s", ticker, market)
        stock = yf.Ticker(ticker)
        info = stock.info
        income_stmt = stock.income_stmt
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow

        fcf = self._extract_free_cash_flow(info, cashflow)
        roe = self._compute_roe(info)
        de = self._compute_debt_to_equity(info)

        fscore, fscore_details = self._compute_piotroski(
            info, income_stmt, balance_sheet, cashflow
        )

        signal = self._fundamental_signal(fscore, de, fcf)

        result = FinancialData(
            ticker=ticker,
            market=market,
            currency=currency,
            company_name=info.get("longName", info.get("shortName", ticker)),
            sector=info.get("sector", ""),
            industry=info.get("industry", ""),
            current_price=info.get("currentPrice", info.get("regularMarketPrice")),
            market_cap=info.get("marketCap"),
            revenue=info.get("totalRevenue"),
            revenue_growth=self._compute_revenue_growth(income_stmt),
            net_income=info.get("netIncomeToCommon"),
            profit_margin=self._compute_profit_margin(info),
            pe_ratio=info.get("trailingPE"),
            eps=info.get("trailingEps"),
            cash=info.get("totalCash"),
            debt=info.get("totalDebt"),
            debt_to_equity=de,
            free_cash_flow=fcf,
            roe=roe,
            dividend_yield=self._compute_dividend_yield(info),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            price_to_book=info.get("priceToBook"),
            piotroski_score=fscore,
            piotroski_details=fscore_details,
            fundamental_signal=signal,
        )
        logger.info(
            "Financial agent completed: F-Score=%s signal=%s", fscore, signal
        )
        return result

    def _compute_piotroski(
        self,
        info: dict,
        income_stmt: pd.DataFrame,
        balance_sheet: pd.DataFrame,
        cashflow: pd.DataFrame,
    ) -> tuple[int, list[str]]:
        score = 0
        details: list[str] = []

        total_assets = info.get("totalAssets")
        net_income = info.get("netIncomeToCommon")
        roa = (net_income / total_assets) if net_income and total_assets else None

        # 1. Positive ROA
        if roa is not None and roa > 0:
            score += 1
            details.append("Positive ROA")
        else:
            details.append("Negative/missing ROA")

        # 2. Positive operating cash flow
        ocf = info.get("operatingCashflow")
        if ocf is not None and ocf > 0:
            score += 1
            details.append("Positive operating cash flow")
        else:
            details.append("Negative/missing operating cash flow")

        # 3. ROA improving (current vs prior year)
        roa_row = _safe_row(income_stmt, "Net Income")
        assets_row = _safe_row(balance_sheet, "Total Assets")
        if roa_row is not None and assets_row is not None and len(roa_row) >= 2 and len(assets_row) >= 2:
            roa_curr = float(roa_row.iloc[0]) / float(assets_row.iloc[0]) if float(assets_row.iloc[0]) != 0 else 0
            roa_prev = float(roa_row.iloc[1]) / float(assets_row.iloc[1]) if float(assets_row.iloc[1]) != 0 else 0
            if roa_curr > roa_prev:
                score += 1
                details.append("ROA improving YoY")
            else:
                details.append("ROA declining YoY")
        else:
            details.append("Cannot compute ROA trend")

        # 4. Accruals: OCF/Assets > ROA (cash quality of earnings)
        if ocf is not None and total_assets and roa is not None:
            ocf_to_assets = ocf / total_assets
            if ocf_to_assets > roa:
                score += 1
                details.append("Cash earnings exceed accrual earnings")
            else:
                details.append("Accrual earnings exceed cash earnings")
        else:
            details.append("Cannot compute accruals quality")

        # 5. Declining leverage (long-term debt / total assets)
        debt_row = _safe_row(balance_sheet, "Long Term Debt")
        if debt_row is not None and assets_row is not None and len(debt_row) >= 2 and len(assets_row) >= 2:
            lev_curr = float(debt_row.iloc[0]) / float(assets_row.iloc[0]) if float(assets_row.iloc[0]) != 0 else 0
            lev_prev = float(debt_row.iloc[1]) / float(assets_row.iloc[1]) if float(assets_row.iloc[1]) != 0 else 0
            if lev_curr <= lev_prev:
                score += 1
                details.append("Leverage declining or stable")
            else:
                details.append("Leverage increasing")
        else:
            details.append("Cannot compute leverage trend")

        # 6. Current ratio improving
        cr_curr = info.get("currentRatio")
        if cr_curr is not None:
            score += 1 if cr_curr >= 1.0 else 0
            details.append(f"Current ratio: {cr_curr:.2f}" + (" (healthy)" if cr_curr >= 1.0 else " (below 1)"))
        else:
            details.append("Current ratio unavailable")

        # 7. No share dilution
        shares_row = _safe_row(balance_sheet, "Share Issued")
        if shares_row is not None and len(shares_row) >= 2:
            if float(shares_row.iloc[0]) <= float(shares_row.iloc[1]):
                score += 1
                details.append("No share dilution")
            else:
                details.append("Shares diluted YoY")
        else:
            details.append("Cannot compute dilution")

        # 8. Gross margin improving
        gm_row = _safe_row(income_stmt, "Gross Profit")
        rev_row = _safe_row(income_stmt, "Total Revenue")
        if gm_row is not None and rev_row is not None and len(gm_row) >= 2 and len(rev_row) >= 2:
            gm_curr = float(gm_row.iloc[0]) / float(rev_row.iloc[0]) if float(rev_row.iloc[0]) != 0 else 0
            gm_prev = float(gm_row.iloc[1]) / float(rev_row.iloc[1]) if float(rev_row.iloc[1]) != 0 else 0
            if gm_curr >= gm_prev:
                score += 1
                details.append("Gross margin improving")
            else:
                details.append("Gross margin declining")
        else:
            details.append("Cannot compute gross margin trend")

        # 9. Asset turnover improving
        if rev_row is not None and assets_row is not None and len(rev_row) >= 2 and len(assets_row) >= 2:
            at_curr = float(rev_row.iloc[0]) / float(assets_row.iloc[0]) if float(assets_row.iloc[0]) != 0 else 0
            at_prev = float(rev_row.iloc[1]) / float(assets_row.iloc[1]) if float(assets_row.iloc[1]) != 0 else 0
            if at_curr >= at_prev:
                score += 1
                details.append("Asset turnover improving")
            else:
                details.append("Asset turnover declining")
        else:
            details.append("Cannot compute asset turnover trend")

        return score, details

    def _fundamental_signal(
        self, fscore: int | None, de: float | None, fcf: float | None
    ) -> str:
        if fscore is None:
            return "neutral"
        if fscore >= 8:
            return "strong"
        if fscore >= 6:
            if de is not None and de > 2.0:
                return "neutral"
            return "healthy"
        if fscore >= 4:
            return "neutral"
        if fscore >= 2:
            return "weak"
        return "distressed"

    def _compute_revenue_growth(self, income_stmt: pd.DataFrame) -> float | None:
        if income_stmt.empty:
            return None
        row = _safe_row(income_stmt, "Total Revenue")
        if row is None or len(row) < 2:
            return None
        current = float(row.iloc[0])
        previous = float(row.iloc[1])
        if previous == 0:
            return None
        return round(((current - previous) / abs(previous)) * 100, 2)

    def _compute_profit_margin(self, info: dict) -> float | None:
        margin = info.get("profitMargins")
        if margin is not None:
            return round(margin * 100, 2)
        revenue = info.get("totalRevenue")
        net_income = info.get("netIncomeToCommon")
        if revenue and net_income and revenue != 0:
            return round((net_income / revenue) * 100, 2)
        return None

    def _compute_debt_to_equity(self, info: dict) -> float | None:
        ratio = info.get("debtToEquity")
        if ratio is not None:
            return round(ratio / 100, 2) if ratio > 5 else round(ratio, 2)
        debt = info.get("totalDebt")
        equity = info.get("totalStockholderEquity")
        if debt is not None and equity and equity != 0:
            return round(debt / equity, 2)
        return None

    def _extract_free_cash_flow(
        self, info: dict, cashflow: pd.DataFrame
    ) -> float | None:
        fcf = info.get("freeCashflow")
        if fcf is not None:
            return float(fcf)
        if cashflow.empty:
            return None
        try:
            operating = cashflow.loc["Total Cash From Operating Activities"].dropna()
            capex = cashflow.loc["Capital Expenditures"].dropna()
            if not operating.empty and not capex.empty:
                return float(operating.iloc[0]) + float(capex.iloc[0])
        except KeyError:
            pass
        return None

    def _compute_roe(self, info: dict) -> float | None:
        net_income = info.get("netIncomeToCommon")
        equity = info.get("totalStockholderEquity")
        if net_income is not None and equity and equity != 0:
            return round((net_income / equity) * 100, 2)
        roe = info.get("returnOnEquity")
        if roe is not None:
            return round(roe * 100, 2) if abs(roe) < 5 else round(roe, 2)
        return None

    def _compute_dividend_yield(self, info: dict) -> float | None:
        dy = info.get("dividendYield")
        if dy is not None:
            return round(dy * 100, 2)
        return None
