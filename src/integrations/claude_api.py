"""Anthropic Claude API integration for content generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import anthropic

from src.config import settings

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8")


class ClaudeContentGenerator:
    """Generates advocacy content using the Anthropic Claude API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.anthropic_model
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """Send a generation request and return the text response."""
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=temperature,
        )
        return message.content[0].text

    async def generate_policy_brief(
        self,
        friction_data: list[dict[str, Any]],
        jurisdiction: str,
        audience: str,
    ) -> str:
        system_prompt = _load_prompt("policy_brief_system_prompt.txt")
        system_prompt = system_prompt.replace("[AUDIENCE]", audience)

        user_prompt = (
            f"Generate a policy brief for {jurisdiction} targeting {audience}.\n\n"
            f"Friction data:\n{_format_friction_data(friction_data)}\n\n"
            "Please follow the structure outlined in the system prompt."
        )
        return await self.generate(system_prompt, user_prompt)

    async def generate_public_content(
        self,
        friction_data: list[dict[str, Any]],
        content_type: str,
        jurisdiction: str,
    ) -> str:
        system_prompt = _load_prompt("public_content_system_prompt.txt")

        user_prompt = (
            f"Generate a {content_type} about housing policy barriers in {jurisdiction}.\n\n"
            f"Friction data:\n{_format_friction_data(friction_data)}\n\n"
            "Make the content accessible and compelling for a general audience."
        )
        return await self.generate(system_prompt, user_prompt)

    async def generate_testimony(
        self,
        friction_data: list[dict[str, Any]],
        jurisdiction: str,
        time_limit_minutes: int = 3,
    ) -> str:
        system_prompt = _load_prompt("testimony_system_prompt.txt")

        user_prompt = (
            f"Generate testimony about housing barriers in {jurisdiction}.\n"
            f"Time limit: {time_limit_minutes} minutes.\n\n"
            f"Friction data:\n{_format_friction_data(friction_data)}\n\n"
            "Include personal impact framing and a clear policy recommendation."
        )
        return await self.generate(system_prompt, user_prompt)

    async def generate_alert_summary(
        self,
        changes: list[dict[str, Any]],
        stakeholder_context: dict[str, Any],
    ) -> str:
        system_prompt = _load_prompt("alert_generation_prompt.txt")

        user_prompt = (
            f"Generate a stakeholder alert for {stakeholder_context.get('organization', 'N/A')} "
            f"in {stakeholder_context.get('jurisdiction', 'N/A')}.\n\n"
            f"Changes:\n{_format_changes(changes)}\n\n"
            f"Stakeholder interests: {stakeholder_context.get('interests', [])}\n"
            f"Active projects: {stakeholder_context.get('projects', [])}"
        )
        return await self.generate(system_prompt, user_prompt, max_tokens=2048)


def _format_friction_data(data: list[dict[str, Any]]) -> str:
    lines = []
    for item in data:
        topic = item.get("topic", "Unknown")
        score = item.get("friction_score", "N/A")
        cost = item.get("estimated_cost", "N/A")
        lines.append(f"- {topic}: friction score {score}, estimated cost ${cost}")
    return "\n".join(lines) if lines else "No friction data available."


def _format_changes(changes: list[dict[str, Any]]) -> str:
    lines = []
    for change in changes:
        title = change.get("title", "Unknown change")
        source = change.get("source", "N/A")
        date = change.get("date", "N/A")
        lines.append(f"- [{date}] {title} (source: {source})")
    return "\n".join(lines) if lines else "No changes to report."
