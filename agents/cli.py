from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agents.models import Assessment
from agents.pipeline import load_latest_assessment, run_pipeline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Track Angular Material changelog impact and propose migrations.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Fetch changelog, scan usages, and write an assessment.")
    _add_run_flags(run)

    scan = sub.add_parser("scan", help="Alias for run without creating a pull request.")
    _add_run_flags(scan)

    sub.add_parser("report", help="Print the latest assessment as JSON.")

    args = parser.parse_args(argv)
    if args.command == "report":
        assessment = load_latest_assessment()
        if assessment is None:
            print("No assessment has been generated yet. Run `python -m agents run`.")
            return 1
        print(json.dumps(assessment.model_dump(), indent=2))
        return 0

    changelog = Path(args.changelog) if getattr(args, "changelog", None) else None
    assessment = run_pipeline(
        changelog_path=changelog,
        from_version=args.from_version,
        to_version=args.to_version,
        fetch=not args.no_fetch,
        apply_patches=args.apply,
        create_pr=args.create_pr,
    )
    _print_summary(assessment)
    return 0


def _add_run_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--changelog", help="Local CHANGELOG.md path instead of GitHub.")
    parser.add_argument("--from-version", dest="from_version")
    parser.add_argument("--to-version", dest="to_version")
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Do not download the changelog; use a local file or cache.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply documented replacements in the working tree.",
    )
    parser.add_argument(
        "--create-pr",
        action="store_true",
        help="Create a draft GitHub PR when source usages are affected.",
    )


def _print_summary(assessment: Assessment) -> None:
    print(assessment.summary)
    print(f"PR required: {assessment.prRequired}")
    print(f"Changes: {len(assessment.changeEvents)}")
    print(f"Usages: {len(assessment.usages)}")
    print(f"Patches: {len(assessment.patches)}")


if __name__ == "__main__":
    sys.exit(main())
