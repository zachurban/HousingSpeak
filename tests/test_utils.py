"""Tests for utility modules."""

from __future__ import annotations

from src.utils.fact_checking import FactCheckResult, check_content
from src.utils.narrative_construction import (
    build_executive_summary,
    format_for_audience,
    translate_friction_to_impact,
)


class TestTranslateFrictionToImpact:
    def test_generates_impact_text(self, sample_friction_data: list[dict]) -> None:
        result = translate_friction_to_impact(sample_friction_data)
        assert "Parking Requirements" in result
        assert "barrier" in result.lower()

    def test_empty_data(self) -> None:
        assert translate_friction_to_impact([]) == ""


class TestBuildExecutiveSummary:
    def test_includes_jurisdiction(self, sample_friction_data: list[dict]) -> None:
        summary = build_executive_summary(sample_friction_data, "Denver, CO", 134000)
        assert "Denver, CO" in summary
        assert "$134,000" in summary

    def test_without_cost(self, sample_friction_data: list[dict]) -> None:
        summary = build_executive_summary(sample_friction_data, "Denver, CO")
        assert "Denver, CO" in summary


class TestFormatForAudience:
    def test_city_council_adaptation(self) -> None:
        text = "you should review this"
        result = format_for_audience(text, "City_Council")
        assert "Council may wish to" in result

    def test_general_public_adaptation(self) -> None:
        text = "regulatory friction is high"
        result = format_for_audience(text, "General_Public")
        assert "red tape" in result


class TestFactChecking:
    def test_verified_dollar_figure(self, sample_content: dict) -> None:
        # Inject a dollar figure that matches the source data.
        sample_content["body"] += "\nThe parking barrier alone costs $47,000."
        result = check_content(sample_content)
        assert any("$47,000" in v for v in result.verified)

    def test_unverified_figure_flagged(self) -> None:
        content = {
            "body": "This costs $999,999 per unit.",
            "jurisdiction": "Denver, CO",
            "source_data": {"cost_estimates": [], "friction_scores": []},
        }
        result = check_content(content)
        assert len(result.unverified) > 0

    def test_friction_score_verified(self, sample_content: dict) -> None:
        result = check_content(sample_content)
        assert any("847" in v for v in result.verified)


class TestFactCheckResult:
    def test_passed_when_no_unverified(self) -> None:
        r = FactCheckResult()
        r.verified.append("ok")
        assert r.passed is True

    def test_failed_when_unverified_present(self) -> None:
        r = FactCheckResult()
        r.unverified.append("bad claim")
        assert r.passed is False
