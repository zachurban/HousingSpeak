"""Public content generator — blog posts, infographics, op-eds, social media."""

from __future__ import annotations

import uuid
from typing import Any

from src.integrations.claude_api import ClaudeContentGenerator
from src.integrations.housing_lens_client import HousingLensClient
from src.models.content import AudienceType, ContentType

CONTENT_TYPE_MAP = {
    "blog_post": ContentType.BLOG_POST,
    "infographic": ContentType.INFOGRAPHIC,
    "social_media": ContentType.SOCIAL_MEDIA,
    "op_ed": ContentType.OP_ED,
    "testimony": ContentType.TESTIMONY,
}


class PublicContentGenerator:
    """Create accessible public advocacy content from technical data."""

    def __init__(self) -> None:
        self.llm = ClaudeContentGenerator()
        self.lens = HousingLensClient()

    async def generate(
        self,
        jurisdiction: str,
        content_type: str = "blog_post",
        friction_data: list[dict[str, Any]] | None = None,
        topics: list[str] | None = None,
    ) -> dict[str, Any]:
        if not friction_data:
            friction_data = await self.lens.get_friction_scores(jurisdiction, topics)

        raw_text = await self.llm.generate_public_content(
            friction_data=friction_data,
            content_type=content_type,
            jurisdiction=jurisdiction,
        )

        # For social media, also generate platform-specific variants.
        social_versions: dict[str, str] | None = None
        if content_type == "social_media":
            social_versions = await self._generate_social_variants(friction_data, jurisdiction)

        ct = CONTENT_TYPE_MAP.get(content_type, ContentType.BLOG_POST)

        return {
            "id": str(uuid.uuid4()),
            "content_type": ct.value,
            "audience": AudienceType.GENERAL_PUBLIC.value,
            "jurisdiction": jurisdiction,
            "headline": _extract_headline(raw_text),
            "body": raw_text,
            "call_to_action": _extract_cta(raw_text),
            "source_data": {"friction_data": friction_data},
            "supporting_data": {"social_media_versions": social_versions},
            "seo_keywords": _extract_keywords(friction_data, jurisdiction),
            "generated_by": f"public_content_generator_v1_{content_type}",
            "status": "draft",
        }

    async def _generate_social_variants(
        self, friction_data: list[dict[str, Any]], jurisdiction: str
    ) -> dict[str, str]:
        variants: dict[str, str] = {}
        for platform in ("twitter", "linkedin"):
            text = await self.llm.generate(
                system_prompt=(
                    f"Write a compelling {platform} post about housing policy barriers. "
                    f"{'Keep under 280 characters.' if platform == 'twitter' else 'Professional tone.'}"
                ),
                user_prompt=f"Jurisdiction: {jurisdiction}\nData: {friction_data[:3]}",
                max_tokens=512,
            )
            variants[platform] = text
        return variants


def _extract_headline(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped[:500]
    return "Housing Policy Update"


def _extract_cta(text: str) -> str | None:
    lower = text.lower()
    for marker in ("call to action", "what you can do", "take action"):
        idx = lower.find(marker)
        if idx != -1:
            remaining = text[idx:]
            paragraphs = remaining.split("\n\n")
            return "\n\n".join(paragraphs[:2]).strip()
    return None


def _extract_keywords(friction_data: list[dict[str, Any]], jurisdiction: str) -> list[str]:
    keywords = [jurisdiction.lower(), "housing policy", "affordable housing"]
    for item in friction_data[:5]:
        topic = item.get("topic", "")
        if topic:
            keywords.append(topic.lower().replace("_", " "))
    return keywords
