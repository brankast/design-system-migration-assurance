from agents.impact_assessor import assess_impacts
from agents.migration_proposer import propose_patches
from agents.models import ChangeEvent, ComponentUsage


def test_applies_documented_replacement(tmp_path, monkeypatch):
    source = tmp_path / "checkout.html"
    source.write_text(
        '<mat-list-option checkboxPosition="before">Mail</mat-list-option>\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "agents.migration_proposer.repo_root",
        lambda: tmp_path,
    )

    event = ChangeEvent(
        id="list-checkbox-position",
        library="Angular Material",
        fromVersion="21.0.0",
        toVersion="22.0.0",
        component="MatListOption",
        changeType="removed",
        severity="high",
        description="`MatListOption.checkboxPosition` has been removed. use `togglePosition` instead.",
        affectedApi="MatListOption.checkboxPosition",
        replacement="togglePosition",
        evidence="`MatListOption.checkboxPosition` has been removed. use `togglePosition` instead.",
    )
    usage = ComponentUsage(
        project="demo",
        component="MatListOption",
        usageType="property",
        file="checkout.html",
        line=1,
        matchedApi="checkboxPosition",
    )
    impacts = assess_impacts([event], [usage])
    patches = propose_patches([event], impacts, apply=True)
    assert len(patches) == 1
    assert patches[0].applied
    assert "togglePosition" in source.read_text(encoding="utf-8")
    assert "checkboxPosition" not in source.read_text(encoding="utf-8")


def test_does_not_invent_replacement(tmp_path, monkeypatch):
    source = tmp_path / "form.html"
    source.write_text('<mat-form-field appearance="legacy"></mat-form-field>\n', encoding="utf-8")
    monkeypatch.setattr("agents.migration_proposer.repo_root", lambda: tmp_path)
    event = ChangeEvent(
        id="legacy-appearance",
        library="Angular Material",
        fromVersion="20",
        toVersion="21",
        component="MatFormField",
        changeType="breaking",
        severity="high",
        description="The legacy form field appearance is no longer supported.",
        affectedApi='appearance="legacy"',
        migrationPath="Replace the legacy appearance with a supported appearance.",
    )
    usage = ComponentUsage(
        project="demo",
        component="MatFormField",
        usageType="property",
        file="form.html",
        line=1,
        matchedApi='appearance="legacy"',
    )
    impacts = assess_impacts([event], [usage])
    patches = propose_patches([event], impacts, apply=True)
    assert patches == []
    assert 'appearance="legacy"' in source.read_text(encoding="utf-8")
