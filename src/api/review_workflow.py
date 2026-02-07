"""Content review workflow — route content through appropriate approval chains."""

from __future__ import annotations

import logging
from typing import Any

from src.models.content import ContentStatus, ContentType

logger = logging.getLogger(__name__)

# Content types that can be auto-published without human review.
AUTO_PUBLISH_TYPES = {ContentType.ALERT}

# Content types requiring editor review.
EDITOR_REVIEW_TYPES = {ContentType.BLOG_POST, ContentType.POLICY_BRIEF, ContentType.OP_ED}

# Content types requiring legal review.
LEGAL_REVIEW_TYPES = {ContentType.MODEL_ORDINANCE, ContentType.TESTIMONY}


async def route_content(content: dict[str, Any]) -> dict[str, Any]:
    """Determine the review path for generated content and update its status.

    Returns the content dict with ``status`` and ``review_route`` updated.
    """
    content_type_str = content.get("content_type", "")
    try:
        content_type = ContentType(content_type_str)
    except ValueError:
        content_type = None

    if content_type in AUTO_PUBLISH_TYPES:
        if _passes_automated_checks(content):
            content["status"] = ContentStatus.APPROVED.value
            content["review_route"] = "auto_publish"
            logger.info("Content %s auto-approved.", content.get("id"))
            return content

    if content_type in LEGAL_REVIEW_TYPES:
        content["status"] = ContentStatus.IN_REVIEW.value
        content["review_route"] = "legal_review"
        logger.info("Content %s routed to legal review.", content.get("id"))
        return content

    if content_type in EDITOR_REVIEW_TYPES:
        content["status"] = ContentStatus.IN_REVIEW.value
        content["review_route"] = "editor_review"
        logger.info("Content %s routed to editor review.", content.get("id"))
        return content

    # Default: executive approval for anything unrecognised or high-risk.
    content["status"] = ContentStatus.IN_REVIEW.value
    content["review_route"] = "executive_approval"
    logger.info("Content %s routed to executive approval.", content.get("id"))
    return content


def _passes_automated_checks(content: dict[str, Any]) -> bool:
    """Run lightweight quality checks that gate auto-publishing."""
    body = content.get("body", "")
    if not body or len(body) < 50:
        return False
    # Ensure source data is present (all claims must be traceable).
    if not content.get("source_data"):
        return False
    return True
