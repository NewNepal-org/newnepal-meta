# Jawafdehi - Nepal Transparency & Accountability Platform

## What This Meta-Repo Is

Jawafdehi is a comprehensive civic tech platform promoting transparency and accountability in Nepali governance. This meta-repository contains the complete ecosystem including multiple services, infrastructure code, documentation, and research materials for Nepal's open corruption database.

**Mission**: Serve as an open database of corruption for Nepal, helping citizens access information about allegations of corruption and misconduct by public entities.

**Live Platform**: https://jawafdehi.org (beta: https://beta.jawafdehi.org)

## Non-Negotiable Rules

### Security & Data Integrity
- **NEVER commit secrets** - Use `.env` files (gitignored) with `.env.example` templates
- **Open data principles** - All case data must remain open and accessible
- **Complete audit trails** - Maintain version history for transparency
- **Service isolation** - Each service manages its own secrets and configuration

### Code Quality Standards
- **Python services** - Use Poetry: `poetry run <command>` (never pip)
- **TypeScript services** - Use Bun runtime with Vite build tool
- **Testing required** - pytest (Python), vitest (TypeScript)
- **Format consistently** - black + isort (Python), ESLint (TypeScript)

### Nepali Context Requirements
- **Authentic Nepali names** in all examples, fixtures, and documentation
- **Bilingual support** - Equal treatment for English and Nepali content
- **WCAG 2.1 AA compliance** for accessibility across all services
- **Local governance awareness** in system design

### Architecture Principles
- **Monorepo structure** - Multiple independent services
- **Service independence** - Each service has own dependencies and config
- **Shared infrastructure** - Common IaC in `services/infra/` (git submodule)
- **Spec-driven development** - Use `.kiro/specs/` for non-trivial features

## Key Paths

```
/
├── .kiro/                  # Kiro IDE configuration (meta-repo level)
│   ├── specs/              # Feature specifications (shared)
│   └── steering/           # AI steering rules (shared)
│
├── services/               # All application services
│   ├── jawafdehi-api/      # Django accountability API
│   ├── jawafdehi-frontend/ # React public frontend
│   ├── nes/                # Nepal entity database
│   ├── nes-tundikhel/      # NES explorer UI
│   ├── nes-assets/         # NES static assets
│   └── infra/              # Infrastructure as Code (git submodule)
│       ├── terraform/      # Terraform configuration
│       └── misc/           # Build configs and scripts
│
├── docs/                   # Meta-repo documentation (cross-cutting concerns)
├── case-research/          # Case research materials
├── laboratory/             # Experimental code and toolkits
├── tools/                  # Shared development tools
└── agent-kit/              # Multi-agent documentation toolkit

Note: Each service also has its own docs/ folder for service-specific documentation.
```

## Expected Workflow

### For New Features
1. **Check existing specs** - Look in `.kiro/specs/` first
2. **Create spec if missing** - Use requirements.md, design.md, tasks.md structure
3. **Identify target service** - Work within appropriate service directory
4. **Follow service patterns** - Each service has its own AGENTS.md

### For Cross-Service Changes
1. **Plan at meta-repo level** - Consider impact across services
2. **Update shared infrastructure** - Modify `services/infra/` if needed (git submodule)
3. **Coordinate service changes** - Update multiple services consistently
4. **Test integration** - Verify service interactions

### For Research & Documentation
1. **Case research** - Use `case-research/` for investigation materials
2. **Experiments** - Use `laboratory/` for proof-of-concepts
3. **Meta-repo documentation** - Update `/docs/` for cross-cutting concerns (architecture, entities, presentations)
4. **Service documentation** - Update `services/{service}/docs/` for service-specific features and APIs

## Essential Commands

### Meta-Repo Management
```bash
# Navigate to specific service
cd services/jawafdehi-api
cd services/jawafdehi-frontend

# Infrastructure operations
cd services/infra
terraform plan
terraform apply

# Meta-repo documentation (cross-cutting concerns)
# Edit files in docs/ directory

# Service-specific documentation
cd services/jawafdehi-api/docs
cd services/nes/docs
```

### Service-Specific Commands
Each service has its own development commands. See individual service AGENTS.md files:

- **jawafdehi-api**: `services/jawafdehi-api/AGENTS.md`
- **jawafdehi-frontend**: `services/jawafdehi-frontend/AGENTS.md` 
- **nes**: `services/nes/AGENTS.md`

## Services Overview

| Service | Type | Stack | Description |
|---------|------|-------|-------------|
| **jawafdehi-api** | Backend | Django, DRF, PostgreSQL, Poetry | Core accountability API |
| **jawafdehi-frontend** | Frontend | React, TypeScript, Vite, Bun | Public-facing website |
| **nes** | Backend | Python, Poetry | Nepal entity database |
| **nes-tundikhel** | Frontend | React, TypeScript, Vite | NES explorer UI |
| **nes-assets** | Static | Jekyll | NES static assets site |

## Technology Stack

### Backend Services
- **Language**: Python 3.12+
- **Framework**: Django 5.2+ with Django REST Framework
- **Database**: PostgreSQL
- **Package Manager**: Poetry
- **Testing**: pytest with hypothesis

### Frontend Services
- **Language**: TypeScript
- **Framework**: React 18
- **Build Tool**: Vite
- **Runtime**: Bun
- **Testing**: Vitest

### Infrastructure
- **Platform**: Google Cloud Platform
- **Compute**: Cloud Run
- **IaC**: Terraform
- **CI/CD**: Cloud Build

## Integration Architecture

### Service Dependencies
- **jawafdehi-frontend** → **jawafdehi-api** (backend)
- **jawafdehi-api** → **nes** (entity data)
- **nes-tundikhel** → **nes** (entity explorer)

### External Integrations
- **PostgreSQL** - Primary database for all services
- **Google Cloud Storage** - File storage and static assets
- **Nepal Entity Service** - Government entity data

## Development Guidelines

### Service Selection
- **New corruption cases** → Work in `services/jawafdehi-api/`
- **Public website features** → Work in `services/jawafdehi-frontend/`
- **Entity management** → Work in `services/nes/`
- **Infrastructure changes** → Work in `services/infra/` (git submodule)

### Cross-Service Coordination
- **API changes** → Update both backend and frontend services
- **Database schema** → Consider impact on all consuming services
- **Authentication** → Coordinate across all user-facing services

### Quality Assurance
- **Test at service level** → Each service has comprehensive test suite
- **Integration testing** → Test service interactions
- **End-to-end testing** → Test complete user workflows

---

*For service-specific guidance, always refer to the individual AGENTS.md file in each service directory. For project-wide context, see the agent-kit handbook.*