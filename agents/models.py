from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ChangeType = Literal["breaking", "deprecated", "behavior", "removed", "migration"]
Severity = Literal["low", "medium", "high"]
UsageType = Literal["component", "property", "directive", "token"]
Risk = Literal["none", "low", "medium", "high"]
Action = Literal["none", "review", "patch"]
Confidence = Literal["documented", "inferred", "uncertain"]


class ChangeEvent(BaseModel):
    id: str
    library: str
    fromVersion: str
    toVersion: str
    component: str
    changeType: ChangeType
    severity: Severity
    description: str
    affectedApi: str | None = None
    migrationPath: str | None = None
    sourceUrl: str | None = None
    evidence: str | None = None
    replacement: str | None = None
    packageName: str | None = None
    confidence: Confidence = "documented"


class ComponentUsage(BaseModel):
    project: str
    component: str
    usageType: UsageType
    file: str
    line: int
    matchedApi: str | None = None
    codeSnippet: str | None = None


class Impact(BaseModel):
    changeId: str
    risk: Risk
    action: Action
    usages: list[ComponentUsage] = Field(default_factory=list)
    uncertainty: str | None = None


class ProposedPatch(BaseModel):
    file: str
    description: str
    find: str
    replace: str
    sourceEvidence: str
    applied: bool = False


class Assessment(BaseModel):
    library: str
    installedVersion: str
    latestVersion: str
    fromVersion: str
    toVersion: str
    changelogSource: str
    changeEvents: list[ChangeEvent] = Field(default_factory=list)
    usages: list[ComponentUsage] = Field(default_factory=list)
    impacts: list[Impact] = Field(default_factory=list)
    patches: list[ProposedPatch] = Field(default_factory=list)
    summary: str = ""
    prRequired: bool = False
