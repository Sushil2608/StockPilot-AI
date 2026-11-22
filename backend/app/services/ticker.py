import asyncio
import logging

import yfinance as yf

logger = logging.getLogger(__name__)


class InvalidTickerError(Exception):
    def __init__(self, ticker: str) -> None:
        self.ticker = ticker
        super().__init__(f"Invalid or unknown ticker: {ticker}")


async def validate_ticker(ticker: str) -> dict:
    logger.info("Validating ticker=%s", ticker)
    info = await asyncio.to_thread(_load_ticker_info, ticker)

    if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
        raise InvalidTickerError(ticker)

    name = info.get("longName", info.get("shortName", ticker))
    logger.info("Ticker %s validated: %s", ticker, name)
    return info


def _load_ticker_info(ticker: str) -> dict:
    return yf.Ticker(ticker).info
