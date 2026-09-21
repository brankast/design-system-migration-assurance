from agents.models import ChangeEvent
from agents.usage_scanner import scan_usages


def _event() -> ChangeEvent:
    return ChangeEvent(
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
        sourceUrl="https://github.com/angular/components/blob/main/CHANGELOG.md",
    )


def test_finds_checkbox_position_usage(tmp_path):
    source = tmp_path / "checkout.html"
    source.write_text(
        '<mat-list-option checkboxPosition="before">Mail</mat-list-option>\n',
        encoding="utf-8",
    )
    usages = scan_usages([_event()], scan_roots=[source])
    assert len(usages) == 1
    assert usages[0].line == 1
    assert usages[0].matchedApi == "checkboxPosition"


def test_does_not_match_unrelated_template(tmp_path):
    source = tmp_path / "ok.html"
    source.write_text("<mat-list-option>Mail</mat-list-option>\n", encoding="utf-8")
    usages = scan_usages([_event()], scan_roots=[source])
    assert usages == []


def test_does_not_match_generic_event_word(tmp_path):
    source = tmp_path / "nav.html"
    source.write_text("<span>Change events</span>\n", encoding="utf-8")
    event = ChangeEvent(
        id="drop-event",
        library="Angular Material",
        fromVersion="21.0.0",
        toVersion="22.0.0",
        component="DropListRef",
        changeType="breaking",
        severity="high",
        description="The event parameter of DropListRef.drop is now required.",
        affectedApi="DropListRef.drop",
    )
    assert scan_usages([event], scan_roots=[source]) == []
