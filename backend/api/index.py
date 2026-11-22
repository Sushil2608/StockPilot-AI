"""Expose the FastAPI application as a Vercel Python Function."""

from app.main import app

__all__ = ["app"]
