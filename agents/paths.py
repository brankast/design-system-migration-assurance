from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def web_package_json() -> Path:
    return repo_root() / "apps" / "web" / "package.json"


def releases_dir() -> Path:
    return repo_root() / "data" / "releases"


def projects_dir() -> Path:
    return repo_root() / "data" / "projects"


def assessments_dir() -> Path:
    return repo_root() / "data" / "assessments"


def state_dir() -> Path:
    return repo_root() / "data" / "state"


def changelog_cache_path() -> Path:
    return releases_dir() / "angular-components-CHANGELOG.md"


def changelog_sample_path() -> Path:
    return releases_dir() / "angular-components-CHANGELOG.sample.md"


def latest_assessment_path() -> Path:
    return assessments_dir() / "latest.json"


def cursor_state_path() -> Path:
    return state_dir() / "changelog-cursor.json"
