# HousingSpeak

Advocacy & Communication Automation for the **HousingMind** ecosystem.

HousingSpeak translates regulatory intelligence from HousingLens and policy monitoring from HousingEar into targeted stakeholder communications, policy reform proposals, and public advocacy materials.

## Core Capabilities

- **Multi-Audience Translation** — Convert technical friction data into audience-appropriate narratives for PHAs, city councils, developers, and federal agencies.
- **Automated Advocacy** — Generate policy briefs, model ordinances, testimony drafts, and reform proposals.
- **Stakeholder Alerting** — Notify stakeholders of relevant Federal Register changes, emerging trends, and project-specific impacts.
- **Public Content** — Produce blog posts, op-eds, social media posts, and infographic data from friction analysis.
- **Comparative Analysis** — Benchmark jurisdictions against peers and surface best-practice policy examples.

## Tech Stack

| Layer | Technology |
|---|---|
| API | Python 3.11+ / FastAPI |
| Database | PostgreSQL (SQLAlchemy async) |
| Task Queue | Celery + Redis |
| LLM | Anthropic Claude API |
| Templates | Jinja2 |
| Email | SendGrid |
| CMS | WordPress REST API |

## Quick Start

```bash
# Clone and install
git clone <repo-url> && cd HousingSpeak
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env with your API keys

# Run the API server
uvicorn src.api.endpoints:app --reload

# Run with Docker
docker compose up -d
```

## Project Structure

```
HousingSpeak/
├── src/
│   ├── api/              # FastAPI endpoints, webhooks, review workflow
│   ├── generators/       # Content generators (policy briefs, alerts, testimony, etc.)
│   ├── integrations/     # HousingLens, HousingEar, Claude API clients
│   ├── models/           # SQLAlchemy models and Pydantic schemas
│   ├── analysis/         # Comparative analysis, impact calculator, peer matching
│   ├── distribution/     # Email, CMS, social media, Celery scheduler
│   ├── templates/        # Jinja2 HTML templates for content types
│   └── utils/            # Narrative construction, tone adaptation, fact checking
├── prompts/              # LLM system prompts for each content type
├── config/               # YAML configs (audience profiles, tone, distribution rules)
├── tests/                # pytest test suite (49 tests)
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/content/generate` | Generate content (policy brief, blog post, testimony, etc.) |
| `GET` | `/api/v1/content/{id}` | Retrieve generated content |
| `POST` | `/api/v1/content/{id}/review` | Submit review action (approve/reject) |
| `POST` | `/api/v1/reports/stakeholder` | Generate a tailored stakeholder report |
| `POST` | `/api/v1/alerts/generate` | Generate personalized stakeholder alerts |
| `POST` | `/api/v1/analysis/comparative` | Run comparative jurisdiction analysis |
| `GET` | `/api/v1/analysis/impact` | Calculate friction cost/timeline impact |
| `POST` | `/api/v1/stakeholders` | Register a stakeholder profile |
| `POST` | `/api/v1/campaigns` | Create an advocacy campaign |
| `POST` | `/api/v1/webhooks/housing-lens` | Webhook: HousingLens events |
| `POST` | `/api/v1/webhooks/housing-ear` | Webhook: HousingEar events |

## Content Types

- **Policy_Brief** — Data-driven reform recommendations for decision-makers
- **Stakeholder_Report** — Customized reports filtered by stakeholder interests
- **Blog_Post** — Accessible public advocacy content
- **Alert** — Time-sensitive notifications about policy changes
- **Model_Ordinance** — Draft legislative language adapted from peer jurisdictions
- **Testimony** — Spoken testimony drafts with timing guidance
- **Op_Ed** — Editorial-style opinion pieces
- **Social_Media** — Platform-specific posts (Twitter, LinkedIn)

## Review Workflow

Content is routed through appropriate review levels:

| Review Level | Content Types |
|---|---|
| Auto-publish | Routine alerts |
| Editor review | Blog posts, policy briefs, op-eds |
| Legal review | Model ordinances, testimony |
| Executive approval | High-stakes campaigns |

## Running Tests

```bash
pytest tests/ -v
```

## Configuration

- **`.env`** — API keys, database URLs, service credentials (see `.env.example`)
- **`config/audience_profiles.yaml`** — Audience definitions, tone preferences, reading levels
- **`config/tone_guidelines.yaml`** — Find-replace rules for audience/channel adaptation
- **`config/distribution_rules.yaml`** — Channel routing, scheduling, and rate limits

## Integration Points

### Inputs
- **HousingLens** — Friction scores, trend alerts, cost estimates
- **HousingEar** — Federal Register changes, meeting transcripts, policy updates

### Outputs
- **Email** (SendGrid) — Stakeholder alerts and digests
- **CMS** (WordPress) — Blog post publishing
- **Social Media** (Buffer) — Scheduled social posts
- **PDF** — Exportable policy briefs and reports

## License

MIT
