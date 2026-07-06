from pydantic import BaseModel, Field


class PricePoint(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="High price")
    low: float = Field(..., description="Low price")
    close: float = Field(..., description="Closing price")
    volume: float = Field(default=0, description="Trading volume")


class PriceHistoryResponse(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    period: str = Field(..., description="Time period")
    currency: str = Field(default="USD", description="Currency code")
    data: list[PricePoint] = Field(default_factory=list)


class TechnicalIndicators(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    current_price: float | None = Field(None, description="Current stock price")

    rsi: float | None = Field(None, description="Relative Strength Index (14-period)")
    macd: float | None = Field(None, description="MACD line value")
    macd_signal: float | None = Field(None, description="MACD signal line value")
    macd_histogram: float | None = Field(None, description="MACD histogram value")
    sma_50: float | None = Field(None, description="50-day Simple Moving Average")
    sma_200: float | None = Field(None, description="200-day Simple Moving Average")
    ema_20: float | None = Field(None, description="20-day Exponential Moving Average")

    bollinger_upper: float | None = Field(None, description="Bollinger Band upper")
    bollinger_middle: float | None = Field(None, description="Bollinger Band middle (20-SMA)")
    bollinger_lower: float | None = Field(None, description="Bollinger Band lower")

    atr: float | None = Field(None, description="Average True Range (14-period)")
    volume_current: float | None = Field(None, description="Current trading volume")
    volume_avg: float | None = Field(None, description="20-day average volume")

    trend: str = Field(
        default="neutral",
        description="Overall trend: bullish, bearish, or neutral",
    )
    technical_score: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Composite technical score (0-100): 80+ Strong Buy, 60-79 Buy, 40-59 Neutral, 20-39 Sell, 0-19 Strong Sell",
    )
    score_breakdown: dict[str, int] = Field(
        default_factory=dict,
        description="Score contributions from each indicator group",
    )
    price_history: list[PricePoint] = Field(
        default_factory=list,
        description="Recent daily closing prices for charting",
    )
