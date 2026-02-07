"""Tests for the policy brief generator helpers."""

from __future__ import annotations

from src.generators.policy_brief import _extract_headline, _extract_section, _merge_cost_data


class TestExtractHeadline:
    def test_returns_first_non_empty_line(self) -> None:
        text = "\n\n# My Headline\nSome body text."
        assert _extract_headline(text) == "My Headline"

    def test_strips_markdown_hashes(self) -> None:
        text = "## Sub-heading\nBody."
        assert _extract_headline(text) == "Sub-heading"

    def test_fallback_when_empty(self) -> None:
        assert _extract_headline("") == "Policy Brief"


class TestExtractSection:
    def test_extracts_matching_section(self) -> None:
        text = (
            "# Executive Summary\nThis is the summary.\n\n"
            "# Problem Statement\nThis is the problem."
        )
        result = _extract_section(text, "Executive Summary")
        assert result is not None
        assert "This is the summary." in result

    def test_returns_none_when_missing(self) -> None:
        text = "# Introduction\nSome text."
        assert _extract_section(text, "Nonexistent") is None


class TestMergeCostData:
    def test_merges_cost_into_issues(self) -> None:
        issues = [{"topic": "Parking Requirements", "friction_score": 847}]
        costs = [{"topic": "Parking Requirements", "estimated_cost": 47000, "detail": "info"}]
        merged = _merge_cost_data(issues, costs)
        assert merged[0]["estimated_cost"] == 47000
        assert merged[0]["cost_detail"] == "info"

    def test_handles_missing_cost(self) -> None:
        issues = [{"topic": "Zoning", "friction_score": 600}]
        merged = _merge_cost_data(issues, [])
        assert "estimated_cost" not in merged[0]
