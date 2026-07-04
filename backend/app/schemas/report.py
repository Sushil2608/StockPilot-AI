from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(default="", description="Full company name")
    steps: list[str] = Field(
        ...,
        description="Ordered list of research steps to execute",
    )


class InvestmentReport(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(default="", description="Full company name")
    summary: str = Field(..., description="Executive investment summary")
    strengths: list[str] = Field(
        default_factory=list,
        description="Key strengths and positive factors",
    )
    weaknesses: list[str] = Field(
        default_factory=list,
        description="Key weaknesses and concerns",
    )
    risks: list[str] = Field(
        default_factory=list,
        description="Risk factors to consider",
    )
    recommendation: str = Field(
        ...,
        description="Investment recommendation: Strong Buy, Buy, Hold, Sell, or Strong Sell",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score from 0.0 to 1.0",
    )
