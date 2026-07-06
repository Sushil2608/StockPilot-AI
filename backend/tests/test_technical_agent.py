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


def test_score_bullish(agent: TechnicalAgent):
    score, breakdown = agent._compute_technical_score(
        price=150.0, rsi=40.0,
        macd=1.5, macd_signal=0.5, macd_hist=1.0,
        sma_50=140.0, sma_200=120.0,
        bb_upper=160.0, bb_lower=130.0,
        vol_current=2_000_000, vol_avg=1_000_000,
    )
    assert score >= 65
    assert agent._score_to_trend(score) == "bullish"


def test_score_bearish(agent: TechnicalAgent):
    score, breakdown = agent._compute_technical_score(
        price=100.0, rsi=78.0,
        macd=-0.5, macd_signal=0.5, macd_hist=-1.0,
        sma_50=120.0, sma_200=130.0,
        bb_upper=115.0, bb_lower=95.0,
        vol_current=500_000, vol_avg=1_000_000,
    )
    assert score <= 35
    assert agent._score_to_trend(score) == "bearish"


def test_score_neutral_missing_data(agent: TechnicalAgent):
    score, breakdown = agent._compute_technical_score(
        price=None, rsi=None,
        macd=None, macd_signal=None, macd_hist=None,
        sma_50=None, sma_200=None,
        bb_upper=None, bb_lower=None,
        vol_current=None, vol_avg=None,
    )
    assert 35 < score < 65
    assert agent._score_to_trend(score) == "neutral"


def test_score_breakdown_has_all_components(agent: TechnicalAgent):
    _, breakdown = agent._compute_technical_score(
        price=150.0, rsi=50.0,
        macd=0.5, macd_signal=0.3, macd_hist=0.2,
        sma_50=145.0, sma_200=130.0,
        bb_upper=160.0, bb_lower=140.0,
        vol_current=1_000_000, vol_avg=1_000_000,
    )
    assert set(breakdown.keys()) == {"rsi", "macd", "moving_avg", "bollinger", "volume"}
    assert all(0 <= v <= 25 for k, v in breakdown.items() if k != "volume")
    assert 0 <= breakdown["volume"] <= 10


def test_score_to_trend(agent: TechnicalAgent):
    assert agent._score_to_trend(80) == "bullish"
    assert agent._score_to_trend(50) == "neutral"
    assert agent._score_to_trend(20) == "bearish"
