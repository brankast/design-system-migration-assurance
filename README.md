# Design System Migration Assurance

AI-powered tooling for detecting and assessing breaking changes in shared frontend component libraries.

## Goal

The system analyzes component library releases, extracts structured change events, identifies affected projects and source-code usages, assesses migration risk, and generates reviewable migration proposals.

## Architecture

- `apps/web` — Angular frontend
- `apps/api` — FastAPI backend
- `agents` — AI/agent workflows
- `packages` — shared schemas and utilities
- `data` — release notes and demo project data
- `docs` — architecture and project documentation
- `tests` — automated tests

## Development

### Frontend

```bash
cd apps/web
npm start