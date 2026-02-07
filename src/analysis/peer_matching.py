"""Peer matching — identify comparable jurisdictions for benchmarking."""

from __future__ import annotations

from typing import Any


class PeerMatcher:
    """Match jurisdictions with similar demographics and housing markets."""

    SIMILARITY_WEIGHTS = {
        "population": 0.3,
        "region": 0.25,
        "housing_market": 0.25,
        "median_income": 0.2,
    }

    async def find_peers(
        self,
        target: dict[str, Any],
        candidates: list[dict[str, Any]],
        top_n: int = 5,
    ) -> list[dict[str, Any]]:
        """Return the *top_n* most similar jurisdictions to *target*.

        Each jurisdiction dict should include keys matching
        ``SIMILARITY_WEIGHTS`` (population, region, housing_market,
        median_income) plus a ``name`` key.
        """
        scored: list[tuple[float, dict[str, Any]]] = []
        for candidate in candidates:
            if candidate.get("name") == target.get("name"):
                continue
            score = self._similarity_score(target, candidate)
            scored.append((score, candidate))

        scored.sort(key=lambda t: t[0], reverse=True)
        return [c for _, c in scored[:top_n]]

    def _similarity_score(self, a: dict[str, Any], b: dict[str, Any]) -> float:
        score = 0.0
        # Population similarity (inverse of relative difference).
        pop_a = a.get("population", 0)
        pop_b = b.get("population", 0)
        if pop_a and pop_b:
            ratio = min(pop_a, pop_b) / max(pop_a, pop_b)
            score += ratio * self.SIMILARITY_WEIGHTS["population"]

        # Same region bonus.
        if a.get("region") and a.get("region") == b.get("region"):
            score += self.SIMILARITY_WEIGHTS["region"]

        # Housing market similarity.
        hm_a = a.get("housing_market", "")
        hm_b = b.get("housing_market", "")
        if hm_a and hm_a == hm_b:
            score += self.SIMILARITY_WEIGHTS["housing_market"]

        # Median income similarity.
        inc_a = a.get("median_income", 0)
        inc_b = b.get("median_income", 0)
        if inc_a and inc_b:
            ratio = min(inc_a, inc_b) / max(inc_a, inc_b)
            score += ratio * self.SIMILARITY_WEIGHTS["median_income"]

        return round(score, 4)
