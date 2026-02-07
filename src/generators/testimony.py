"""Testimony generator — spoken testimony drafts with data citations."""

from __future__ import annotations

import uuid
from typing import Any

from src.integrations.claude_api import ClaudeContentGenerator
from src.integrations.housing_lens_client import HousingLensClient
from src.models.content import AudienceType, ContentType


class TestimonyGenerator:
    """Draft spoken testimony for public hearings and legislative sessions."""

    def __init__(self) -> None:
        self.llm = ClaudeContentGenerator()
        self.lens = HousingLensClient()

    async def generate(
        self,
        jurisdiction: str,
        audience: AudienceType = AudienceType.CITY_COUNCIL,
        friction_data: list[dict[str, Any]] | None = None,
        topics: list[str] | None = None,
        time_limit_minutes: int = 3,
        include_personal_framing: bool = True,
    ) -> dict[str, Any]:
        if not friction_data:
            friction_data = await self.lens.get_friction_scores(jurisdiction, topics)

        raw_text = await self.llm.generate_testimony(
            friction_data=friction_data,
            jurisdiction=jurisdiction,
            time_limit_minutes=time_limit_minutes,
        )

        word_count = len(raw_text.split())
        estimated_minutes = round(word_count / 150, 1)  # ~150 words/minute spoken

        return {
            "id": str(uuid.uuid4()),
            "content_type": ContentType.TESTIMONY.value,
            "audience": audience.value,
            "jurisdiction": jurisdiction,
            "headline": f"Public Testimony — Housing Barriers in {jurisdiction}",
            "body": raw_text,
            "source_data": {"friction_data": friction_data},
            "supporting_data": {
                "word_count": word_count,
                "estimated_minutes": estimated_minutes,
                "time_limit_minutes": time_limit_minutes,
            },
            "generated_by": "testimony_generator_v1",
            "status": "draft",
        }
