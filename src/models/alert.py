"""Alert models for stakeholder notifications."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class AlertPriority(str, enum.Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertType(str, enum.Enum):
    FEDERAL_REGISTER_CHANGE = "federal_register_change"
    EMERGING_TREND = "emerging_trend"
    MEETING_AGENDA = "meeting_agenda"
    FRICTION_SCORE_CHANGE = "friction_score_change"
    PROJECT_IMPACT = "project_impact"
    POLICY_UPDATE = "policy_update"
    DEADLINE_REMINDER = "deadline_reminder"


class AlertStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ACTED_ON = "acted_on"
    DISMISSED = "dismissed"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    stakeholder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stakeholders.id"), nullable=False
    )
    priority: Mapped[AlertPriority] = mapped_column(Enum(AlertPriority), nullable=False)
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType), nullable=False)
    headline: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    action_required: Mapped[bool] = mapped_column(Boolean, default=False)
    action_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    related_project_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    recommended_actions: Mapped[dict | None] = mapped_column(JSON, default=list)
    source_data: Mapped[dict | None] = mapped_column(JSON, default=dict)
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus), default=AlertStatus.PENDING
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
