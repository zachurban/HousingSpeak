"""Social media publisher — schedule posts via Buffer or direct APIs."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.config import settings
from src.integrations.distribution_channels import DistributionResult

logger = logging.getLogger(__name__)


class SocialMediaPublisher:
    """Publish or schedule social media posts through the Buffer API."""

    def __init__(self) -> None:
        self.api_key = settings.buffer_api_key
        self.base_url = "https://api.bufferapp.com/1"

    async def publish(
        self, content: dict[str, Any], platform: str = "twitter"
    ) -> DistributionResult:
        """Schedule a social media post.

        *content* should include ``body`` (str) and optionally
        ``scheduled_date`` (ISO 8601 string).
        """
        text = content.get("body", "")
        # Truncate for Twitter if needed.
        if platform == "twitter" and len(text) > 280:
            text = text[:277] + "..."

        if not self.api_key:
            logger.warning("Buffer API key not configured; post not scheduled.")
            return DistributionResult(
                channel=platform, success=False, error="API key not configured"
            )

        payload: dict[str, Any] = {
            "text": text,
            "profile_ids": content.get("profile_ids", []),
            "shorten": True,
        }
        scheduled = content.get("scheduled_date")
        if scheduled:
            payload["scheduled_at"] = scheduled

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.base_url}/updates/create.json",
                    data=payload,
                    params={"access_token": self.api_key},
                )
                resp.raise_for_status()
                update_id = resp.json().get("updates", [{}])[0].get("id", "")
                return DistributionResult(
                    channel=platform, success=True, message_id=update_id
                )
        except httpx.HTTPStatusError as exc:
            logger.error("Buffer error: %s", exc.response.text)
            return DistributionResult(channel=platform, success=False, error=str(exc))
