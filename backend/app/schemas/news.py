from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    title: str = Field(..., description="News article headline")
    source: str = Field(..., description="News source or publisher")
    url: str = Field(default="", description="Link to the article")
    published: str = Field(default="", description="Publication date")


class NewsAnalysis(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    positive_developments: list[str] = Field(
        default_factory=list,
        description="List of positive news developments",
    )
    negative_developments: list[str] = Field(
        default_factory=list,
        description="List of negative news developments",
    )
    overall_sentiment: str = Field(
        ...,
        description="Overall sentiment: bullish, bearish, or neutral",
    )
    evidence: list[NewsItem] = Field(
        default_factory=list,
        description="Source articles used for analysis",
    )
