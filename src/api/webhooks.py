"""Webhook handlers for incoming events from HousingLens and HousingEar."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Request

from src.generators.alerts import AlertGenerator

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/housing-lens")
async def housing_lens_webhook(request: Request) -> dict[str, str]:
    """Receive push notifications from HousingLens (friction score changes, new trends)."""
    payload: dict[str, Any] = await request.json()
    event_type = payload.get("event_type", "unknown")
    logger.info("HousingLens webhook received: %s", event_type)

    if event_type == "friction_score_change":
        # Trigger alert generation for affected stakeholders.
        generator = AlertGenerator()
        affected_jurisdiction = payload.get("jurisdiction", "")
        # In production, look up stakeholders by jurisdiction and generate alerts.
        _ = generator, affected_jurisdiction

    return {"status": "received", "event_type": event_type}


@router.post("/housing-ear")
async def housing_ear_webhook(request: Request) -> dict[str, str]:
    """Receive push notifications from HousingEar (policy updates, meeting agendas)."""
    payload: dict[str, Any] = await request.json()
    event_type = payload.get("event_type", "unknown")
    logger.info("HousingEar webhook received: %s", event_type)

    if event_type in ("federal_register_change", "meeting_agenda", "policy_update"):
        generator = AlertGenerator()
        _ = generator

    return {"status": "received", "event_type": event_type}
