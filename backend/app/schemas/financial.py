from pydantic import BaseModel, Field


class FinancialData(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Full company name")
    revenue: float | None = Field(None, description="Total revenue in USD")
    market_cap: float | None = Field(None, description="Market capitalization in USD")
    pe_ratio: float | None = Field(None, description="Price-to-Earnings ratio")
    eps: float | None = Field(None, description="Earnings per share")
    cash: float | None = Field(None, description="Total cash and equivalents in USD")
    debt: float | None = Field(None, description="Total debt in USD")
    roe: float | None = Field(None, description="Return on equity as a percentage")
    fifty_two_week_high: float | None = Field(None, description="52-week high price")
    fifty_two_week_low: float | None = Field(None, description="52-week low price")
    current_price: float | None = Field(None, description="Current stock price")
