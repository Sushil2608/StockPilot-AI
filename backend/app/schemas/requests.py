from enum import Enum

from pydantic import BaseModel, Field


class Market(str, Enum):
    US = "US"
    INDIA = "IN"


class AnalysisRequest(BaseModel):
    ticker: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Stock ticker symbol",
        examples=["AAPL", "RELIANCE"],
    )
    market: Market = Field(
        default=Market.US,
        description="Stock market: US or IN (India/NSE)",
    )
