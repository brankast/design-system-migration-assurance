from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from agents.change_extractor import extract_change_events, latest_stable_version
from agents.changelog_tracker import (
    ChangelogDocument,
    fetch_changelog,
    load_changelog,
    load_seeded_release_events,
)
from agents.impact_assessor import assess_impacts
from agents.migration_proposer import propose_patches
from agents.models import Assessment, ChangeEvent
from agents.paths import (
    assessments_dir,
    changelog_cache_path,
    changelog_sample_path,
    cursor_state_path,
    latest_assessment_path,
)
from agents.pr_creator import (
    maybe_create_pull_request,
    write_assessment_json,
    write_report,
)
from agents.usage_scanner import scan_usages
from agents.versions import (
    previous_major_floor,
    read_installed_material_version,
    version_gt,
)


def run_pipeline(
    *,
    changelog_path: Path | None = None,
    from_version: str | None = None,
    to_version: str | None = None,
    fetch: bool = True,
    apply_patches: bool = False,
    create_pr: bool = False,
) -> Assessment:
    installed = read_installed_material_version()
    document = _load_document(changelog_path, fetch=fetch)
    latest = latest_stable_version(document.text) or installed
    start = from_version or previous_major_floor(installed)
    end = to_version or _max_version(installed, latest)

    extracted = extract_change_events(
        document,
        from_version=start,
        to_version=end,
    )
    seeded = [
        ChangeEvent.model_validate(item) for item in load_seeded_release_events()
    ]
    events = _merge_events(extracted, seeded)
    usages = scan_usages(events)
    impacts = assess_impacts(events, usages)
    patches = propose_patches(events, impacts, apply=apply_patches or create_pr)
    pr_required = any(impact.action != "none" for impact in impacts)
    summary = _summary(events, impacts, latest, installed)

    assessment = Assessment(
        library="Angular Material",
        installedVersion=installed,
        latestVersion=latest,
        fromVersion=start,
        toVersion=end,
        changelogSource=document.source,
        changeEvents=events,
        usages=usages,
        impacts=impacts,
        patches=patches,
        summary=summary,
        prRequired=pr_required,
    )

    assessments_dir().mkdir(parents=True, exist_ok=True)
    write_assessment_json(assessment, latest_assessment_path())
    report_path = assessments_dir() / "latest.md"
    write_report(assessment, report_path)
    _write_cursor(end)

    maybe_create_pull_request(
        assessment,
        report_path,
        create=create_pr,
    )
    return assessment


def load_latest_assessment() -> Assessment | None:
    path = latest_assessment_path()
    if not path.exists():
        return None
    return Assessment.model_validate_json(path.read_text(encoding="utf-8"))


def empty_assessment() -> Assessment:
    installed = read_installed_material_version()
    seeded = [
        ChangeEvent.model_validate(item) for item in load_seeded_release_events()
    ]
    return Assessment(
        library="Angular Material",
        installedVersion=installed,
        latestVersion=installed,
        fromVersion=previous_major_floor(installed),
        toVersion=installed,
        changelogSource="seeded-releases",
        changeEvents=seeded,
        summary="No changelog scan has been run yet.",
        prRequired=False,
    )


def _load_document(path: Path | None, *, fetch: bool) -> ChangelogDocument:
    if path:
        return load_changelog(path)
    if fetch:
        try:
            return fetch_changelog()
        except Exception:
            fallback = changelog_cache_path()
            if fallback.exists():
                return load_changelog(fallback)
            sample = changelog_sample_path()
            if sample.exists():
                return load_changelog(sample)
            raise
    for candidate in (changelog_cache_path(), changelog_sample_path()):
        if candidate.exists():
            return load_changelog(candidate)
    raise FileNotFoundError("No local changelog cache or sample is available.")


def _merge_events(
    extracted: list[ChangeEvent],
    seeded: list[ChangeEvent],
) -> list[ChangeEvent]:
    by_id = {event.id: event for event in extracted}
    for event in seeded:
        by_id.setdefault(event.id, event)
    return list(by_id.values())


def _max_version(left: str, right: str) -> str:
    return left if version_gt(left, right) else right


def _summary(
    events: list[ChangeEvent],
    impacts: list,
    latest: str,
    installed: str,
) -> str:
    affected = sum(1 for impact in impacts if impact.action != "none")
    return (
        f"Found {len(events)} documented Angular Material changes through {latest}. "
        f"{affected} change(s) match source usages in this repository. "
        f"Installed package version is {installed}."
    )


def _write_cursor(version: str) -> None:
    path = cursor_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "library": "angular-material",
        "lastProcessedVersion": version,
        "lastCheckedAt": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
