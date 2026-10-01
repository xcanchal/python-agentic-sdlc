# SDLC Workbench

A small agentic workspace for moving software work through a structured SDLC.

The application uses specialized AI agents for each stage. The application controls the workflow. A human reviews and approves the output before work moves forward.

> Status: early development.

## Workflow

```text
Research
→ Definition
→ Design
→ Implementation
→ Verification
→ Done
```

Each stage consumes approved artifacts from previous stages and produces new artifacts.

Examples:

```text
Research        → RESEARCH_BRIEF
Definition      → PRD + ACCEPTANCE_CRITERIA
Design          → TECH_DESIGN + optional ADR / UX_SPEC / WIREFRAME
Implementation  → IMPLEMENTATION
Verification    → TEST_CASES + VERIFICATION_REPORT
```

The application is the orchestrator.

There is no LLM orchestrator in V1.

## Principles

- KISS
- YAGNI
- Human approval between stages
- Explicit artifacts
- Deterministic workflow
- Specialized agents
- Provider-independent application and domain layers

## Stack

### Backend

```text
Python 3.12
FastAPI
Uvicorn
asyncio
Pydantic
Pydantic Settings
SQLAlchemy 2 AsyncSession
asyncpg
Alembic
PostgreSQL
```

### Python tooling

```text
uv        dependency and environment management
Ruff      linting and formatting
Pyright   static type checking
pytest    tests
```

### Frontend

```text
React
TypeScript
Vite
```

The frontend is a SPA. SSR is not required.

## Async persistence

The backend uses:

```text
FastAPI
→ SQLAlchemy 2 AsyncSession
→ asyncpg
→ PostgreSQL
```

Alembic manages database schema migrations.

`asyncio` is part of Python and is not installed as a dependency.

## Repository structure

This repository is a simple monorepo.

```text
.
├── backend/
│   ├── src/
│   │   └── agentic_sdlc/
│   │       ├── main.py
│   │       ├── api/
│   │       ├── application/
│   │       ├── domain/
│   │       ├── infrastructure/
│   │       └── config/
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── compose.yaml
├── README.md
└── .gitignore
```

The repository root is the workspace.

```text
backend/
→ Python, FastAPI, uv, Ruff, Pyright, pytest

frontend/
→ React, TypeScript, Vite
```

No monorepo framework is required for V1.

Backend responsibilities:

```text
api
→ HTTP boundary

application
→ use-case orchestration

domain
→ business rules

infrastructure
→ database and external AI providers

config
→ runtime configuration and fixed stage definitions
```

## Development

Install Python 3.12 and `uv`.

### Backend

Run Python commands from `backend/`:

```bash
cd backend
uv sync
```

Run the API:

```bash
uv run uvicorn agentic_sdlc.main:app --reload
```

Run tests and checks:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

Add dependencies:

```bash
uv add <package>
uv add --dev <package>
```

### Frontend

Run frontend commands from `frontend/`:

```bash
cd frontend
npm install
npm run dev
```

Do not use Poetry, Black, Flake8, isort, or mypy unless the project gets a concrete need for them.

## V1 scope

V1 must support:

```text
create project
→ create work item
→ run current stage
→ save generated artifacts
→ review output
→ approve
→ move to next stage
→ inspect run and artifact history
```

The first vertical slice is smaller:

```text
create project
→ create work item
→ run ResearchAgent
→ save RESEARCH_BRIEF
→ review
→ approve
→ move to Definition
```

## V1 agents

```text
ResearchAgent
DefinitionAgent
DesignAgent
ImplementationAgent
VerificationAgent
```

Agents do not:

- choose the next stage;
- approve their own output;
- move work items;
- orchestrate other agents.

Generic subagents are not part of V1.

## Non-goals

V1 does not include:

```text
LLM orchestrator
generic subagent framework
RAG
vector database
MCP
GitHub integration
automatic repository editing
background queues
WebSockets
real-time collaboration
drag and drop
workflow builder
teams
billing
model routing
```

## Product specification

See [`sdlc-workbench-prd.md`](./sdlc-workbench-prd.md) for the full product and implementation brief.

## Development rule

Implement one small vertical slice at a time.

Before completing a backend iteration:

```bash
cd backend
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

Do not implement future requirements early.
