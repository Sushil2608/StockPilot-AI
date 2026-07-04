import os

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "StockPilot AI"
    assert "version" in data


@pytest.mark.anyio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.anyio
async def test_analyze_invalid_ticker(client: AsyncClient):
    response = await client.post("/analyze", json={"ticker": ""})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_analyze_missing_body(client: AsyncClient):
    response = await client.post("/analyze")
    assert response.status_code == 422
