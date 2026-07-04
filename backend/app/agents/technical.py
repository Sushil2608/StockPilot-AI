import logging

import numpy as np
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator

from app.schemas import TechnicalIndicators

logger = logging.getLogger(__name__)


class TechnicalAgent:
    async def run(self, ticker: str) -> TechnicalIndicators:
        logger.info("Technical agent starting for ticker=%s", ticker)
        df = await self._fetch_history(ticker)

        if df.empty or len(df) < 200:
            logger.warning(
                "Insufficient data for ticker=%s (rows=%d)", ticker, len(df)
            )
            return TechnicalIndicators(ticker=ticker)

        close = df["Close"]
        current_price = self._safe_float(close.iloc[-1])

        rsi_value = self._calculate_rsi(close)
        macd_line, macd_signal, macd_hist = self._calculate_macd(close)
        sma_50 = self._calculate_sma(close, 50)
        sma_200 = self._calculate_sma(close, 200)
        trend = self._determine_trend(current_price, sma_50, sma_200, rsi_value)

        result = TechnicalIndicators(
            ticker=ticker,
            current_price=current_price,
            rsi=rsi_value,
            macd=macd_line,
            macd_signal=macd_signal,
            macd_histogram=macd_hist,
            sma_50=sma_50,
            sma_200=sma_200,
            trend=trend,
        )
        logger.info("Technical agent completed: trend=%s", trend)
        return result

    async def _fetch_history(self, ticker: str) -> pd.DataFrame:
        stock = yf.Ticker(ticker)
        return stock.history(period="1y")

    def _safe_float(self, value: object) -> float | None:
        try:
            f = float(value)
            return None if np.isnan(f) else round(f, 2)
        except (TypeError, ValueError):
            return None

    def _calculate_rsi(self, close: pd.Series) -> float | None:
        indicator = RSIIndicator(close=close, window=14)
        values = indicator.rsi().dropna()
        return self._safe_float(values.iloc[-1]) if not values.empty else None

    def _calculate_macd(
        self, close: pd.Series
    ) -> tuple[float | None, float | None, float | None]:
        indicator = MACD(close=close)
        macd_line = indicator.macd().dropna()
        signal = indicator.macd_signal().dropna()
        hist = indicator.macd_diff().dropna()
        return (
            self._safe_float(macd_line.iloc[-1]) if not macd_line.empty else None,
            self._safe_float(signal.iloc[-1]) if not signal.empty else None,
            self._safe_float(hist.iloc[-1]) if not hist.empty else None,
        )

    def _calculate_sma(self, close: pd.Series, window: int) -> float | None:
        indicator = SMAIndicator(close=close, window=window)
        values = indicator.sma_indicator().dropna()
        return self._safe_float(values.iloc[-1]) if not values.empty else None

    def _determine_trend(
        self,
        price: float | None,
        sma_50: float | None,
        sma_200: float | None,
        rsi: float | None,
    ) -> str:
        if price is None or sma_50 is None or sma_200 is None:
            return "neutral"

        bullish_signals = 0
        bearish_signals = 0

        if price > sma_50:
            bullish_signals += 1
        else:
            bearish_signals += 1

        if sma_50 > sma_200:
            bullish_signals += 1
        else:
            bearish_signals += 1

        if rsi is not None:
            if rsi > 70:
                bearish_signals += 1
            elif rsi < 30:
                bullish_signals += 1

        if bullish_signals > bearish_signals:
            return "bullish"
        elif bearish_signals > bullish_signals:
            return "bearish"
        return "neutral"
