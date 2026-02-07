"""Utilities for constructing audience-appropriate narratives from data."""

from __future__ import annotations

from typing import Any


def translate_friction_to_impact(friction_data: list[dict[str, Any]]) -> str:
    """Convert friction scores into human-centred impact language.

    Example: friction_score 847 -> "developers waste ~6 months and $47,000 per project".
    """
    parts: list[str] = []
    for item in friction_data:
        score = item.get("friction_score", 0)
        topic = item.get("topic", "regulatory barriers")
        cost = item.get("estimated_cost")
        delay = item.get("delay_days")

        human = _score_to_human(score, topic, cost, delay)
        parts.append(human)
    return " ".join(parts)


def build_executive_summary(
    top_issues: list[dict[str, Any]],
    jurisdiction: str,
    total_cost: float | None = None,
) -> str:
    """Produce a 3-4 sentence executive summary suitable for decision-makers."""
    issue_count = len(top_issues)
    topics = ", ".join(i.get("topic", "") for i in top_issues[:3])
    summary = (
        f"{jurisdiction} faces {issue_count} significant regulatory friction "
        f"areas, most critically in {topics}."
    )
    if total_cost:
        summary += f" Together, these add an estimated ${total_cost:,.0f} in costs per project."
    summary += (
        " Addressing these barriers through targeted policy reforms can reduce "
        "development timelines and lower housing costs for residents."
    )
    return summary


def format_for_audience(text: str, audience: str) -> str:
    """Apply light audience-specific adjustments to narrative text."""
    if audience in ("City_Council", "State_Legislature"):
        # Slightly more formal register.
        text = text.replace("you should", "the Council may wish to")
        text = text.replace("we recommend", "staff recommends")
    elif audience == "General_Public":
        text = text.replace("regulatory friction", "red tape")
        text = text.replace("entitlement process", "permit process")
    return text


def _score_to_human(
    score: int, topic: str, cost: float | None, delay: int | None
) -> str:
    severity = "significant" if score > 600 else "moderate" if score > 300 else "minor"
    parts = [f"{topic.replace('_', ' ')} represents a {severity} barrier"]
    if cost:
        parts.append(f"costing an estimated ${cost:,.0f}")
    if delay:
        months = round(delay / 30, 1)
        parts.append(f"adding roughly {months} months of delay")
    return ", ".join(parts) + "."
