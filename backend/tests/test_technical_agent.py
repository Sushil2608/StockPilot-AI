import os

import pytest
import numpy as np

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from app.agents.technical import TechnicalAgent


@pytest.fixture
def agent():
    return TechnicalAgent()


def test_safe_float_normal(agent: TechnicalAgent):
    assert agent._safe_float(42.5) == 42.5


def test_safe_float_nan(agent: TechnicalAgent):
    assert agent._safe_float(float("nan")) is None


def test_safe_float_none(agent: TechnicalAgent):
    assert agent._safe_float(None) is None


def test_safe_float_numpy_nan(agent: TechnicalAgent):
    assert agent._safe_float(np.nan) is None


def test_determine_trend_bullish(agent: TechnicalAgent):
    result = agent._determine_trend(
        price=150.0, sma_50=140.0, sma_200=120.0, rsi=55.0
    )
    assert result == "bullish"


def test_determine_trend_bearish(agent: TechnicalAgent):
    result = agent._determine_trend(
        price=100.0, sma_50=120.0, sma_200=130.0, rsi=75.0
    )
    assert result == "bearish"


def test_determine_trend_neutral_missing_data(agent: TechnicalAgent):
    result = agent._determine_trend(
        price=None, sma_50=None, sma_200=None, rsi=None
    )
    assert result == "neutral"
