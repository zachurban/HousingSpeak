"""Shared test fixtures."""

from __future__ import annotations

import uuid

import pytest


@pytest.fixture
def sample_friction_data() -> list[dict]:
    return [
        {
            "topic": "Parking Requirements",
            "friction_score": 847,
            "estimated_cost": 47000,
            "delay_days": 180,
            "detail": "Minimum parking ratios exceed demand studies by 40%.",
        },
        {
            "topic": "Zoning Variances",
            "friction_score": 623,
            "estimated_cost": 32000,
            "delay_days": 120,
            "detail": "Variance approval requires three public hearings.",
        },
        {
            "topic": "Building Permits",
            "friction_score": 501,
            "estimated_cost": 18000,
            "delay_days": 90,
            "detail": "Average permit review takes 14 weeks.",
        },
        {
            "topic": "Impact Fees",
            "friction_score": 445,
            "estimated_cost": 25000,
            "delay_days": 30,
            "detail": "Fees increased 22% in the last two years.",
        },
        {
            "topic": "Design Review",
            "friction_score": 312,
            "estimated_cost": 12000,
            "delay_days": 60,
            "detail": "Subjective design standards create unpredictable timelines.",
        },
    ]


@pytest.fixture
def sample_stakeholder() -> dict:
    return {
        "id": str(uuid.uuid4()),
        "stakeholder_type": "PHA_Executive_Director",
        "organization": "Denver Housing Authority",
        "jurisdiction": "Denver, CO",
        "contact_name": "Jane Smith",
        "contact_email": "jsmith@denverha.org",
        "interests": ["VAWA", "Capital_Fund", "Voucher_Administration"],
        "notification_frequency": "weekly_digest",
        "notification_channels": ["email", "dashboard"],
        "alert_threshold": "medium",
        "projects": [
            {
                "project_id": "proj_123",
                "stage": "Pre-Entitlement",
                "location": "Denver, CO",
                "unit_count": 60,
            }
        ],
    }


@pytest.fixture
def sample_content() -> dict:
    return {
        "id": str(uuid.uuid4()),
        "content_type": "Policy_Brief",
        "audience": "City_Council",
        "jurisdiction": "Denver, CO",
        "headline": "Five Barriers Costing Denver Developers $8.2M Annually",
        "executive_summary": "Denver faces 5 significant friction areas.",
        "body": (
            "# Five Barriers Costing Denver Developers $8.2M Annually\n\n"
            "## Executive Summary\n"
            "Denver faces 5 significant regulatory friction areas, most "
            "critically in Parking Requirements, Zoning Variances, and "
            "Building Permits. Together, these add an estimated $134,000 "
            "in costs per project.\n\n"
            "## Problem Statement\n"
            "The friction score for Parking Requirements is 847, indicating "
            "severe barriers.\n\n"
            "## Recommendations\n"
            "1. Reduce minimum parking ratios\n"
            "2. Streamline variance process\n"
        ),
        "source_data": {
            "friction_scores": [847, 623, 501],
            "cost_estimates": [
                {"topic": "Parking Requirements", "estimated_cost": 47000},
            ],
        },
        "status": "draft",
        "generated_by": "policy_brief_generator_v1",
    }
