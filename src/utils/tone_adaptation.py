"""Tone adaptation — adjust generated content for different audiences and channels."""

from __future__ import annotations

from typing import Any

import yaml
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"


def load_tone_guidelines() -> dict[str, Any]:
    """Load audience-specific tone guidelines from YAML config."""
    path = CONFIG_DIR / "tone_guidelines.yaml"
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {}


def adapt_tone(text: str, audience: str, channel: str = "default") -> str:
    """Rewrite *text* with audience- and channel-appropriate tone adjustments.

    This applies rule-based substitutions; for deeper rewrites, pass the text
    through the LLM with the relevant system prompt.
    """
    guidelines = load_tone_guidelines()
    audience_rules: dict[str, str] = guidelines.get("audiences", {}).get(audience, {})
    channel_rules: dict[str, str] = guidelines.get("channels", {}).get(channel, {})

    for old, new in audience_rules.items():
        text = text.replace(old, new)
    for old, new in channel_rules.items():
        text = text.replace(old, new)

    return text


def get_reading_level(text: str) -> dict[str, float]:
    """Return Flesch-Kincaid readability metrics for the text."""
    try:
        import textstat

        return {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "gunning_fog": textstat.gunning_fog(text),
        }
    except ImportError:
        return {"error": "textstat not installed"}
