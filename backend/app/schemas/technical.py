from pydantic import BaseModel, Field


class TechnicalIndicators(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    current_price: float | None = Field(None, description="Current stock price")
    rsi: float | None = Field(None, description="Relative Strength Index (14-period)")
    macd: float | None = Field(None, description="MACD line value")
    macd_signal: float | None = Field(None, description="MACD signal line value")
    macd_histogram: float | None = Field(None, description="MACD histogram value")
    sma_50: float | None = Field(None, description="50-day Simple Moving Average")
    sma_200: float | None = Field(None, description="200-day Simple Moving Average")
    trend: str = Field(
        default="neutral",
        description="Overall trend: bullish, bearish, or neutral",
    )
