import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.pipeline import (  # noqa: E402
    empty_assessment,
    load_latest_assessment,
    run_pipeline,
)

app = FastAPI(
    title="Design System Migration Assurance API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    fetchChangelog: bool = True
    applyPatches: bool = False
    fromVersion: str | None = None
    toVersion: str | None = None
    changelogPath: str | None = Field(
        default=None,
        description="Optional local CHANGELOG.md path. Used in tests and offline runs.",
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "design-system-migration-assurance",
    }


@app.get("/assessments/latest")
def latest_assessment():
    assessment = load_latest_assessment()
    if assessment is None:
        assessment = empty_assessment()
    return assessment.model_dump()


@app.get("/changes")
def changes():
    assessment = load_latest_assessment() or empty_assessment()
    return assessment.changeEvents


@app.get("/usages")
def usages():
    assessment = load_latest_assessment() or empty_assessment()
    return assessment.usages


@app.post("/scan")
async def scan(request: ScanRequest | None = None):
    payload = request or ScanRequest()
    changelog = Path(payload.changelogPath) if payload.changelogPath else None
    assessment = await run_in_threadpool(
        run_pipeline,
        changelog_path=changelog,
        from_version=payload.fromVersion,
        to_version=payload.toVersion,
        fetch=payload.fetchChangelog,
        apply_patches=payload.applyPatches,
        create_pr=False,
    )
    return assessment.model_dump()
