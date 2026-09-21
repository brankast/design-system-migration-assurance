from pathlib import Path

from agents.pipeline import run_pipeline

SAMPLE = Path("data/releases/angular-components-CHANGELOG.sample.md")


def test_pipeline_flags_demo_consumer_usages():
    assessment = run_pipeline(
        changelog_path=SAMPLE,
        fetch=False,
        apply_patches=False,
        create_pr=False,
        from_version="21.0.0",
        to_version="22.0.0",
    )
    assert assessment.prRequired
    assert assessment.summary
    apis = {usage.matchedApi for usage in assessment.usages}
    assert "checkboxPosition" in apis
    assert 'appearance="legacy"' in apis
    assert "event" not in apis
