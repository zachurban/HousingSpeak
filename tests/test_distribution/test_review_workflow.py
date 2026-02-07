"""Tests for the review workflow router."""

from __future__ import annotations

import pytest

from src.api.review_workflow import _passes_automated_checks, route_content


class TestPassesAutomatedChecks:
    def test_passes_with_body_and_source(self) -> None:
        content = {"body": "A" * 100, "source_data": {"friction_scores": [847]}}
        assert _passes_automated_checks(content) is True

    def test_fails_with_short_body(self) -> None:
        content = {"body": "Short", "source_data": {"friction_scores": [847]}}
        assert _passes_automated_checks(content) is False

    def test_fails_without_source_data(self) -> None:
        content = {"body": "A" * 100, "source_data": None}
        assert _passes_automated_checks(content) is False


@pytest.mark.asyncio
async def test_route_alert_auto_publishes() -> None:
    content = {
        "id": "123",
        "content_type": "Alert",
        "body": "A" * 100,
        "source_data": {"friction_scores": [847]},
    }
    result = await route_content(content)
    assert result["status"] == "approved"
    assert result["review_route"] == "auto_publish"


@pytest.mark.asyncio
async def test_route_model_ordinance_to_legal() -> None:
    content = {"id": "456", "content_type": "Model_Ordinance", "body": "Draft text."}
    result = await route_content(content)
    assert result["status"] == "in_review"
    assert result["review_route"] == "legal_review"


@pytest.mark.asyncio
async def test_route_blog_post_to_editor() -> None:
    content = {"id": "789", "content_type": "Blog_Post", "body": "Blog content."}
    result = await route_content(content)
    assert result["status"] == "in_review"
    assert result["review_route"] == "editor_review"
