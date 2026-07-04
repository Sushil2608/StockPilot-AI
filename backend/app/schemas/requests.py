from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    ticker: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Stock ticker symbol (e.g., NVDA, AAPL, MSFT)",
        examples=["NVDA", "AAPL", "MSFT"],
    )
