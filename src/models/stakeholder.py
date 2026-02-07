"""Stakeholder profile models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class StakeholderType(str, enum.Enum):
    PHA_EXECUTIVE_DIRECTOR = "PHA_Executive_Director"
    CITY_COUNCIL = "City_Council"
    DEVELOPER = "Developer"
    HUD_REGIONAL_OFFICE = "HUD_Regional_Office"
    STATE_AGENCY = "State_Agency"


class AlertFrequency(str, enum.Enum):
    IMMEDIATE = "immediate"
    DAILY_DIGEST = "daily_digest"
    WEEKLY_DIGEST = "weekly_digest"
    MONTHLY_SUMMARY = "monthly_summary"


class AlertThreshold(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT_ONLY = "urgent_only"


class Stakeholder(Base):
    __tablename__ = "stakeholders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    stakeholder_type: Mapped[StakeholderType] = mapped_column(Enum(StakeholderType), nullable=False)
    organization: Mapped[str] = mapped_column(String(255), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(255))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    interests: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    notification_frequency: Mapped[AlertFrequency] = mapped_column(
        Enum(AlertFrequency), default=AlertFrequency.WEEKLY_DIGEST
    )
    notification_channels: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=lambda: ["email"]
    )
    alert_threshold: Mapped[AlertThreshold] = mapped_column(
        Enum(AlertThreshold), default=AlertThreshold.MEDIUM
    )
    projects: Mapped[dict | None] = mapped_column(JSON, default=list)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
