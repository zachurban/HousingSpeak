"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = (
        "postgresql+asyncpg://housingspeak:housingspeak@localhost:5432/housingspeak"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Anthropic Claude API
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # SendGrid
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "alerts@housingspeak.org"

    # HousingMind Ecosystem APIs
    housing_lens_api_url: str = "http://localhost:8001"
    housing_lens_api_key: str = ""
    housing_ear_api_url: str = "http://localhost:8002"
    housing_ear_api_key: str = ""

    # CMS
    cms_api_url: str = ""
    cms_username: str = ""
    cms_password: str = ""

    # Social Media
    buffer_api_key: str = ""

    # Content Settings
    default_review_required: bool = True
    auto_publish_digests: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
