"""Pydantic schemas for API request/response validation."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.models.alert import AlertPriority, AlertStatus, AlertType
from src.models.campaign import CampaignStatus
from src.models.content import AudienceType, ContentStatus, ContentType
from src.models.stakeholder import AlertFrequency, AlertThreshold, StakeholderType


# --- Stakeholder Schemas ---


class ProjectInfo(BaseModel):
    project_id: str
    stage: str = "Pre-Entitlement"
    location: str
    unit_count: int = 0


class StakeholderCreate(BaseModel):
    stakeholder_type: StakeholderType
    organization: str
    jurisdiction: str
    contact_name: str | None = None
    contact_email: str | None = None
    interests: list[str] = Field(default_factory=list)
    notification_frequency: AlertFrequency = AlertFrequency.WEEKLY_DIGEST
    notification_channels: list[str] = Field(default_factory=lambda: ["email"])
    alert_threshold: AlertThreshold = AlertThreshold.MEDIUM
    projects: list[ProjectInfo] = Field(default_factory=list)


class StakeholderResponse(StakeholderCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Content Schemas ---


class ContentGenerateRequest(BaseModel):
    content_type: ContentType
    audience: AudienceType
    jurisdiction: str
    friction_data: list[dict] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    stakeholder_id: uuid.UUID | None = None
    campaign_id: uuid.UUID | None = None
    additional_context: str | None = None


class ContentResponse(BaseModel):
    id: uuid.UUID
    content_type: ContentType
    audience: AudienceType
    jurisdiction: str
    headline: str
    executive_summary: str | None = None
    body: str
    call_to_action: str | None = None
    source_data: dict | None = None
    supporting_data: dict | None = None
    status: ContentStatus
    version: int
    generated_by: str | None = None
    reviewed_by: str | None = None
    created_at: datetime
    published_at: datetime | None = None

    model_config = {"from_attributes": True}


class ContentReviewAction(BaseModel):
    action: str = Field(pattern="^(approve|reject|request_changes)$")
    reviewer: str
    comments: str | None = None


# --- Alert Schemas ---


class AlertResponse(BaseModel):
    id: uuid.UUID
    stakeholder_id: uuid.UUID
    priority: AlertPriority
    alert_type: AlertType
    headline: str
    summary: str
    action_required: bool
    action_deadline: datetime | None = None
    related_project_ids: list[str]
    recommended_actions: list[str] | None = None
    status: AlertStatus
    created_at: datetime
    sent_at: datetime | None = None

    model_config = {"from_attributes": True}


class AlertGenerateRequest(BaseModel):
    stakeholder_ids: list[uuid.UUID] | None = None
    since: datetime | None = None


# --- Campaign Schemas ---


class CampaignCreate(BaseModel):
    name: str
    description: str | None = None
    jurisdiction: str
    target_audience: list[str] = Field(default_factory=list)
    policy_goals: list[str] = Field(default_factory=list)
    stakeholder_ids: list[str] = Field(default_factory=list)


class CampaignResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    jurisdiction: str
    target_audience: list[str]
    policy_goals: list[str] | None = None
    status: CampaignStatus
    total_touches: int
    current_step: int
    start_date: datetime | None = None
    end_date: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Comparative Analysis Schemas ---


class ComparativeAnalysisRequest(BaseModel):
    jurisdictions: list[str]
    metric: str = "friction_score"
    topics: list[str] = Field(default_factory=list)


class ComparativeAnalysisResponse(BaseModel):
    ranking: list[dict]
    peer_group: list[dict]
    best_practices: list[dict]
    opportunity_gaps: list[dict]
    narrative_summary: str
    visualization_config: dict | None = None
