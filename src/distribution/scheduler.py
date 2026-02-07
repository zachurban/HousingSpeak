"""Celery-based task scheduler for automated content generation and distribution."""

from __future__ import annotations

import asyncio
import logging

from celery import Celery
from celery.schedules import crontab

from src.config import settings

logger = logging.getLogger(__name__)

app = Celery("housingspeak", broker=settings.redis_url, backend=settings.redis_url)

app.conf.beat_schedule = {
    "weekly-digest": {
        "task": "src.distribution.scheduler.generate_weekly_digest",
        "schedule": crontab(hour=9, minute=0, day_of_week="monday"),
    },
    "daily-alert-scan": {
        "task": "src.distribution.scheduler.scan_and_alert",
        "schedule": crontab(hour=7, minute=0),
    },
}
app.conf.timezone = "US/Mountain"


def _run_async(coro):  # type: ignore[no-untyped-def]
    """Run an async coroutine inside a Celery sync task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.task(name="src.distribution.scheduler.generate_weekly_digest")
def generate_weekly_digest() -> None:
    """Generate and send weekly digest emails to all stakeholders."""
    from src.generators.stakeholder_report import StakeholderReportGenerator

    async def _run() -> None:
        generator = StakeholderReportGenerator()
        # In production, fetch stakeholders from the database.
        logger.info("Weekly digest generation started.")
        # Placeholder: iterate stakeholders and generate/send reports.
        _ = generator  # ensure import is used
        logger.info("Weekly digest generation completed.")

    _run_async(_run())


@app.task(name="src.distribution.scheduler.scan_and_alert")
def scan_and_alert() -> None:
    """Scan for new policy changes and generate stakeholder alerts."""
    from src.generators.alerts import AlertGenerator

    async def _run() -> None:
        generator = AlertGenerator()
        logger.info("Daily alert scan started.")
        # Placeholder: fetch stakeholders from DB and generate alerts.
        _ = generator
        logger.info("Daily alert scan completed.")

    _run_async(_run())


@app.task(name="src.distribution.scheduler.generate_content")
def generate_content_task(content_type: str, jurisdiction: str, audience: str) -> dict:
    """On-demand content generation task."""
    from src.generators.policy_brief import PolicyBriefGenerator
    from src.generators.public_content import PublicContentGenerator

    async def _run() -> dict:
        if content_type in ("Policy_Brief", "policy_brief"):
            from src.models.content import AudienceType

            gen = PolicyBriefGenerator()
            return await gen.generate(
                jurisdiction=jurisdiction, audience=AudienceType(audience)
            )
        else:
            gen_pub = PublicContentGenerator()
            return await gen_pub.generate(
                jurisdiction=jurisdiction, content_type=content_type
            )

    return _run_async(_run())
