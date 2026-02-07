"""FastAPI application and route definitions."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query

from src.analysis.comparative_analysis import ComparativeAnalyzer
from src.analysis.impact_calculator import ImpactCalculator
from src.generators.alerts import AlertGenerator
from src.generators.model_ordinance import ModelOrdinanceGenerator
from src.generators.policy_brief import PolicyBriefGenerator
from src.generators.public_content import PublicContentGenerator
from src.generators.stakeholder_report import StakeholderReportGenerator
from src.generators.testimony import TestimonyGenerator
from src.models.content import AudienceType, ContentType
from src.models.schemas import (
    AlertGenerateRequest,
    AlertResponse,
    CampaignCreate,
    CampaignResponse,
    ComparativeAnalysisRequest,
    ComparativeAnalysisResponse,
    ContentGenerateRequest,
    ContentResponse,
    ContentReviewAction,
    StakeholderCreate,
    StakeholderResponse,
)

from src.api.webhooks import router as webhooks_router

app = FastAPI(
    title="HousingSpeak API",
    description="Advocacy & Communication Automation for the HousingMind ecosystem",
    version="0.1.0",
)
app.include_router(webhooks_router)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Content Generation
# ---------------------------------------------------------------------------


@app.post("/api/v1/content/generate", response_model=ContentResponse)
async def generate_content(req: ContentGenerateRequest) -> dict:
    """Generate advocacy content based on friction data and audience."""
    generator: PolicyBriefGenerator | PublicContentGenerator | TestimonyGenerator | ModelOrdinanceGenerator

    if req.content_type == ContentType.POLICY_BRIEF:
        generator = PolicyBriefGenerator()
        result = await generator.generate(
            jurisdiction=req.jurisdiction,
            audience=req.audience,
            friction_data=req.friction_data or None,
            topics=req.topics or None,
        )
    elif req.content_type == ContentType.TESTIMONY:
        gen_test = TestimonyGenerator()
        result = await gen_test.generate(
            jurisdiction=req.jurisdiction,
            audience=req.audience,
            friction_data=req.friction_data or None,
            topics=req.topics or None,
        )
    elif req.content_type == ContentType.MODEL_ORDINANCE:
        gen_ord = ModelOrdinanceGenerator()
        result = await gen_ord.generate(
            target_jurisdiction=req.jurisdiction,
            topic=req.topics[0] if req.topics else "",
            friction_data=req.friction_data or None,
        )
    else:
        gen_pub = PublicContentGenerator()
        result = await gen_pub.generate(
            jurisdiction=req.jurisdiction,
            content_type=req.content_type.value.lower(),
            friction_data=req.friction_data or None,
            topics=req.topics or None,
        )

    # Ensure required fields for the response model.
    result.setdefault("id", str(uuid.uuid4()))
    result.setdefault("version", 1)
    result.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    return result


@app.get("/api/v1/content/{content_id}", response_model=ContentResponse)
async def get_content(content_id: uuid.UUID) -> dict:
    """Retrieve a previously generated content item."""
    # Placeholder — would query the database in production.
    raise HTTPException(status_code=404, detail="Content not found")


@app.post("/api/v1/content/{content_id}/review")
async def review_content(content_id: uuid.UUID, action: ContentReviewAction) -> dict:
    """Submit a review action (approve / reject / request_changes)."""
    # Placeholder — would update DB record and route accordingly.
    return {
        "content_id": str(content_id),
        "action": action.action,
        "reviewer": action.reviewer,
        "status": "approved" if action.action == "approve" else "in_review",
    }


# ---------------------------------------------------------------------------
# Stakeholder Reports
# ---------------------------------------------------------------------------


@app.post("/api/v1/reports/stakeholder", response_model=ContentResponse)
async def generate_stakeholder_report(
    stakeholder_id: uuid.UUID | None = None,
    jurisdiction: str = Query(default=""),
) -> dict:
    """Generate a tailored stakeholder report."""
    generator = StakeholderReportGenerator()
    # In production, fetch stakeholder from DB by ID.
    stakeholder = {
        "id": str(stakeholder_id or uuid.uuid4()),
        "organization": "Stakeholder Org",
        "jurisdiction": jurisdiction or "Denver, CO",
        "interests": [],
        "projects": [],
        "stakeholder_type": "PHA_Executive_Director",
    }
    result = await generator.generate(stakeholder=stakeholder)
    result.setdefault("id", str(uuid.uuid4()))
    result.setdefault("version", 1)
    result.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    return result


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------


@app.post("/api/v1/alerts/generate", response_model=list[AlertResponse])
async def generate_alerts(req: AlertGenerateRequest) -> list[dict]:
    """Generate personalized alerts for stakeholders."""
    generator = AlertGenerator()
    # In production, fetch stakeholder profiles from DB.
    stakeholder_profiles: list[dict] = []
    since = req.since.isoformat() if req.since else None
    alerts = await generator.generate_alerts(stakeholder_profiles, since=since)
    return alerts


# ---------------------------------------------------------------------------
# Comparative Analysis
# ---------------------------------------------------------------------------


@app.post("/api/v1/analysis/comparative", response_model=ComparativeAnalysisResponse)
async def comparative_analysis(req: ComparativeAnalysisRequest) -> dict:
    """Run a comparative benchmarking analysis across jurisdictions."""
    analyzer = ComparativeAnalyzer()
    return await analyzer.analyze(
        jurisdictions=req.jurisdictions,
        metric=req.metric,
        topics=req.topics or None,
    )


# ---------------------------------------------------------------------------
# Impact Calculator
# ---------------------------------------------------------------------------


@app.get("/api/v1/analysis/impact")
async def calculate_impact(
    jurisdiction: str = Query(...),
    unit_count: int = Query(default=1),
) -> dict:
    """Calculate the financial and timeline impact of friction."""
    calc = ImpactCalculator()
    return await calc.calculate(jurisdiction=jurisdiction, unit_count=unit_count)


# ---------------------------------------------------------------------------
# Stakeholders (CRUD placeholders)
# ---------------------------------------------------------------------------


@app.post("/api/v1/stakeholders", response_model=StakeholderResponse, status_code=201)
async def create_stakeholder(data: StakeholderCreate) -> dict:
    """Register a new stakeholder profile."""
    now = datetime.now(timezone.utc)
    return {
        "id": str(uuid.uuid4()),
        **data.model_dump(),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }


@app.get("/api/v1/stakeholders/{stakeholder_id}", response_model=StakeholderResponse)
async def get_stakeholder(stakeholder_id: uuid.UUID) -> dict:
    raise HTTPException(status_code=404, detail="Stakeholder not found")


# ---------------------------------------------------------------------------
# Campaigns (CRUD placeholders)
# ---------------------------------------------------------------------------


@app.post("/api/v1/campaigns", response_model=CampaignResponse, status_code=201)
async def create_campaign(data: CampaignCreate) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "id": str(uuid.uuid4()),
        **data.model_dump(),
        "status": "planning",
        "total_touches": 0,
        "current_step": 0,
        "start_date": None,
        "end_date": None,
        "created_at": now.isoformat(),
    }
