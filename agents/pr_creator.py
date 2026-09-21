from __future__ import annotations

import json
import subprocess
from pathlib import Path

from agents.models import Assessment
from agents.paths import repo_root


class PrResult:
    def __init__(self, created: bool, url: str | None, reason: str) -> None:
        self.created = created
        self.url = url
        self.reason = reason


def maybe_create_pull_request(
    assessment: Assessment,
    report_path: Path,
    *,
    create: bool,
    repo: Path | None = None,
    extra_files: list[Path] | None = None,
) -> PrResult:
    if not create:
        return PrResult(False, None, "PR creation was not requested.")
    if not assessment.prRequired:
        return PrResult(False, None, "No affected usages require a pull request.")

    root = repo or repo_root()
    branch = _branch_name(assessment)
    title = (
        f"chore(material): review breaking changes through {assessment.toVersion}"
    )
    body = _pr_body(assessment, report_path)
    files = extra_files or _default_files(assessment, report_path)

    try:
        if _existing_pr(title, cwd=root):
            return PrResult(False, None, f"An open PR already exists: {title}")

        _run(["git", "checkout", "-B", branch], cwd=root)
        rel_files = [_relative(path, root) for path in files]
        rel_files = [path for path in rel_files if (root / path).exists()]
        if rel_files:
            _run(["git", "add", "--", *rel_files], cwd=root)
        status = _run(["git", "status", "--porcelain"], cwd=root)
        if not status.stdout.strip():
            return PrResult(False, None, "Working tree is clean; nothing to propose.")

        _run(["git", "commit", "-m", title], cwd=root)
        _run(["git", "push", "-u", "origin", branch], cwd=root)
        created = _run(
            [
                "gh",
                "pr",
                "create",
                "--draft",
                "--title",
                title,
                "--body",
                body,
            ],
            cwd=root,
        )
        url = created.stdout.strip() or None
        return PrResult(True, url, "Draft pull request created.")
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        return PrResult(False, None, f"Could not create pull request: {detail}")


def write_report(assessment: Assessment, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_markdown_report(assessment), encoding="utf-8")
    return path


def write_assessment_json(assessment: Assessment, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(assessment.model_dump(), indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def _default_files(assessment: Assessment, report_path: Path) -> list[Path]:
    files = [
        Path("data/assessments/latest.json"),
        Path("data/assessments/latest.md"),
        Path("data/state/changelog-cursor.json"),
        report_path,
    ]
    files.extend(Path(patch.file) for patch in assessment.patches if patch.applied)
    return files


def _relative(path: Path, root: Path) -> str:
    resolved = path if path.is_absolute() else root / path
    try:
        return str(resolved.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _branch_name(assessment: Assessment) -> str:
    safe = assessment.toVersion.replace(".", "-")
    return f"chore/material-breaking-changes-{safe}"


def _existing_pr(title: str, *, cwd: Path) -> bool:
    try:
        result = _run(
            [
                "gh",
                "pr",
                "list",
                "--state",
                "open",
                "--search",
                title,
                "--json",
                "title",
            ],
            cwd=cwd,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    try:
        rows = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return False
    return any(row.get("title") == title for row in rows)


def _run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
    )


def _pr_body(assessment: Assessment, report_path: Path) -> str:
    relative = report_path.as_posix()
    affected = [impact for impact in assessment.impacts if impact.action != "none"]
    lines = [
        "## Summary",
        "",
        assessment.summary,
        "",
        f"- Library: **{assessment.library}**",
        f"- Installed: `{assessment.installedVersion}`",
        f"- Changelog latest: `{assessment.latestVersion}`",
        f"- Range: `{assessment.fromVersion}` → `{assessment.toVersion}`",
        f"- Changelog source: {assessment.changelogSource}",
        f"- Affected changes: {len(affected)}",
        "",
        "## Human review required",
        "",
        "Generated patches are proposals. Do not merge until a reviewer confirms",
        "each replacement against the changelog evidence.",
        "",
        f"Full report: `{relative}`",
        "",
    ]
    return "\n".join(lines)


def _markdown_report(assessment: Assessment) -> str:
    lines = [
        f"# {assessment.library} changelog impact",
        "",
        assessment.summary,
        "",
        f"- Installed version: `{assessment.installedVersion}`",
        f"- Latest changelog version: `{assessment.latestVersion}`",
        f"- Analyzed range: `{assessment.fromVersion}` → `{assessment.toVersion}`",
        f"- Source: {assessment.changelogSource}",
        "",
        "## Affected usages",
        "",
    ]
    affected = [impact for impact in assessment.impacts if impact.usages]
    if not affected:
        lines.append("No source usages matched documented breaking or deprecated APIs.")
        lines.append("")
        return "\n".join(lines)

    for impact in affected:
        event = next(
            (item for item in assessment.changeEvents if item.id == impact.changeId),
            None,
        )
        if not event:
            continue
        lines.append(f"### {event.component} — `{event.affectedApi}`")
        lines.append("")
        lines.append(event.description)
        lines.append("")
        lines.append(f"- Change type: `{event.changeType}`")
        lines.append(f"- Severity: `{event.severity}`")
        lines.append(f"- Confidence: `{event.confidence}`")
        if event.migrationPath:
            lines.append(f"- Documented migration: {event.migrationPath}")
        if event.sourceUrl:
            lines.append(f"- Source: {event.sourceUrl}")
        if impact.uncertainty:
            lines.append(f"- Uncertainty: {impact.uncertainty}")
        lines.append("")
        lines.append("| File | Line | Snippet |")
        lines.append("| --- | --- | --- |")
        for usage in impact.usages:
            snippet = (usage.codeSnippet or "").replace("|", "\\|")
            lines.append(f"| `{usage.file}` | {usage.line} | `{snippet}` |")
        lines.append("")
    if assessment.patches:
        lines.append("## Proposed patches")
        lines.append("")
        for patch in assessment.patches:
            state = "applied" if patch.applied else "proposed"
            lines.append(
                f"- `{patch.file}`: `{patch.find}` → `{patch.replace}` ({state})"
            )
            lines.append(f"  - Evidence: {patch.sourceEvidence}")
        lines.append("")
    return "\n".join(lines)
