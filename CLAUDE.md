# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

This is the **Jawafdehi meta-repository** — a civic tech platform promoting transparency and accountability in Nepali governance. It serves as an open database of corruption for Nepal. All services are git submodules under `services/`.

- **Live**: https://jawafdehi.org (beta: https://beta.jawafdehi.org)
- **Project Board**: https://trello.com/b/zSNsFJvU/jawafdehiorg

## Repository Architecture

All application services are git submodules. This repo itself holds only cross-cutting documentation, specs, and tooling.

**Service dependencies:**
- `jawafdehi-frontend` → `jawafdehi-api` (backend)
- `jawafdehi-api` → `nes` (entity data)
- `nes-tundikhel` → `nes` (entity explorer)

| Service | Stack | Purpose |
|---------|-------|---------|
| `services/jawafdehi-api` | Django 5.2+, DRF, PostgreSQL, Poetry | Core accountability API |
| `services/jawafdehi-frontend` | React 18, TypeScript, Vite, Bun | Public-facing website |
| `services/nes` | Python, Poetry | Nepal entity database |
| `services/nes-tundikhel` | React, TypeScript, Vite | NES explorer UI |
| `services/nes-assets` | Jekyll | NES static assets site |
| `services/infra` | Terraform, GCP | Infrastructure as Code (git submodule) |
| `services/ngm` | — | Nepal governance module |

**Additional submodules:**
- `docs/admin` — admin documentation (GitLab: `damodardahal/newnepal-admin`)

**NES database note**: The actual database lives in `services/nes/nes-db/v2/` — it is large, so minimize read operations and never write to it via CLI.

## Submodule Setup

```bash
# Mount only the services you need
git submodule update --init services/jawafdehi-api services/jawafdehi-frontend services/nes

# Set up a Python service
cd services/jawafdehi-api
poetry install
cp .env.example .env

# Set up a TypeScript service
cd services/jawafdehi-frontend
bun install
cp .env.example .env

# Update a service to latest
cd services/jawafdehi-api && git pull origin main && cd ../..
git add services/jawafdehi-api && git commit -m "Update jawafdehi-api to latest"
```

## Commands by Service

### jawafdehi-api (Django)
```bash
cd services/jawafdehi-api
poetry run python manage.py runserver
poetry run python manage.py migrate
poetry run python manage.py makemigrations
poetry run pytest                          # run all tests
poetry run pytest tests/path/test_foo.py  # run a single test file
poetry run black . && poetry run isort .  # format code
```

### jawafdehi-frontend (React)
```bash
cd services/jawafdehi-frontend
bun run dev       # dev server
bun test          # run tests
bun run build     # production build
bun run lint      # lint
```

### nes (Nepal Entity Service)
```bash
cd services/nes
poetry run pytest
poetry run nes-api          # production API server → http://localhost:8080
poetry run nes-dev          # dev server (auto-reload) → http://localhost:8195
poetry run black . && poetry run isort .
```

**NES submodule setup**: `nes-db` is itself a submodule inside `nes`. Initialize it separately:
```bash
cd services/nes
git submodule update --init nes-db
```

**nes-tundikhel environment**: uses localStorage key `nes_tundikhel_environment` (`PRODUCTION` or `LOCAL`).
Local points to `http://localhost:8080` (matches `nes-api`). Switch via browser console:
```javascript
localStorage.setItem('nes_tundikhel_environment', 'LOCAL'); location.reload();
```

### Infrastructure
```bash
cd services/infra
terraform init
terraform plan
terraform apply
```

## Key Rules

- **Python services**: Always use `poetry run <command>` — never use pip directly; target Python 3.12+
- **TypeScript services**: Use Bun as runtime and package manager; Vite as build tool
- **Formatters**: black + isort (Python), ESLint (TypeScript)
- **Testing**: pytest with hypothesis (Python), vitest (TypeScript)
- **Infrastructure**: GCP (Cloud Run + Cloud Build); IaC via Terraform in `services/infra/` (git submodule)
- **Each service has its own AGENTS.md** — read it before making changes to that service

## Spec-Driven Development

Before implementing non-trivial features, check `.kiro/specs/` for existing specifications. Each spec has `requirements.md`, `design.md`, and `tasks.md`. Create a new spec directory if none exists for the feature.

## Nepali Context Requirements

- Use **authentic Nepali names** in all examples, fixtures, and test data
- Support **bilingual content** equally (English and Nepali)
- Maintain **WCAG 2.1 AA** accessibility compliance across all services
- Consider local governance structures in system design

## Cross-Service Changes

For changes that affect multiple services, update in this order:
1. Backend first (`jawafdehi-api`, `nes`)
2. Frontend second (`jawafdehi-frontend`, `nes-tundikhel`)
3. Infrastructure last (`services/infra`)

Create one PR per service and link them in PR descriptions.

## Documentation Locations

- **Cross-cutting docs** (architecture, presentations, research): `docs/`
- **Service-specific docs**: `services/{service}/docs/`
- **Feature specs**: `.kiro/specs/{feature}/`
- **Experiments and POCs**: `laboratory/`
- **Case research materials**: `case-research/` (and `docs/case-research/`)
- **Multi-agent toolkit**: `agent-kit/`
- **Admin docs** (submodule): `docs/admin/`
