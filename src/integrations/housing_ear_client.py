"""Client for the HousingEar policy-monitoring API."""

from __future__ import annotations

from typing import Any

import httpx

from src.config import settings


class HousingEarClient:
    """Fetches Federal Register changes, meeting transcripts, and policy updates."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self.base_url = (base_url or settings.housing_ear_api_url).rstrip("/")
        self.api_key = api_key or settings.housing_ear_api_key
        self._headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.base_url}{path}", headers=self._headers, params=params
            )
            resp.raise_for_status()
            return resp.json()

    async def get_federal_register_changes(
        self,
        jurisdiction: str | None = None,
        topics: list[str] | None = None,
        since: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return recent Federal Register changes relevant to housing."""
        params: dict[str, Any] = {}
        if jurisdiction:
            params["jurisdiction"] = jurisdiction
        if topics:
            params["topics"] = ",".join(topics)
        if since:
            params["since"] = since
        data = await self._get("/api/v1/federal-register", params)
        return data.get("changes", [])

    async def get_meeting_transcripts(
        self, jurisdiction: str, since: str | None = None
    ) -> list[dict[str, Any]]:
        """Return meeting transcripts/agendas for a jurisdiction."""
        params: dict[str, Any] = {"jurisdiction": jurisdiction}
        if since:
            params["since"] = since
        data = await self._get("/api/v1/meetings", params)
        return data.get("transcripts", [])

    async def get_policy_updates(
        self, jurisdiction: str | None = None, since: str | None = None
    ) -> list[dict[str, Any]]:
        """Return policy updates and regulatory changes."""
        params: dict[str, Any] = {}
        if jurisdiction:
            params["jurisdiction"] = jurisdiction
        if since:
            params["since"] = since
        data = await self._get("/api/v1/policy-updates", params)
        return data.get("updates", [])
