from __future__ import annotations

import json
from pathlib import Path

import httpx

from agents.paths import changelog_cache_path, releases_dir

CHANGELOG_URL = (
    "https://raw.githubusercontent.com/angular/components/main/CHANGELOG.md"
)
SOURCE_URL = "https://github.com/angular/components/blob/main/CHANGELOG.md"
LIBRARY = "Angular Material"


class ChangelogDocument:
    def __init__(self, text: str, source: str) -> None:
        self.text = text
        self.source = source


def fetch_changelog(
    *,
    url: str = CHANGELOG_URL,
    cache_path: Path | None = None,
    timeout: float = 30.0,
    use_cache_on_failure: bool = True,
) -> ChangelogDocument:
    cache = cache_path or changelog_cache_path()
    try:
        response = httpx.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "design-system-migration-assurance"},
            follow_redirects=True,
        )
        response.raise_for_status()
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(response.text, encoding="utf-8")
        return ChangelogDocument(response.text, url)
    except httpx.HTTPError:
        if use_cache_on_failure and cache.exists():
            return ChangelogDocument(cache.read_text(encoding="utf-8"), str(cache))
        raise


def load_changelog(path: Path) -> ChangelogDocument:
    return ChangelogDocument(path.read_text(encoding="utf-8"), str(path))


def load_seeded_release_events() -> list[dict]:
    events: list[dict] = []
    directory = releases_dir()
    if not directory.exists():
        return events
    for path in sorted(directory.glob("*.json")):
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            events.extend(data)
        else:
            events.append(data)
    return events
