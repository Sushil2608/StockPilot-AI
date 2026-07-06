import logging

import numpy as np
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange

from app.schemas import TechnicalIndicators, PricePoint

logger = logging.getLogger(__name__)

MINIMUM_DATA_POINTS = 200
PRICE_HISTORY_DAYS = 30


class TechnicalAgent:
    async def run(self, ticker: str) -> TechnicalIndicators:
        logger.info("Technical agent starting for ticker=%s", ticker)
        df = await self._fetch_history(ticker)

        if df.empty or len(df) < MINIMUM_DATA_POINTS:
            logger.warning(
                "Insufficient data for ticker=%s (rows=%d)", ticker, len(df)
            )
            return TechnicalIndicators(ticker=ticker)

        close = df["Close"]
        high = df["High"]
        low = df["Low"]
        volume = df["Volume"]
        current_price = self._safe_float(close.iloc[-1])

        rsi_value = self._calculate_rsi(close)
        macd_line, macd_signal, macd_hist = self._calculate_macd(close)
        sma_50 = self._calculate_sma(close, 50)
        sma_200 = self._calculate_sma(close, 200)
        ema_20 = self._calculate_ema(close, 20)
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger(close)
        atr = self._calculate_atr(high, low, close)
        vol_current, vol_avg = self._calculate_volume(volume)

        score, breakdown = self._compute_technical_score(
            current_price, rsi_value, macd_line, macd_signal, macd_hist,
            sma_50, sma_200, bb_upper, bb_lower, vol_current, vol_avg,
        )

        trend = self._score_to_trend(score)
        price_history = self._extract_price_history(df)

        result = TechnicalIndicators(
            ticker=ticker,
            current_price=current_price,
            rsi=rsi_value,
            macd=macd_line,
            macd_signal=macd_signal,
            macd_histogram=macd_hist,
            sma_50=sma_50,
            sma_200=sma_200,
            ema_20=ema_20,
            bollinger_upper=bb_upper,
            bollinger_middle=bb_middle,
            bollinger_lower=bb_lower,
            atr=atr,
            volume_current=vol_current,
            volume_avg=vol_avg,
            trend=trend,
            technical_score=score,
            score_breakdown=breakdown,
            price_history=price_history,
        )
        logger.info("Technical agent completed: score=%d trend=%s", score, trend)
        return result

    def _compute_technical_score(
        self,
        price: float | None,
        rsi: float | None,
        macd: float | None,
        macd_signal: float | None,
        macd_hist: float | None,
        sma_50: float | None,
        sma_200: float | None,
        bb_upper: float | None,
        bb_lower: float | None,
        vol_current: float | None,
        vol_avg: float | None,
    ) -> tuple[int, dict[str, int]]:
        breakdown: dict[str, int] = {}

        # RSI component (0-25): oversold is bullish, overbought is bearish
        rsi_score = 12
        if rsi is not None:
            if rsi < 20:
                rsi_score = 25
            elif rsi < 30:
                rsi_score = 20
            elif rsi < 45:
                rsi_score = 16
            elif rsi <= 55:
                rsi_score = 12
            elif rsi <= 70:
                rsi_score = 8
            elif rsi <= 80:
                rsi_score = 4
            else:
                rsi_score = 0
        breakdown["rsi"] = rsi_score

        # MACD component (0-25)
        macd_score = 12
        if macd is not None and macd_signal is not None:
            if macd > macd_signal and macd > 0:
                macd_score = 25
            elif macd > macd_signal:
                macd_score = 20
            elif macd > 0 and macd <= macd_signal:
                macd_score = 10
            elif macd <= macd_signal and macd <= 0:
                macd_score = 4
            else:
                macd_score = 8
            if macd_hist is not None:
                if macd_hist > 0 and macd > macd_signal:
                    macd_score = min(25, macd_score + 3)
                elif macd_hist < 0 and macd < macd_signal:
                    macd_score = max(0, macd_score - 3)
        breakdown["macd"] = macd_score

        # Moving average component (0-25)
        ma_score = 12
        if price is not None and sma_50 is not None and sma_200 is not None:
            if price > sma_50 > sma_200:
                ma_score = 25
            elif price > sma_50 and sma_50 <= sma_200:
                ma_score = 16
            elif price <= sma_50 and sma_50 > sma_200:
                ma_score = 10
            elif price <= sma_50 <= sma_200:
                ma_score = 0
            else:
                ma_score = 8
        breakdown["moving_avg"] = ma_score

        # Bollinger Bands component (0-15)
        bb_score = 7
        if price is not None and bb_upper is not None and bb_lower is not None:
            bb_range = bb_upper - bb_lower
            if bb_range > 0:
                position = (price - bb_lower) / bb_range
                if position < 0.0:
                    bb_score = 15
                elif position < 0.2:
                    bb_score = 12
                elif position < 0.4:
                    bb_score = 9
                elif position <= 0.6:
                    bb_score = 7
                elif position <= 0.8:
                    bb_score = 4
                elif position <= 1.0:
                    bb_score = 2
                else:
                    bb_score = 0
        breakdown["bollinger"] = bb_score

        # Volume confirmation (0-10)
        vol_score = 5
        if vol_current is not None and vol_avg is not None and vol_avg > 0:
            ratio = vol_current / vol_avg
            if ratio > 1.5:
                vol_score = 10
            elif ratio > 1.2:
                vol_score = 8
            elif ratio >= 0.8:
                vol_score = 5
            elif ratio >= 0.5:
                vol_score = 3
            else:
                vol_score = 1
        breakdown["volume"] = vol_score

        total = sum(breakdown.values())
        return max(0, min(100, total)), breakdown

    def _score_to_trend(self, score: int) -> str:
        if score >= 65:
            return "bullish"
        elif score <= 35:
            return "bearish"
        return "neutral"

    async def _fetch_history(self, ticker: str) -> pd.DataFrame:
        stock = yf.Ticker(ticker)
        return stock.history(period="1y")

    def _safe_float(self, value: object) -> float | None:
        try:
            f = float(value)
            return None if np.isnan(f) else round(f, 2)
        except (TypeError, ValueError):
            return None

    def _last_value(self, series: pd.Series) -> float | None:
        values = series.dropna()
        return self._safe_float(values.iloc[-1]) if not values.empty else None

    def _calculate_rsi(self, close: pd.Series) -> float | None:
        return self._last_value(RSIIndicator(close=close, window=14).rsi())

    def _calculate_macd(
        self, close: pd.Series
    ) -> tuple[float | None, float | None, float | None]:
        indicator = MACD(close=close)
        return (
            self._last_value(indicator.macd()),
            self._last_value(indicator.macd_signal()),
            self._last_value(indicator.macd_diff()),
        )

    def _calculate_sma(self, close: pd.Series, window: int) -> float | None:
        return self._last_value(
            SMAIndicator(close=close, window=window).sma_indicator()
        )

    def _calculate_ema(self, close: pd.Series, window: int) -> float | None:
        return self._last_value(
            EMAIndicator(close=close, window=window).ema_indicator()
        )

    def _calculate_bollinger(
        self, close: pd.Series
    ) -> tuple[float | None, float | None, float | None]:
        indicator = BollingerBands(close=close, window=20, window_dev=2)
        return (
            self._last_value(indicator.bollinger_hband()),
            self._last_value(indicator.bollinger_mavg()),
            self._last_value(indicator.bollinger_lband()),
        )

    def _calculate_atr(
        self, high: pd.Series, low: pd.Series, close: pd.Series
    ) -> float | None:
        return self._last_value(
            AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range()
        )

    def _calculate_volume(
        self, volume: pd.Series
    ) -> tuple[float | None, float | None]:
        current = self._safe_float(volume.iloc[-1])
        avg = self._safe_float(volume.tail(20).mean())
        return current, avg

    def _extract_price_history(self, df: pd.DataFrame) -> list[PricePoint]:
        recent = df.tail(PRICE_HISTORY_DAYS)
        return self._dataframe_to_points(recent)

    @staticmethod
    def _dataframe_to_points(df: pd.DataFrame) -> list[PricePoint]:
        points: list[PricePoint] = []
        for idx, row in df.iterrows():
            points.append(PricePoint(
                date=idx.strftime("%Y-%m-%d"),
                open=round(float(row["Open"]), 2),
                high=round(float(row["High"]), 2),
                low=round(float(row["Low"]), 2),
                close=round(float(row["Close"]), 2),
                volume=round(float(row.get("Volume", 0))),
            ))
        return points
