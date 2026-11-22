from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Market(str, Enum):
    US = "US"
    INDIA = "IN"


class AnalysisRequest(BaseModel):
    ticker: str = Field(
        ...,
        min_length=1,
        max_length=15,
        pattern=r"^[A-Z0-9][A-Z0-9.&-]*$",
        description="Stock ticker symbol",
        examples=["AAPL", "RELIANCE"],
    )
    market: Market = Field(
        default=Market.US,
        description="Stock market: US or IN (India/NSE)",
    )

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value
