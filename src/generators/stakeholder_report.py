"""Stakeholder report generator — customized reports per stakeholder profile."""

from __future__ import annotations

import uuid
from typing import Any

from src.integrations.claude_api import ClaudeContentGenerator
from src.integrations.housing_lens_client import HousingLensClient
from src.models.content import AudienceType, ContentType


class StakeholderReportGenerator:
    """Produce tailored reports for individual stakeholder profiles."""

    def __init__(self) -> None:
        self.llm = ClaudeContentGenerator()
        self.lens = HousingLensClient()

    async def generate(
        self,
        stakeholder: dict[str, Any],
        friction_data: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Build a stakeholder-specific report.

        Parameters
        ----------
        stakeholder:
            Dict representation of a Stakeholder profile (must include
            ``jurisdiction``, ``interests``, ``projects``, and ``stakeholder_type``).
        friction_data:
            Optional pre-fetched friction data. If omitted, fetched from
            HousingLens.
        """
        jurisdiction = stakeholder["jurisdiction"]
        interests = stakeholder.get("interests", [])
        projects = stakeholder.get("projects", [])

        if not friction_data:
            friction_data = await self.lens.get_friction_scores(jurisdiction, interests)

        # Filter to stakeholder interests.
        relevant = [
            d for d in friction_data if d.get("topic") in interests
        ] or friction_data[:5]

        # Build a context-rich prompt for the LLM.
        audience = _map_stakeholder_type_to_audience(stakeholder.get("stakeholder_type", ""))
        prompt_context = (
            f"Stakeholder: {stakeholder.get('organization', 'N/A')}\n"
            f"Type: {stakeholder.get('stakeholder_type', 'N/A')}\n"
            f"Jurisdiction: {jurisdiction}\n"
            f"Interests: {', '.join(interests)}\n"
            f"Active projects: {len(projects)}\n"
        )

        raw_text = await self.llm.generate(
            system_prompt=(
                "You are a housing policy analyst creating a customized stakeholder "
                "report. Focus on the stakeholder's specific interests and active "
                "projects. Provide actionable insights and recommendations."
            ),
            user_prompt=(
                f"{prompt_context}\n"
                f"Friction data:\n{_format_items(relevant)}\n\n"
                "Generate a concise, data-driven stakeholder report."
            ),
        )

        return {
            "id": str(uuid.uuid4()),
            "content_type": ContentType.STAKEHOLDER_REPORT.value,
            "audience": audience.value,
            "jurisdiction": jurisdiction,
            "headline": f"Stakeholder Report — {stakeholder.get('organization', jurisdiction)}",
            "executive_summary": None,
            "body": raw_text,
            "source_data": {"friction_data": relevant, "stakeholder_interests": interests},
            "generated_by": "stakeholder_report_generator_v1",
            "status": "draft",
        }


def _map_stakeholder_type_to_audience(stype: str) -> AudienceType:
    mapping = {
        "PHA_Executive_Director": AudienceType.PHA_BOARD,
        "City_Council": AudienceType.CITY_COUNCIL,
        "Developer": AudienceType.DEVELOPERS,
        "HUD_Regional_Office": AudienceType.HUD_OFFICIALS,
        "State_Agency": AudienceType.STATE_LEGISLATURE,
    }
    return mapping.get(stype, AudienceType.GENERAL_PUBLIC)


def _format_items(items: list[dict[str, Any]]) -> str:
    lines = []
    for item in items:
        lines.append(
            f"- {item.get('topic', 'N/A')}: score={item.get('friction_score', 'N/A')}"
        )
    return "\n".join(lines) or "No data."
