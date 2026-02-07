"""Success story mining — find jurisdictions that solved similar problems."""

from __future__ import annotations

from typing import Any

from src.integrations.housing_ear_client import HousingEarClient
from src.integrations.housing_lens_client import HousingLensClient


class SuccessStoryFinder:
    """Identify jurisdictions with low friction in areas where others struggle."""

    def __init__(self) -> None:
        self.lens = HousingLensClient()
        self.ear = HousingEarClient()

    async def find(
        self,
        target_jurisdiction: str,
        candidate_jurisdictions: list[str],
        topics: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Return success stories relevant to *target_jurisdiction*'s high-friction areas."""
        target_scores = await self.lens.get_friction_scores(target_jurisdiction, topics)
        high_friction_topics = [
            s.get("topic")
            for s in sorted(
                target_scores, key=lambda s: s.get("friction_score", 0), reverse=True
            )[:5]
            if s.get("topic")
        ]

        stories: list[dict[str, Any]] = []
        for candidate in candidate_jurisdictions:
            if candidate == target_jurisdiction:
                continue
            candidate_scores = await self.lens.get_friction_scores(candidate, high_friction_topics)
            for cs in candidate_scores:
                topic = cs.get("topic")
                if topic in high_friction_topics and cs.get("friction_score", 999) < 300:
                    stories.append({
                        "jurisdiction": candidate,
                        "topic": topic,
                        "friction_score": cs.get("friction_score"),
                        "detail": cs.get("detail"),
                    })

        stories.sort(key=lambda s: s.get("friction_score", 999))
        return stories
