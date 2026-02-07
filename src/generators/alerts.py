"""Stakeholder alert generator — personalized notifications based on profile interests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from src.integrations.claude_api import ClaudeContentGenerator
from src.integrations.housing_ear_client import HousingEarClient
from src.integrations.housing_lens_client import HousingLensClient
from src.models.alert import AlertPriority, AlertType


class AlertGenerator:
    """Generate personalized alerts based on stakeholder interests and projects."""

    def __init__(self) -> None:
        self.llm = ClaudeContentGenerator()
        self.ear = HousingEarClient()
        self.lens = HousingLensClient()

    async def generate_alerts(
        self,
        stakeholder_profiles: list[dict[str, Any]],
        since: str | None = None,
    ) -> list[dict[str, Any]]:
        """Scan for changes and produce per-stakeholder alerts."""
        alerts: list[dict[str, Any]] = []

        for stakeholder in stakeholder_profiles:
            jurisdiction = stakeholder.get("jurisdiction", "")
            interests = stakeholder.get("interests", [])

            # Gather change data from HousingEar + HousingLens.
            fed_changes = await self.ear.get_federal_register_changes(
                jurisdiction=jurisdiction, topics=interests, since=since
            )
            policy_updates = await self.ear.get_policy_updates(
                jurisdiction=jurisdiction, since=since
            )
            trend_alerts = await self.lens.get_trend_alerts(
                jurisdiction=jurisdiction, since=since
            )

            # Skip if nothing new.
            if not fed_changes and not policy_updates and not trend_alerts:
                continue

            # Determine priority and type from the changes.
            priority, alert_type = _classify(fed_changes, policy_updates, trend_alerts)

            # Use Claude to draft a human-friendly summary.
            all_changes = fed_changes + policy_updates + trend_alerts
            summary_text = await self.llm.generate_alert_summary(
                changes=all_changes,
                stakeholder_context=stakeholder,
            )

            alert = {
                "id": str(uuid.uuid4()),
                "stakeholder_id": stakeholder.get("id"),
                "priority": priority.value,
                "alert_type": alert_type.value,
                "headline": _build_headline(all_changes, jurisdiction),
                "summary": summary_text,
                "action_required": priority in (AlertPriority.URGENT, AlertPriority.HIGH),
                "action_deadline": _infer_deadline(fed_changes),
                "related_project_ids": [
                    p.get("project_id", "") for p in stakeholder.get("projects", [])
                ],
                "recommended_actions": _recommend_actions(priority, alert_type),
                "source_data": {
                    "federal_changes": fed_changes,
                    "policy_updates": policy_updates,
                    "trend_alerts": trend_alerts,
                },
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            alerts.append(alert)

        return alerts


def _classify(
    fed: list[dict[str, Any]],
    policy: list[dict[str, Any]],
    trends: list[dict[str, Any]],
) -> tuple[AlertPriority, AlertType]:
    if fed:
        return AlertPriority.HIGH, AlertType.FEDERAL_REGISTER_CHANGE
    if policy:
        return AlertPriority.MEDIUM, AlertType.POLICY_UPDATE
    return AlertPriority.LOW, AlertType.EMERGING_TREND


def _build_headline(changes: list[dict[str, Any]], jurisdiction: str) -> str:
    if changes:
        first_title = changes[0].get("title", "Policy Change")
        return f"{jurisdiction}: {first_title}"
    return f"{jurisdiction}: New updates available"


def _infer_deadline(fed_changes: list[dict[str, Any]]) -> str | None:
    for change in fed_changes:
        deadline = change.get("comment_deadline") or change.get("effective_date")
        if deadline:
            return deadline
    return None


def _recommend_actions(priority: AlertPriority, alert_type: AlertType) -> list[str]:
    actions: list[str] = []
    if priority in (AlertPriority.URGENT, AlertPriority.HIGH):
        actions.append("Review the change details immediately")
    if alert_type == AlertType.FEDERAL_REGISTER_CHANGE:
        actions.append("Consider submitting a public comment before the deadline")
        actions.append("Assess impact on current projects")
    elif alert_type == AlertType.POLICY_UPDATE:
        actions.append("Review updated requirements")
    elif alert_type == AlertType.EMERGING_TREND:
        actions.append("Monitor this trend in upcoming meetings")
    return actions
