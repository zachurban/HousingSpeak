"""Tests for the alert generator helpers."""

from __future__ import annotations

from src.generators.alerts import _build_headline, _classify, _recommend_actions
from src.models.alert import AlertPriority, AlertType


class TestClassify:
    def test_federal_changes_highest(self) -> None:
        priority, atype = _classify([{"title": "new rule"}], [], [])
        assert priority == AlertPriority.HIGH
        assert atype == AlertType.FEDERAL_REGISTER_CHANGE

    def test_policy_updates_medium(self) -> None:
        priority, atype = _classify([], [{"title": "update"}], [])
        assert priority == AlertPriority.MEDIUM
        assert atype == AlertType.POLICY_UPDATE

    def test_trends_low(self) -> None:
        priority, atype = _classify([], [], [{"title": "trend"}])
        assert priority == AlertPriority.LOW
        assert atype == AlertType.EMERGING_TREND


class TestBuildHeadline:
    def test_uses_first_change_title(self) -> None:
        changes = [{"title": "New Parking Rule"}]
        assert _build_headline(changes, "Denver, CO") == "Denver, CO: New Parking Rule"

    def test_fallback_when_no_changes(self) -> None:
        assert "updates available" in _build_headline([], "Denver, CO")


class TestRecommendActions:
    def test_urgent_includes_immediate_review(self) -> None:
        actions = _recommend_actions(AlertPriority.URGENT, AlertType.FEDERAL_REGISTER_CHANGE)
        assert any("immediately" in a.lower() for a in actions)

    def test_federal_change_includes_comment(self) -> None:
        actions = _recommend_actions(AlertPriority.HIGH, AlertType.FEDERAL_REGISTER_CHANGE)
        assert any("comment" in a.lower() for a in actions)
