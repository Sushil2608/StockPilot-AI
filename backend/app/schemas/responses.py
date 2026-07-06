from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.financial import FinancialData
from app.schemas.news import NewsAnalysis
from app.schemas.report import InvestmentReport, ResearchPlan
from app.schemas.technical import TechnicalIndicators


class AgentStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class AgentStatus(BaseModel):
    agent: str = Field(..., description="Agent name")
    status: AgentStatusEnum = Field(..., description="Current agent status")
    message: str = Field(default="", description="Status message or error detail")


class AnalysisResponse(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    market: str = Field(default="US", description="Market: US or IN")
    currency: str = Field(default="USD", description="Currency code")
    planner: ResearchPlan | None = Field(None, description="Research plan output")
    financial: FinancialData | None = Field(None, description="Financial data output")
    news: NewsAnalysis | None = Field(None, description="News analysis output")
    technical: TechnicalIndicators | None = Field(
        None, description="Technical indicators output"
    )
    report: InvestmentReport | None = Field(
        None, description="Final investment report"
    )
