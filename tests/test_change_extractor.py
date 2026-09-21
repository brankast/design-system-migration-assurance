from pathlib import Path

from agents.change_extractor import extract_change_events, latest_stable_version
from agents.changelog_tracker import load_changelog

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "releases"
    / "angular-components-CHANGELOG.sample.md"
)


def changelog():
    return load_changelog(FIXTURE)


def test_latest_stable_version():
    assert latest_stable_version(changelog().text) == "22.0.0"


def test_extracts_material_list_breaking_change():
    events = extract_change_events(
        changelog(),
        from_version="21.0.0",
        to_version="22.0.0",
    )
    checkbox = next(
        event
        for event in events
        if event.affectedApi == "MatListOption.checkboxPosition"
    )
    assert checkbox.changeType == "removed"
    assert checkbox.replacement == "togglePosition"
    assert checkbox.migrationPath is not None
    assert "togglePosition" in checkbox.migrationPath
    assert checkbox.sourceUrl
    assert checkbox.evidence
    assert checkbox.confidence == "documented"


def test_extracts_renamed_symbol():
    events = extract_change_events(
        changelog(),
        from_version="21.0.0",
        to_version="22.0.0",
    )
    renamed = next(
        event
        for event in events
        if event.affectedApi == "MatListOptionCheckboxPosition"
    )
    assert renamed.replacement == "MatListOptionTogglePosition"


def test_skips_commit_tables():
    events = extract_change_events(
        changelog(),
        from_version="21.0.0",
        to_version="22.0.0",
    )
    assert all("gmp-click" not in event.description for event in events)


def test_prefers_specific_api_over_generic_words():
    events = extract_change_events(
        changelog(),
        from_version="21.0.0",
        to_version="22.0.0",
    )
    drop = next(event for event in events if "DropListRef" in (event.affectedApi or ""))
    assert drop.affectedApi == "DropListRef.drop"
    assert all(event.affectedApi != "event" for event in events)


def test_ignores_versions_outside_range():
    events = extract_change_events(
        changelog(),
        from_version="22.0.0",
        to_version="22.0.0",
    )
    assert events == []
