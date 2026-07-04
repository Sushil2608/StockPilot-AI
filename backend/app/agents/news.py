import logging

import yfinance as yf
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

from app.schemas import NewsAnalysis, NewsItem

logger = logging.getLogger(__name__)

NEWS_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a financial news analyst. "
        "Analyze the provided news articles for a given stock. "
        "Identify positive and negative developments, "
        "and determine the overall market sentiment.",
    ),
    (
        "human",
        "Analyze the following news articles for {ticker}:\n\n{news_text}\n\n"
        "Provide your analysis with positive developments, "
        "negative developments, and overall sentiment.",
    ),
])


def _extract_article(raw: dict) -> dict:
    content = raw.get("content", raw)
    provider = content.get("provider", {})
    canonical = content.get("canonicalUrl", {})
    return {
        "title": content.get("title", "No title"),
        "publisher": provider.get("displayName", "Unknown"),
        "url": canonical.get("url", ""),
        "published": content.get("pubDate", ""),
    }


class NewsAgent:
    def __init__(self, llm: ChatAnthropic) -> None:
        self.chain = NEWS_ANALYSIS_PROMPT | llm.with_structured_output(
            NewsAnalysis
        )

    async def run(self, ticker: str) -> NewsAnalysis:
        logger.info("News agent starting for ticker=%s", ticker)
        raw_articles = await self._fetch_news(ticker)
        articles = [_extract_article(a) for a in raw_articles[:10]]

        if not articles:
            logger.warning("No news articles found for ticker=%s", ticker)
            return NewsAnalysis(
                ticker=ticker,
                overall_sentiment="neutral",
                positive_developments=["No recent news available"],
                negative_developments=[],
                evidence=[],
            )

        news_text = self._format_articles(articles)
        evidence = [
            NewsItem(
                title=a["title"],
                source=a["publisher"],
                url=a["url"],
                published=a["published"],
            )
            for a in articles
        ]

        result = await self.chain.ainvoke({
            "ticker": ticker,
            "news_text": news_text,
        })
        result.ticker = ticker
        result.evidence = evidence
        logger.info(
            "News agent completed: sentiment=%s", result.overall_sentiment
        )
        return result

    async def _fetch_news(self, ticker: str) -> list[dict]:
        stock = yf.Ticker(ticker)
        return stock.news or []

    def _format_articles(self, articles: list[dict]) -> str:
        lines: list[str] = []
        for i, article in enumerate(articles, 1):
            lines.append(f"{i}. [{article['publisher']}] {article['title']}")
        return "\n".join(lines)
