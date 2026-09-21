from __future__ import annotations

import re
from pathlib import Path

from agents.models import ChangeEvent, ComponentUsage
from agents.paths import projects_dir, repo_root
from agents.tokens import is_distinctive_token

SCAN_EXTENSIONS = {".html", ".ts", ".scss", ".css"}
SKIP_DIRS = {
    "node_modules",
    ".angular",
    "dist",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "coverage",
}


def scan_usages(
    events: list[ChangeEvent],
    *,
    scan_roots: list[Path] | None = None,
) -> list[ComponentUsage]:
    roots = scan_roots or default_scan_roots()
    usages: list[ComponentUsage] = []
    files = _collect_files(roots)
    for event in events:
        needles = _needles_for(event)
        if not needles:
            continue
        for file_path in files:
            usages.extend(_scan_file(file_path, event, needles))
    return _dedupe(usages)


def default_scan_roots() -> list[Path]:
    roots = [repo_root() / "apps" / "web" / "src"]
    extra = projects_dir()
    if extra.exists():
        roots.append(extra)
    return roots


def _collect_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            files.append(root)
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix not in SCAN_EXTENSIONS:
                continue
            files.append(path)
    return files


def _needles_for(event: ChangeEvent) -> list[str]:
    needles: list[str] = []
    if event.affectedApi:
        needles.append(event.affectedApi)
        if "." in event.affectedApi:
            last = event.affectedApi.split(".")[-1]
            if is_distinctive_token(last):
                needles.append(last)
    if event.component.startswith("Mat"):
        selector = _mat_selector(event.component)
        if selector:
            needles.append(selector)
    unique: list[str] = []
    seen: set[str] = set()
    for needle in needles:
        if not needle or len(needle) < 4:
            continue
        if needle in seen:
            continue
        seen.add(needle)
        unique.append(needle)
    # Keep selector-only needles from matching every usage of a component.
    # Prefer API tokens; include selector only when no property-like API exists.
    api_like = [n for n in unique if not n.startswith("mat-")]
    if api_like:
        return api_like
    return unique


def _mat_selector(symbol: str) -> str | None:
    if not symbol.startswith("Mat"):
        return None
    rest = symbol[3:]
    if not rest or not rest[0].isupper():
        return None
    kebab = re.sub(r"(?<!^)([A-Z])", r"-\1", rest).lower()
    return f"mat-{kebab}"


def _scan_file(
    path: Path,
    event: ChangeEvent,
    needles: list[str],
) -> list[ComponentUsage]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    usages: list[ComponentUsage] = []
    relative = _relative_to_repo(path)
    project = _project_name(relative)
    for index, line in enumerate(text.splitlines(), start=1):
        for needle in needles:
            if not _line_has_needle(line, needle):
                continue
            usages.append(
                ComponentUsage(
                    project=project,
                    component=event.component,
                    usageType=_usage_type(needle, event),
                    file=relative,
                    line=index,
                    matchedApi=needle,
                    codeSnippet=line.strip()[:240],
                )
            )
            break
    return usages


def _line_has_needle(line: str, needle: str) -> bool:
    if is_distinctive_token(needle):
        return needle in line
    return re.search(rf"\b{re.escape(needle)}\b", line) is not None


def _usage_type(needle: str, event: ChangeEvent) -> str:
    if needle.startswith("mat-"):
        return "component"
    if needle.startswith("--") or needle.startswith("$"):
        return "token"
    if event.affectedApi and "." in event.affectedApi:
        return "property"
    return "property"


def _project_name(relative: str) -> str:
    parts = Path(relative).parts
    if len(parts) >= 2 and parts[0] == "apps":
        return parts[1]
    if len(parts) >= 3 and parts[0] == "data" and parts[1] == "projects":
        return parts[2]
    return parts[0] if parts else "unknown"


def _relative_to_repo(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root()))
    except ValueError:
        return str(path)


def _dedupe(usages: list[ComponentUsage]) -> list[ComponentUsage]:
    seen: set[tuple[str, int, str | None]] = set()
    unique: list[ComponentUsage] = []
    for usage in usages:
        key = (usage.file, usage.line, usage.matchedApi)
        if key in seen:
            continue
        seen.add(key)
        unique.append(usage)
    return unique
