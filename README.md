# Design System Migration Assurance

AI-assisted, evidence-backed tooling for Angular Material breaking-change detection.

The system reads the official Angular Components changelog, extracts structured change events, finds affected source usages, and opens a **draft pull request** only when a change is necessary.

## Layout

- `apps/web` — Angular + Angular Material dashboard
- `apps/api` — FastAPI backend
- `agents` — changelog tracker, extractor, scanner, assessor, PR creator
- `data/projects/demo-consumer` — sample app still using removed Material APIs
- `docs/agents.md` — agent input/output contracts

## Run the dashboard

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn apps.api.main:app --reload
```

Terminal 2:

```bash
cd apps/web
npm start
```

Open `http://localhost:4200`. Use **Run changelog scan** to fetch the live Material changelog and refresh the assessment.

## Run the agent locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m agents run --no-fetch --changelog data/releases/angular-components-CHANGELOG.sample.md
```

That command scans this repo, writes `data/assessments/latest.json`, and reports whether a PR is required.

Create a draft PR (CI or a clean git checkout):

```bash
python -m agents run --create-pr
```

`--create-pr` applies **only** replacements the changelog states explicitly, such as `checkboxPosition` → `togglePosition`. If the changelog does not name a replacement, the PR lists the usage for human review.

## Tests

```bash
pytest
cd apps/web && npm test
```

## Scheduled watch

`.github/workflows/material-changelog.yml` runs every Monday, fetches the Angular Components changelog, and opens a draft PR when source usages are affected.
