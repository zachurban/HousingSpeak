"""Unified interface for content distribution channels."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DistributionResult:
    channel: str
    success: bool
    message_id: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class DistributionManager:
    """Coordinates content distribution across multiple channels."""

    def __init__(self) -> None:
        from src.distribution.cms_publisher import CMSPublisher
        from src.distribution.email_service import EmailService
        from src.distribution.social_media import SocialMediaPublisher

        self.email = EmailService()
        self.cms = CMSPublisher()
        self.social = SocialMediaPublisher()

    async def distribute(
        self,
        content: dict[str, Any],
        channels: list[str],
    ) -> list[DistributionResult]:
        """Distribute content to the specified channels and return results."""
        results: list[DistributionResult] = []

        for channel in channels:
            if channel == "email":
                result = await self.email.send(content)
            elif channel == "blog":
                result = await self.cms.publish(content)
            elif channel in ("twitter", "linkedin", "social_media"):
                result = await self.social.publish(content, platform=channel)
            else:
                result = DistributionResult(
                    channel=channel, success=False, error=f"Unknown channel: {channel}"
                )
            results.append(result)

        return results
