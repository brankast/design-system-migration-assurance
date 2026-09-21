# Agents

Each agent has one job. None of them should be merged into a general-purpose bot.

## changelog_tracker

- Input: GitHub changelog URL or a local markdown file
- Output: changelog text plus source URL
- Failure: uses the on-disk cache or `data/releases/angular-components-CHANGELOG.sample.md`

## change_extractor

- Input: changelog text and a version range
- Output: `ChangeEvent` objects with evidence, optional replacement, and source URL
- Constraint: only extract backtick-quoted APIs from Breaking Changes / Deprecations sections

## usage_scanner

- Input: change events and repository roots (`apps/web/src`, `data/projects`)
- Output: `ComponentUsage` rows with file, line, and snippet
- Constraint: no LLM; exact token search only

## impact_assessor

- Input: events + usages
- Output: risk, action (`none` | `review` | `patch`), and uncertainty when a replacement is missing

## migration_proposer

- Input: impacts whose action is `patch`
- Output: proposed find/replace pairs taken from changelog evidence
- Constraint: never invent a replacement such as mapping `legacy` to `outline`

## pr_creator

- Input: assessment + report files
- Output: draft GitHub PR when `prRequired` is true
- Constraint: generated patches stay proposals until a human reviews them
