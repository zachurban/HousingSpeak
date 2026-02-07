"""Tests for analysis module helpers."""

from __future__ import annotations

import pytest

from src.analysis.comparative_analysis import _avg_metric, _find_gaps, _rank
from src.analysis.impact_calculator import _build_narrative
from src.analysis.peer_matching import PeerMatcher


class TestRanking:
    def test_ranks_by_average(self) -> None:
        scores = {
            "CityA": [{"friction_score": 800}, {"friction_score": 600}],
            "CityB": [{"friction_score": 300}, {"friction_score": 200}],
        }
        ranked = _rank(scores, "friction_score")
        assert ranked[0]["jurisdiction"] == "CityB"  # lower = better rank
        assert ranked[1]["jurisdiction"] == "CityA"

    def test_avg_metric_empty(self) -> None:
        assert _avg_metric([], "friction_score") == 0.0


class TestFindGaps:
    def test_identifies_gap(self) -> None:
        ranking = [
            {"jurisdiction": "CityB", "avg_friction_score": 250},
            {"jurisdiction": "CityA", "avg_friction_score": 700},
        ]
        scores = {
            "CityA": [{"topic": "Parking", "friction_score": 700}],
            "CityB": [{"topic": "Parking", "friction_score": 250}],
        }
        gaps = _find_gaps(ranking, scores)
        assert len(gaps) == 1
        assert gaps[0]["topic"] == "Parking"
        assert gaps[0]["gap"] == 450


class TestBuildNarrative:
    def test_includes_jurisdiction(self) -> None:
        result = _build_narrative("Denver, CO", 100000, 90, [])
        assert "Denver, CO" in result
        assert "$100,000" in result


class TestPeerMatcher:
    @pytest.mark.asyncio
    async def test_find_peers_excludes_self(self) -> None:
        matcher = PeerMatcher()
        target = {"name": "Denver", "population": 700000, "region": "West"}
        candidates = [
            {"name": "Denver", "population": 700000, "region": "West"},
            {"name": "Portland", "population": 650000, "region": "West"},
        ]
        peers = await matcher.find_peers(target, candidates)
        assert all(p["name"] != "Denver" for p in peers)

    @pytest.mark.asyncio
    async def test_find_peers_ranks_by_similarity(self) -> None:
        matcher = PeerMatcher()
        target = {"name": "Denver", "population": 700000, "region": "West", "median_income": 70000}
        candidates = [
            {"name": "Portland", "population": 650000, "region": "West", "median_income": 68000},
            {"name": "NYC", "population": 8000000, "region": "East", "median_income": 60000},
        ]
        peers = await matcher.find_peers(target, candidates)
        assert peers[0]["name"] == "Portland"
