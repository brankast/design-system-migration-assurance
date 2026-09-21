from __future__ import annotations

from agents.models import ChangeEvent, ComponentUsage, Impact


def assess_impacts(
    events: list[ChangeEvent],
    usages: list[ComponentUsage],
) -> list[Impact]:
    impacts: list[Impact] = []
    for event in events:
        matched = [usage for usage in usages if _matches(event, usage)]
        if not matched:
            impacts.append(
                Impact(
                    changeId=event.id,
                    risk="none",
                    action="none",
                    usages=[],
                )
            )
            continue
        has_replacement = bool(event.replacement)
        action = "patch" if has_replacement else "review"
        risk = event.severity if event.severity in {"low", "medium", "high"} else "medium"
        uncertainty = None
        if not has_replacement:
            uncertainty = (
                "No documented replacement token was found in the changelog. "
                "A human must apply the migration path if one exists."
            )
        impacts.append(
            Impact(
                changeId=event.id,
                risk=risk,  # type: ignore[arg-type]
                action=action,  # type: ignore[arg-type]
                usages=matched,
                uncertainty=uncertainty,
            )
        )
    return impacts


def _matches(event: ChangeEvent, usage: ComponentUsage) -> bool:
    if usage.component == event.component and usage.matchedApi:
        if event.affectedApi and (
            usage.matchedApi == event.affectedApi
            or usage.matchedApi == event.affectedApi.split(".")[-1]
        ):
            return True
    if event.affectedApi and usage.matchedApi == event.affectedApi:
        return True
    if event.affectedApi and usage.matchedApi and event.affectedApi.endswith(usage.matchedApi):
        return True
    return False
