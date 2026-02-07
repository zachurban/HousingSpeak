"""Content output models for generated advocacy materials."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class ContentType(str, enum.Enum):
    POLICY_BRIEF = "Policy_Brief"
    STAKEHOLDER_REPORT = "Stakeholder_Report"
    BLOG_POST = "Blog_Post"
    ALERT = "Alert"
    MODEL_ORDINANCE = "Model_Ordinance"
    TESTIMONY = "Testimony"
    OP_ED = "Op_Ed"
    INFOGRAPHIC = "Infographic"
    SOCIAL_MEDIA = "Social_Media"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class AudienceType(str, enum.Enum):
    PHA_BOARD = "PHA_Board"
    CITY_COUNCIL = "City_Council"
    STATE_LEGISLATURE = "State_Legislature"
    DEVELOPERS = "Developers"
    GENERAL_PUBLIC = "General_Public"
    HUD_OFFICIALS = "HUD_Officials"
    MEDIA = "Media"


class Content(Base):
    __tablename__ = "content"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType), nullable=False)
    audience: Mapped[AudienceType] = mapped_column(Enum(AudienceType), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(255), nullable=False)
    headline: Mapped[str] = mapped_column(String(500), nullable=False)
    executive_summary: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    call_to_action: Mapped[str | None] = mapped_column(Text)
    source_data: Mapped[dict | None] = mapped_column(JSON, default=dict)
    supporting_data: Mapped[dict | None] = mapped_column(JSON, default=dict)
    distribution_config: Mapped[dict | None] = mapped_column(JSON, default=dict)
    seo_keywords: Mapped[dict | None] = mapped_column(JSON, default=list)
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus), default=ContentStatus.DRAFT
    )
    generated_by: Mapped[str | None] = mapped_column(String(255))
    reviewed_by: Mapped[str | None] = mapped_column(String(255))
    stakeholder_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stakeholders.id")
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id")
    )
    version: Mapped[int] = mapped_column(default=1)
    parent_content_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
