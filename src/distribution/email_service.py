"""Email distribution service using SendGrid."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.config import settings
from src.integrations.distribution_channels import DistributionResult

logger = logging.getLogger(__name__)


class EmailService:
    """Send transactional and digest emails via SendGrid."""

    def __init__(self) -> None:
        self.api_key = settings.sendgrid_api_key
        self.from_email = settings.sendgrid_from_email
        self.base_url = "https://api.sendgrid.com/v3"

    async def send(self, content: dict[str, Any]) -> DistributionResult:
        """Send an email with the content payload.

        *content* should include ``to_emails`` (list[str]), ``subject``
        (str), and ``html_body`` (str).
        """
        to_emails: list[str] = content.get("to_emails", [])
        subject: str = content.get("subject", content.get("headline", "HousingSpeak Alert"))
        html_body: str = content.get("html_body", content.get("body", ""))

        if not to_emails:
            return DistributionResult(channel="email", success=False, error="No recipients")

        payload = {
            "personalizations": [{"to": [{"email": e} for e in to_emails]}],
            "from": {"email": self.from_email, "name": "HousingSpeak"},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_body}],
        }

        if not self.api_key:
            logger.warning("SendGrid API key not configured; email not sent.")
            return DistributionResult(
                channel="email", success=False, error="API key not configured"
            )

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.base_url}/mail/send",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                )
                resp.raise_for_status()
                msg_id = resp.headers.get("X-Message-Id", "")
                return DistributionResult(channel="email", success=True, message_id=msg_id)
        except httpx.HTTPStatusError as exc:
            logger.error("SendGrid error: %s", exc.response.text)
            return DistributionResult(
                channel="email", success=False, error=str(exc)
            )
