"""Client for the HousingLens friction-scoring API."""

from __future__ import annotations

from typing import Any

import httpx

from src.config import settings


class HousingLensClient:
    """Fetches friction scores, trend alerts, cost estimates, and query patterns."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self.base_url = (base_url or settings.housing_lens_api_url).rstrip("/")
        self.api_key = api_key or settings.housing_lens_api_key
        self._headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.base_url}{path}", headers=self._headers, params=params
            )
            resp.raise_for_status()
            return resp.json()

    async def get_friction_scores(
        self, jurisdiction: str, topics: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Return friction scores for a jurisdiction, optionally filtered by topic."""
        params: dict[str, Any] = {"jurisdiction": jurisdiction}
        if topics:
            params["topics"] = ",".join(topics)
        data = await self._get("/api/v1/friction-scores", params)
        return data.get("scores", [])

    async def get_trend_alerts(
        self, jurisdiction: str | None = None, since: str | None = None
    ) -> list[dict[str, Any]]:
        """Return emerging trend alerts."""
        params: dict[str, Any] = {}
        if jurisdiction:
            params["jurisdiction"] = jurisdiction
        if since:
            params["since"] = since
        data = await self._get("/api/v1/trends", params)
        return data.get("alerts", [])

    async def get_cost_estimates(
        self, jurisdiction: str, topics: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Return cost-impact estimates for friction areas."""
        params: dict[str, Any] = {"jurisdiction": jurisdiction}
        if topics:
            params["topics"] = ",".join(topics)
        data = await self._get("/api/v1/cost-estimates", params)
        return data.get("estimates", [])

    async def get_query_patterns(self, jurisdiction: str) -> list[dict[str, Any]]:
        """Return commonly searched query patterns for a jurisdiction."""
        data = await self._get("/api/v1/query-patterns", {"jurisdiction": jurisdiction})
        return data.get("patterns", [])
