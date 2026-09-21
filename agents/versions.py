from __future__ import annotations

import json
import re
from pathlib import Path

from agents.paths import web_package_json

VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$")
PACKAGE_NAME = "@angular/material"


def parse_version(value: str) -> tuple[int, int, int, str]:
    match = VERSION_RE.match(value.strip())
    if not match:
        raise ValueError(f"Unsupported version: {value}")
    pre = match.group(4) or ""
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)), pre)


def is_prerelease(value: str) -> bool:
    return bool(parse_version(value)[3])


def version_sort_key(value: str) -> tuple[int, int, int, int, str]:
    major, minor, patch, pre = parse_version(value)
    # Stable releases sort after pre-releases of the same number.
    return (major, minor, patch, 1 if pre else 2, pre)


def version_gt(left: str, right: str) -> bool:
    return version_sort_key(left) > version_sort_key(right)


def version_gte(left: str, right: str) -> bool:
    return version_sort_key(left) >= version_sort_key(right)


def version_in_range(value: str, from_version: str, to_version: str) -> bool:
    return version_gt(value, from_version) and version_gte(to_version, value)


def previous_major_floor(value: str) -> str:
    major, _, _, _ = parse_version(value)
    previous = max(major - 1, 0)
    return f"{previous}.0.0"


def npm_version_from_spec(spec: str) -> str:
    return spec.lstrip("^~>=< ")


def read_installed_material_version(package_json: Path | None = None) -> str:
    path = package_json or web_package_json()
    data = json.loads(path.read_text(encoding="utf-8"))
    spec = data.get("dependencies", {}).get(PACKAGE_NAME)
    if not spec:
        raise ValueError(f"{PACKAGE_NAME} is not listed in {path}")
    return npm_version_from_spec(spec)
