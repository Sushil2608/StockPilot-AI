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
    assert agent._compute_roe(info) == 0.18
