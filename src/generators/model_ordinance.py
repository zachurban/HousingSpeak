"""Model ordinance generator — draft ordinance language adapted from successful jurisdictions."""

from __future__ import annotations

import uuid
from typing import Any

from src.integrations.claude_api import ClaudeContentGenerator
from src.integrations.housing_lens_client import HousingLensClient
from src.models.content import AudienceType, ContentType


class ModelOrdinanceGenerator:
    """Generate draft model ordinance text adapted from peer jurisdictions."""

    def __init__(self) -> None:
        self.llm = ClaudeContentGenerator()
        self.lens = HousingLensClient()

    async def generate(
        self,
        target_jurisdiction: str,
        source_jurisdiction: str | None = None,
        topic: str = "",
        friction_data: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Produce model ordinance language.

        If *source_jurisdiction* is provided, the ordinance will be framed as
        an adaptation of that jurisdiction's approach.
        """
        if not friction_data:
            friction_data = await self.lens.get_friction_scores(
                target_jurisdiction, [topic] if topic else None
            )

        source_label = source_jurisdiction or "best-practice jurisdictions"

        raw_text = await self.llm.generate(
            system_prompt=(
                "You are a municipal legislative drafter creating model ordinance "
                "language for housing policy reform. Write clear, precise legal "
                "language that a city council could adopt. Include whereas clauses, "
                "definitions, operative sections, and an effective-date provision."
            ),
            user_prompt=(
                f"Draft a model ordinance for {target_jurisdiction} addressing "
                f"'{topic}' barriers.\n\n"
                f"This ordinance is inspired by reforms in {source_label}.\n\n"
                f"Friction data:\n"
                + "\n".join(
                    f"- {d.get('topic', 'N/A')}: score {d.get('friction_score', 'N/A')}"
                    for d in friction_data[:5]
                )
                + "\n\nProduce the full ordinance text."
            ),
            max_tokens=4096,
            temperature=0.5,
        )

        return {
            "id": str(uuid.uuid4()),
            "content_type": ContentType.MODEL_ORDINANCE.value,
            "audience": AudienceType.CITY_COUNCIL.value,
            "jurisdiction": target_jurisdiction,
            "headline": f"Model Ordinance — {topic or 'Housing Reform'} ({target_jurisdiction})",
            "body": raw_text,
            "source_data": {
                "friction_data": friction_data,
                "source_jurisdiction": source_jurisdiction,
                "topic": topic,
            },
            "generated_by": "model_ordinance_generator_v1",
            "status": "draft",
        }
