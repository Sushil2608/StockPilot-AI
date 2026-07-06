import os

import pytest

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from app.agents.financial import FinancialAgent


@pytest.fixture
def agent():
    return FinancialAgent()


def test_compute_roe_from_values(agent: FinancialAgent):
    info = {"netIncomeToCommon": 50_000_000, "totalStockholderEquity": 200_000_000}
    assert agent._compute_roe(info) == 25.0


def test_compute_roe_zero_equity(agent: FinancialAgent):
    info = {"netIncomeToCommon": 50_000_000, "totalStockholderEquity": 0}
    assert agent._compute_roe(info) is None


def test_compute_roe_missing_fields(agent: FinancialAgent):
    assert agent._compute_roe({}) is None


def test_compute_roe_fallback_to_api_field(agent: FinancialAgent):
    info = {"returnOnEquity": 0.18}
    assert agent._compute_roe(info) == 18.0


def test_compute_profit_margin_from_api(agent: FinancialAgent):
    info = {"profitMargins": 0.25}
    assert agent._compute_profit_margin(info) == 25.0


def test_compute_profit_margin_calculated(agent: FinancialAgent):
    info = {"totalRevenue": 1_000_000, "netIncomeToCommon": 200_000}
    assert agent._compute_profit_margin(info) == 20.0


def test_compute_debt_to_equity(agent: FinancialAgent):
    info = {"totalDebt": 500_000, "totalStockholderEquity": 1_000_000}
    assert agent._compute_debt_to_equity(info) == 0.5


def test_compute_dividend_yield(agent: FinancialAgent):
    info = {"dividendYield": 0.032}
    assert agent._compute_dividend_yield(info) == 3.2


def test_compute_dividend_yield_none(agent: FinancialAgent):
    assert agent._compute_dividend_yield({}) is None
