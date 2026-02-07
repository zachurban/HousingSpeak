"""Tests for FastAPI endpoints (health + basic validation)."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.endpoints import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_stakeholder() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/stakeholders",
            json={
                "stakeholder_type": "PHA_Executive_Director",
                "organization": "Test PHA",
                "jurisdiction": "Denver, CO",
            },
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["organization"] == "Test PHA"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_stakeholder_not_found() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/stakeholders/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_campaign() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/campaigns",
            json={
                "name": "Test Campaign",
                "jurisdiction": "Denver, CO",
                "target_audience": ["City_Council"],
            },
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Campaign"
    assert data["status"] == "planning"
