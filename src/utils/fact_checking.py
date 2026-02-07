"""Fact-checking utilities — verify generated claims against source data."""

from __future__ import annotations

import re
from typing import Any


class FactCheckResult:
    """Container for fact-check outcomes."""

    def __init__(self) -> None:
        self.verified: list[str] = []
        self.unverified: list[str] = []
        self.warnings: list[str] = []

    @property
    def passed(self) -> bool:
        return len(self.unverified) == 0

    def summary(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "verified_count": len(self.verified),
            "unverified_count": len(self.unverified),
            "warnings": self.warnings,
            "unverified_claims": self.unverified,
        }


def check_content(content: dict[str, Any]) -> FactCheckResult:
    """Run automated fact-checks on generated content.

    Verifies that:
    1. Dollar figures in the body are traceable to source_data cost estimates.
    2. Friction scores cited match source data.
    3. Jurisdiction names are consistent.
    """
    result = FactCheckResult()
    body = content.get("body", "")
    source = content.get("source_data", {})

    _check_dollar_figures(body, source, result)
    _check_friction_scores(body, source, result)
    _check_jurisdiction_consistency(content, result)

    return result


def _check_dollar_figures(body: str, source: dict[str, Any], result: FactCheckResult) -> None:
    """Verify dollar figures mentioned in the body against source cost data."""
    dollar_pattern = re.compile(r"\$[\d,]+(?:\.\d+)?")
    cited_amounts = dollar_pattern.findall(body)
    cost_estimates = source.get("cost_estimates", [])
    known_amounts = {
        f"${c.get('estimated_cost', 0):,.0f}" for c in cost_estimates if c.get("estimated_cost")
    }

    for amount in cited_amounts:
        normalised = amount.replace(",", "")
        if amount in known_amounts or normalised in known_amounts:
            result.verified.append(f"Dollar figure {amount} found in source data.")
        else:
            result.unverified.append(f"Dollar figure {amount} not traced to source data.")


def _check_friction_scores(body: str, source: dict[str, Any], result: FactCheckResult) -> None:
    """Verify friction scores cited in the body."""
    score_pattern = re.compile(
        r"(?:friction score|score of|scored)\s+(?:[\w\s,]*?\s)?(?:is\s+)?(\d{2,4})",
        re.IGNORECASE,
    )
    cited_scores = score_pattern.findall(body)
    known_scores = {str(s) for s in source.get("friction_scores", [])}

    for score in cited_scores:
        if score in known_scores:
            result.verified.append(f"Friction score {score} verified.")
        else:
            result.unverified.append(f"Friction score {score} not in source data.")


def _check_jurisdiction_consistency(content: dict[str, Any], result: FactCheckResult) -> None:
    """Ensure the jurisdiction in the body matches the metadata."""
    jurisdiction = content.get("jurisdiction", "")
    body = content.get("body", "")
    if jurisdiction and jurisdiction.lower() not in body.lower():
        result.warnings.append(
            f"Jurisdiction '{jurisdiction}' not mentioned in the body text."
        )
