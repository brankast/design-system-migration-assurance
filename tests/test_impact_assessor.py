from agents.impact_assessor import assess_impacts
from agents.models import ChangeEvent, ComponentUsage


def test_marks_review_when_replacement_is_missing():
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
        project="demo-consumer",
        component="MatFormField",
        usageType="property",
        file="data/projects/demo-consumer/src/checkout.html",
        line=4,
        matchedApi='appearance="legacy"',
        codeSnippet='<mat-form-field appearance="legacy">',
    )
    impacts = assess_impacts([event], [usage])
    assert impacts[0].action == "review"
    assert impacts[0].risk == "high"
    assert impacts[0].uncertainty


def test_marks_patch_when_changelog_has_replacement():
    event = ChangeEvent(
        id="list-checkbox-position",
        library="Angular Material",
        fromVersion="21.0.0",
        toVersion="22.0.0",
        component="MatListOption",
        changeType="removed",
        severity="high",
        description="removed",
        affectedApi="MatListOption.checkboxPosition",
        replacement="togglePosition",
    )
    usage = ComponentUsage(
        project="demo-consumer",
        component="MatListOption",
        usageType="property",
        file="checkout.html",
        line=1,
        matchedApi="checkboxPosition",
    )
    impacts = assess_impacts([event], [usage])
    assert impacts[0].action == "patch"
    assert impacts[0].uncertainty is None
