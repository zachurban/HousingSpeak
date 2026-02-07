"""Policy brief generator — translates friction data into reform recommendations."""

from __future__ import annotations

import uuid
from typing import Any

from src.integrations.claude_api import ClaudeContentGenerator
from src.integrations.housing_lens_client import HousingLensClient
from src.models.content import AudienceType, ContentType


class PolicyBriefGenerator:
    """Generate policy reform recommendations grounded in friction scores."""

    def __init__(self) -> None:
        self.llm = ClaudeContentGenerator()
        self.lens = HousingLensClient()

    async def generate(
        self,
        jurisdiction: str,
        audience: AudienceType,
        friction_data: list[dict[str, Any]] | None = None,
        topics: list[str] | None = None,
        additional_context: str | None = None,
    ) -> dict[str, Any]:
        """Produce a complete policy brief dict ready for persistence.

        If *friction_data* is not supplied the generator fetches it from
        HousingLens for the given *jurisdiction* and *topics*.
        """
        if not friction_data:
            friction_data = await self.lens.get_friction_scores(jurisdiction, topics)

        # Rank by friction score descending and keep the top 5 issues.
        top_issues = sorted(
            friction_data, key=lambda d: d.get("friction_score", 0), reverse=True
        )[:5]

        # Fetch cost estimates to enrich the brief.
        cost_data = await self.lens.get_cost_estimates(
            jurisdiction, [i.get("topic", "") for i in top_issues]
        )

        # Build the LLM prompt payload combining friction + cost data.
        enriched_data = _merge_cost_data(top_issues, cost_data)

        raw_text = await self.llm.generate_policy_brief(
            friction_data=enriched_data,
            jurisdiction=jurisdiction,
            audience=audience.value,
        )

        return {
            "id": str(uuid.uuid4()),
            "content_type": ContentType.POLICY_BRIEF.value,
            "audience": audience.value,
            "jurisdiction": jurisdiction,
            "headline": _extract_headline(raw_text),
            "executive_summary": _extract_section(raw_text, "Executive Summary"),
            "body": raw_text,
            "call_to_action": _extract_section(raw_text, "Implementation Roadmap"),
            "source_data": {
                "friction_scores": [i.get("friction_score") for i in top_issues],
                "topics": [i.get("topic", "") for i in top_issues],
                "cost_estimates": cost_data,
            },
            "generated_by": "policy_brief_generator_v1",
            "status": "draft",
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _merge_cost_data(
    issues: list[dict[str, Any]], costs: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    cost_by_topic = {c.get("topic"): c for c in costs}
    merged = []
    for issue in issues:
        entry = dict(issue)
        cost_info = cost_by_topic.get(issue.get("topic"))
        if cost_info:
            entry["estimated_cost"] = cost_info.get("estimated_cost")
            entry["cost_detail"] = cost_info.get("detail")
        merged.append(entry)
    return merged


def _extract_headline(text: str) -> str:
    """Return the first non-empty line as the headline."""
    for line in text.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped[:500]
    return "Policy Brief"


def _extract_section(text: str, section_name: str) -> str | None:
    """Naively extract content under a markdown heading matching *section_name*."""
    lines = text.splitlines()
    capturing = False
    captured: list[str] = []
    for line in lines:
        heading = line.strip().lstrip("#").strip()
        if heading.lower().startswith(section_name.lower()):
            capturing = True
            continue
        if capturing:
            if line.strip().startswith("#"):
                break
            captured.append(line)
    return "\n".join(captured).strip() or None
