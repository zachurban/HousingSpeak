"""Comparative analysis — benchmarking jurisdictions against each other."""

from __future__ import annotations

from typing import Any

from src.integrations.claude_api import ClaudeContentGenerator
from src.integrations.housing_lens_client import HousingLensClient


class ComparativeAnalyzer:
    """Rank and compare jurisdictions on friction scores and policy outcomes."""

    def __init__(self) -> None:
        self.lens = HousingLensClient()
        self.llm = ClaudeContentGenerator()

    async def analyze(
        self,
        jurisdictions: list[str],
        metric: str = "friction_score",
        topics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run a comparative analysis across *jurisdictions*.

        Returns a dict with ranking, peer_group, best_practices,
        opportunity_gaps, narrative_summary, and visualization_config.
        """
        # Fetch scores for every jurisdiction.
        scores_by_jur: dict[str, list[dict[str, Any]]] = {}
        for jur in jurisdictions:
            scores_by_jur[jur] = await self.lens.get_friction_scores(jur, topics)

        ranking = _rank(scores_by_jur, metric)
        peer_group = _identify_peers(jurisdictions, ranking)
        best_practices = _extract_best_practices(ranking[:3], scores_by_jur)
        opportunity_gaps = _find_gaps(ranking, scores_by_jur)

        narrative = await self.llm.generate(
            system_prompt=(
                "You are a housing policy analyst writing a comparative benchmarking "
                "report. Use a constructive, competitive tone. Highlight where "
                "lagging jurisdictions can learn from leaders."
            ),
            user_prompt=(
                f"Jurisdictions compared: {', '.join(jurisdictions)}\n"
                f"Ranking ({metric}): {ranking}\n"
                f"Best practices: {best_practices}\n"
                f"Gaps: {opportunity_gaps}\n\n"
                "Write a two-paragraph narrative summary."
            ),
            max_tokens=1024,
        )

        viz = _build_viz_config(ranking, metric)

        return {
            "ranking": ranking,
            "peer_group": peer_group,
            "best_practices": best_practices,
            "opportunity_gaps": opportunity_gaps,
            "narrative_summary": narrative,
            "visualization_config": viz,
        }


def _rank(
    scores_by_jur: dict[str, list[dict[str, Any]]], metric: str
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for jur, scores in scores_by_jur.items():
        avg = _avg_metric(scores, metric)
        ranked.append({"jurisdiction": jur, f"avg_{metric}": avg})
    ranked.sort(key=lambda r: r.get(f"avg_{metric}", 0))
    return ranked


def _avg_metric(scores: list[dict[str, Any]], metric: str) -> float:
    values = [s.get(metric, 0) for s in scores if s.get(metric) is not None]
    return round(sum(values) / len(values), 2) if values else 0.0


def _identify_peers(
    jurisdictions: list[str], ranking: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    if not ranking:
        return []
    target = ranking[-1]  # worst-performing for improvement focus
    return [r for r in ranking if r["jurisdiction"] != target["jurisdiction"]]


def _extract_best_practices(
    top_ranked: list[dict[str, Any]], scores_by_jur: dict[str, list[dict[str, Any]]]
) -> list[dict[str, Any]]:
    practices: list[dict[str, Any]] = []
    for entry in top_ranked:
        jur = entry["jurisdiction"]
        low_friction = sorted(
            scores_by_jur.get(jur, []), key=lambda s: s.get("friction_score", 0)
        )[:3]
        practices.append({"jurisdiction": jur, "low_friction_areas": low_friction})
    return practices


def _find_gaps(
    ranking: list[dict[str, Any]], scores_by_jur: dict[str, list[dict[str, Any]]]
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    if len(ranking) < 2:
        return gaps
    worst = ranking[-1]
    best = ranking[0]
    worst_topics = {s.get("topic"): s for s in scores_by_jur.get(worst["jurisdiction"], [])}
    best_topics = {s.get("topic"): s for s in scores_by_jur.get(best["jurisdiction"], [])}
    for topic, worst_score in worst_topics.items():
        best_score = best_topics.get(topic)
        if best_score:
            gap = (worst_score.get("friction_score", 0) - best_score.get("friction_score", 0))
            if gap > 0:
                gaps.append({
                    "topic": topic,
                    "gap": gap,
                    "lagging": worst["jurisdiction"],
                    "leading": best["jurisdiction"],
                })
    gaps.sort(key=lambda g: g.get("gap", 0), reverse=True)
    return gaps


def _build_viz_config(ranking: list[dict[str, Any]], metric: str) -> dict[str, Any]:
    return {
        "chart_type": "bar_chart",
        "title": f"Jurisdiction Comparison — {metric.replace('_', ' ').title()}",
        "x_axis": "jurisdiction",
        "y_axis": f"avg_{metric}",
        "data": ranking,
    }
