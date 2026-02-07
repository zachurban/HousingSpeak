"""Tests for the public content generator helpers."""

from __future__ import annotations

from src.generators.public_content import _extract_cta, _extract_headline, _extract_keywords


class TestExtractHeadline:
    def test_basic_headline(self) -> None:
        assert _extract_headline("# Big News\nBody.") == "Big News"

    def test_fallback(self) -> None:
        assert _extract_headline("") == "Housing Policy Update"


class TestExtractCta:
    def test_finds_call_to_action_section(self) -> None:
        text = "Some intro.\n\n## Call to Action\nContact your representative today."
        result = _extract_cta(text)
        assert result is not None
        assert "Contact" in result

    def test_returns_none_when_missing(self) -> None:
        assert _extract_cta("No CTA here.") is None


class TestExtractKeywords:
    def test_includes_jurisdiction(self) -> None:
        kw = _extract_keywords([], "Denver, CO")
        assert "denver, co" in kw

    def test_includes_topics(self) -> None:
        data = [{"topic": "Parking_Requirements"}, {"topic": "Zoning"}]
        kw = _extract_keywords(data, "Denver, CO")
        assert "parking requirements" in kw
        assert "zoning" in kw
