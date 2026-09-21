from __future__ import annotations

from pathlib import Path

from agents.models import ChangeEvent, Impact, ProposedPatch
from agents.paths import repo_root


def propose_patches(
    events: list[ChangeEvent],
    impacts: list[Impact],
    *,
    apply: bool = False,
) -> list[ProposedPatch]:
    by_id = {event.id: event for event in events}
    patches: list[ProposedPatch] = []
    for impact in impacts:
        if impact.action != "patch":
            continue
        event = by_id.get(impact.changeId)
        if not event or not event.affectedApi or not event.replacement:
            continue
        find = _search_token(event.affectedApi)
        replace = event.replacement
        if find == replace or len(find) < 4:
            continue
        evidence = event.evidence or event.description
        for usage in impact.usages:
            path = repo_root() / usage.file
            if not path.exists():
                continue
            original = path.read_text(encoding="utf-8")
            if find not in original:
                continue
            patch = ProposedPatch(
                file=usage.file,
                description=f"Replace `{find}` with `{replace}` from changelog evidence.",
                find=find,
                replace=replace,
                sourceEvidence=evidence,
                applied=False,
            )
            if apply:
                updated = original.replace(find, replace)
                if updated != original:
                    path.write_text(updated, encoding="utf-8")
                    patch.applied = True
            patches.append(patch)
    return _dedupe(patches)


def _search_token(affected_api: str) -> str:
    if "." in affected_api:
        return affected_api.split(".")[-1]
    return affected_api


def _dedupe(patches: list[ProposedPatch]) -> list[ProposedPatch]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[ProposedPatch] = []
    for patch in patches:
        key = (patch.file, patch.find, patch.replace)
        if key in seen:
            continue
        seen.add(key)
        unique.append(patch)
    return unique
