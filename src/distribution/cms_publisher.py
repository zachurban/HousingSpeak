"""CMS publisher — push content to WordPress or headless CMS."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.config import settings
from src.integrations.distribution_channels import DistributionResult

logger = logging.getLogger(__name__)


class CMSPublisher:
    """Publish blog posts and pages to a WordPress REST API."""

    def __init__(self) -> None:
        self.api_url = settings.cms_api_url
        self.username = settings.cms_username
        self.password = settings.cms_password

    async def publish(self, content: dict[str, Any]) -> DistributionResult:
        """Create a new post on the CMS.

        *content* should include ``headline`` (str), ``body`` (str), and
        optionally ``seo_keywords`` (list[str]).
        """
        if not self.api_url:
            logger.warning("CMS API URL not configured; publish skipped.")
            return DistributionResult(
                channel="blog", success=False, error="CMS not configured"
            )

        payload = {
            "title": content.get("headline", "Untitled"),
            "content": content.get("body", ""),
            "status": "draft",
            "tags": content.get("seo_keywords", []),
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.api_url}/posts",
                    json=payload,
                    auth=(self.username, self.password),
                )
                resp.raise_for_status()
                post_id = resp.json().get("id")
                return DistributionResult(
                    channel="blog",
                    success=True,
                    message_id=str(post_id),
                    metadata={"cms_url": f"{self.api_url}/posts/{post_id}"},
                )
        except httpx.HTTPStatusError as exc:
            logger.error("CMS publish error: %s", exc.response.text)
            return DistributionResult(channel="blog", success=False, error=str(exc))
