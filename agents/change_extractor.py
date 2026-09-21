from __future__ import annotations

import re

from agents.changelog_tracker import SOURCE_URL, ChangelogDocument
from agents.models import ChangeEvent
from agents.tokens import pick_affected_api
from agents.versions import is_prerelease, version_in_range

VERSION_HEADER_RE = re.compile(
    r"^# (\d+\.\d+\.\d+(?:-[\w.]+)?)\b.*$",
    re.MULTILINE,
)
BACKTICK_RE = re.compile(r"`([^`]+)`")
USE_INSTEAD_RE = re.compile(
    r"(?i)\buse(?:s)?\s+`([^`]+)`\s+instead"
)
RENAMED_TO_RE = re.compile(
    r"(?i)renamed to\s+`([^`]+)`"
)
COMMIT_NOISE_RE = re.compile(r"^\s*\*\s*(feat|fix|refactor|docs)\(")


def extract_change_events(
    document: ChangelogDocument,
    *,
    from_version: str,
    to_version: str,
    include_prerelease: bool = False,
    library: str = "Angular Material",
) -> list[ChangeEvent]:
    events: list[ChangeEvent] = []
    sections = _split_versions(document.text)
    for version, body in sections:
        if not include_prerelease and is_prerelease(version):
            continue
        if not version_in_range(version, from_version, to_version):
            continue
        events.extend(
            _events_from_version(
                version=version,
                body=body,
                from_version=from_version,
                library=library,
                source=document.source or SOURCE_URL,
            )
        )
    return _dedupe(events)


def _split_versions(text: str) -> list[tuple[str, str]]:
    matches = list(VERSION_HEADER_RE.finditer(text))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group(1), text[start:end]))
    return sections


def latest_stable_version(text: str) -> str | None:
    for match in VERSION_HEADER_RE.finditer(text):
        version = match.group(1)
        if not is_prerelease(version):
            return version
    return None


def _events_from_version(
    *,
    version: str,
    body: str,
    from_version: str,
    library: str,
    source: str,
) -> list[ChangeEvent]:
    events: list[ChangeEvent] = []
    for heading, change_type, section in _change_sections(body):
        current_package = "material" if heading == "material" else heading
        for raw_line in _api_lines(section):
            event = _event_from_line(
                line=raw_line,
                version=version,
                from_version=from_version,
                library=library,
                source=source,
                change_type=change_type,
                package_name=current_package,
            )
            if event:
                events.append(event)
    return events


def _change_sections(body: str) -> list[tuple[str, str, str]]:
    sections: list[tuple[str, str, str]] = []
    breaking = _extract_named_section(body, "Breaking Changes")
    if breaking:
        sections.extend(_package_sections(breaking, "breaking"))
    deprecations = _extract_named_section(body, "Deprecations")
    if deprecations:
        sections.extend(_package_sections(deprecations, "deprecated"))
    return sections


def _extract_named_section(body: str, title: str) -> str | None:
    heading = f"## {title}"
    start = body.find(heading)
    if start < 0:
        return None
    start += len(heading)
    next_h2 = re.search(r"^## ", body[start:], re.MULTILINE)
    end = start + next_h2.start() if next_h2 else len(body)
    section = body[start:end]
    table = section.find("| Commit |")
    if table >= 0:
        section = section[:table]
    return section


def _package_sections(section: str, change_type: str) -> list[tuple[str, str, str]]:
    matches = list(re.finditer(r"^### ([^\n]+)$", section, re.MULTILINE))
    if not matches:
        return [("material", change_type, section)]
    packages: list[tuple[str, str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        packages.append((match.group(1).strip(), change_type, section[start:end]))
    return packages


def _api_lines(section: str) -> list[str]:
    lines: list[str] = []
    for raw in section.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("|"):
            continue
        if COMMIT_NOISE_RE.search(stripped):
            continue
        if stripped.startswith(("-", "*")):
            cleaned = stripped.lstrip("-* ").strip()
            if cleaned:
                lines.append(cleaned)
    return lines


def _event_from_line(
    *,
    line: str,
    version: str,
    from_version: str,
    library: str,
    source: str,
    change_type: str,
    package_name: str,
) -> ChangeEvent | None:
    symbols = BACKTICK_RE.findall(line)
    affected = pick_affected_api(symbols)
    if not affected:
        return None

    replacement = _replacement_from_line(line)
    component = _component_from_symbol(affected, package_name)
    severity = _severity(line, change_type)
    mapped_type = "removed" if "removed" in line.lower() else change_type
    migration = None
    if replacement:
        migration = f"Use `{replacement}` instead of `{affected}`."
    elif "instead" in line.lower() or "use " in line.lower():
        migration = line

    event_id = _make_id(library, version, component, affected)
    return ChangeEvent(
        id=event_id,
        library=library,
        fromVersion=from_version,
        toVersion=version,
        component=component,
        changeType=mapped_type,  # type: ignore[arg-type]
        severity=severity,
        description=line,
        affectedApi=affected,
        migrationPath=migration,
        sourceUrl=source,
        evidence=line,
        replacement=replacement,
        packageName=package_name,
        confidence="documented",
    )


def _replacement_from_line(line: str) -> str | None:
    match = USE_INSTEAD_RE.search(line) or RENAMED_TO_RE.search(line)
    if not match:
        return None
    return match.group(1).strip()


def _component_from_symbol(symbol: str, package_name: str) -> str:
    root = symbol.split(".")[0].split("(")[0].strip()
    if root.startswith("Mat") or root.startswith("CDK") or root.startswith("Cdk"):
        return root
    return root or package_name


def _severity(line: str, change_type: str) -> str:
    lowered = line.lower()
    if "removed" in lowered or change_type == "breaking":
        return "high"
    if change_type == "deprecated":
        return "medium"
    return "medium"


def _make_id(library: str, version: str, component: str, api: str) -> str:
    raw = f"{library}-{version}-{component}-{api}"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", raw).strip("-").lower()
    return slug[:140]


def _dedupe(events: list[ChangeEvent]) -> list[ChangeEvent]:
    seen: set[str] = set()
    unique: list[ChangeEvent] = []
    for event in events:
        if event.id in seen:
            continue
        seen.add(event.id)
        unique.append(event)
    return unique
