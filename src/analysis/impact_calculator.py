"""Impact calculator — quantify the financial and timeline cost of friction."""

from __future__ import annotations

from typing import Any

from src.integrations.housing_lens_client import HousingLensClient


class ImpactCalculator:
    """Translate friction scores into human-readable financial and timeline impacts."""

    def __init__(self) -> None:
        self.lens = HousingLensClient()

    async def calculate(
        self,
        jurisdiction: str,
        topics: list[str] | None = None,
        unit_count: int = 1,
    ) -> dict[str, Any]:
        """Return an impact summary for a jurisdiction."""
        friction = await self.lens.get_friction_scores(jurisdiction, topics)
        costs = await self.lens.get_cost_estimates(jurisdiction, topics)

        total_cost = sum(c.get("estimated_cost", 0) for c in costs)
        total_delay_days = sum(c.get("delay_days", 0) for c in costs)
        per_unit_cost = round(total_cost / unit_count, 2) if unit_count else total_cost

        top_cost_drivers = sorted(costs, key=lambda c: c.get("estimated_cost", 0), reverse=True)[
            :5
        ]

        return {
            "jurisdiction": jurisdiction,
            "total_estimated_cost": total_cost,
            "per_unit_cost": per_unit_cost,
            "total_delay_days": total_delay_days,
            "top_cost_drivers": top_cost_drivers,
            "friction_scores": friction,
            "narrative": _build_narrative(jurisdiction, total_cost, total_delay_days, top_cost_drivers),
        }


def _build_narrative(
    jurisdiction: str,
    total_cost: float,
    delay_days: int,
    drivers: list[dict[str, Any]],
) -> str:
    parts = [
        f"In {jurisdiction}, regulatory friction adds an estimated "
        f"${total_cost:,.0f} in costs and {delay_days} days of delay per project."
    ]
    if drivers:
        top = drivers[0]
        parts.append(
            f"The largest single cost driver is {top.get('topic', 'unknown')} "
            f"at ${top.get('estimated_cost', 0):,.0f}."
        )
    return " ".join(parts)
