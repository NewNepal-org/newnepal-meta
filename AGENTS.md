# NewNepal.org Meta Repo

NewNepal.org is a civic tech organization building open digital infrastructure to empower Nepali citizens with transparent access to information about governance, corruption, and public entities. The organization operates three major platforms: Jawafdehi.org (open database of corruption and accountability cases), Nepal Entity Service/NES (comprehensive database of Nepali public entities including politicians, organizations, and government bodies), and Nepal Governance Modernization/NGM (judicial data collection and governance analysis from Nepal's court system). All platforms emphasize open source code, open data principles, bilingual support (English/Nepali), and complete audit trails to promote transparency and accountability in Nepali governance.

## What This Meta-Repo Is

This meta-repository serves as the central hub for the entire NewNepal.org ecosystem, consolidating all projects, services, infrastructure code, documentation, and research materials in one place.

> Repository: https://github.com/NewNepal-org/newnepal-meta

By centralizing documentation and specifications across multiple services, the meta-repo provides a single source of truth that streamlines agentic development and AI-assisted coding workflows. This architecture enables efficient collaboration, consistent standards, and seamless integration across all NewNepal.org platforms.

## NewNepal.org Projects

NewNepal.org consists of three major projects, each with their own subcomponents:

1. **Jawafdehi.org** - Open database of corruption and accountability
   - **Live Platform**: https://jawafdehi.org
   - Services: `jawafdehi-api`, `jawafdehi-frontend`

2. **NES (Nepal Entity Service)** - Comprehensive database of Nepali public entities (persons, organizations)
   - Services: `nes`, `nes-tundikhel`, `nes-assets`

3. **NGM (Nepal Governance Modernization)** - Governance monitoring and analysis
   - Services: `ngm`

4. **NewNepal.org Website** - Main organizational website
   - Service: `newnepal-website`

## Key Paths

```
/
├── .kiro/                  # Kiro IDE configuration (meta-repo level)
│   ├── specs/              # Feature specifications (shared)
│   └── steering/           # AI steering rules (shared)
├── .amazonq/               # Amazon Q configuration
│   └── rules/              # Amazon Q rules
├── .cursor/                # Cursor IDE configuration
│   └── rules/              # Cursor rules
├── .github/                # GitHub configuration (workflows, templates)
│
├── services/               # All application services (independent repositories)
│   ├── jawafdehi-api/      # Django accountability API
│   ├── jawafdehi-frontend/ # React public frontend
│   ├── nes/                # Nepal entity database
│   ├── nes-tundikhel/      # NES explorer UI
│   ├── nes-assets/         # NES static assets
│   ├── newnepal-website/   # NewNepal.org main website
│   └── infra/              # Infrastructure as Code (independent repository)
│       ├── terraform/      # Terraform configuration
│       └── misc/           # Build configs and scripts
│
├── docs/                   # Meta-repo documentation (cross-cutting concerns)
├── case-research/          # Case research materials
├── laboratory/             # Experimental code and toolkits
└── tools/                  # Shared development tools

Note: Services are independent repositories. Clone them into the services/ directory as needed.
For full details on repository setup and selective cloning, see docs/GETTING_STARTED.md.
Each service also has its own docs/ folder for service-specific documentation.
```

## Selective Service Cloning

Services in this meta-repo are organized as independent repositories. Clone only what you need:

```bash
# Clone meta-repo (documentation and shared resources)
git clone git@github.com:NewNepal-org/newnepal-meta.git

# Clone specific service(s) into services/ directory
cd newnepal-meta/services
git clone git@github.com:NewNepal-org/JawafdehiAPI.git jawafdehi-api
git clone git@github.com:NewNepal-org/NepalEntityService.git nes

# Or clone all services
git clone git@github.com:NewNepal-org/JawafdehiAPI.git jawafdehi-api
git clone git@github.com:NewNepal-org/Jawafdehi.git jawafdehi-frontend
git clone git@github.com:NewNepal-org/NepalEntityService.git nes
git clone git@github.com:NewNepal-org/NepalEntityService-tundikhel.git nes-tundikhel
git clone git@github.com:NewNepal-org/NepalEntityService-assets.git nes-assets
git clone git@github.com:NewNepal-org/newnepal-website.git newnepal-website
git clone git@github.com:NewNepal-org/ngm.git ngm
git clone git@github.com:NewNepal-org/GCP-deployment.git infra
```

For complete setup instructions, dependency management, and development workflows, see `docs/GETTING_STARTED.md`.

## Documentation Organization

The `/docs` folder contains cross-cutting documentation for the entire NewNepal.org ecosystem:

**TODO**: Document the complete structure and organization of the `/docs` folder.

## Non-Negotiable Rules

### Code Quality & Standards
- **Python services** - Use Poetry: `poetry run <command>` (never pip)
- **TypeScript services** - Use Bun runtime with Vite build tool
- **Unit testing heavily emphasized** - Comprehensive test coverage required for both frontend and backend code
- **Testing frameworks** - pytest with hypothesis (Python), vitest (TypeScript)
- **Format consistently** - black + isort (Python), ESLint (TypeScript)
- **NEVER commit or view .env files** - Do not commit OR view `.env` files for ANY purposes whatsoever; use `.env.example` templates only
- **Nepali context** - Use authentic Nepali names in examples, fixtures, and documentation with bilingual support (English/Nepali) where possible

### Documentation & Specifications
- **Specs as source of truth** - Documentation updates take higher priority than code changes
- **Spec-driven development** - Use `.kiro/specs/` for non-trivial features
- **Open source principles** - All code follows open source best practices and licensing
- **Community collaboration** - Transparent development process with public repositories
- **Open data principles** - All case data must remain open and accessible
- **Complete audit trails** - Maintain version history for transparency

### Architecture Principles
- **Meta-repo structure** - Multiple independent service repositories
- **Work from meta-repo** - Users are expected to always work from the meta-repo, cloning only the services they need
- **Clone missing services** - If a particular service is needed but doesn't exist locally, clone it: `cd services && git clone git@github.com:NewNepal-org/<repo-name>.git <service-name>`
- **Service independence** - Each service has own dependencies, config, and secrets management
- **Shared infrastructure** - Common IaC in `services/infra/` (independent repository)
- **Selective cloning** - Clone only the services you need

## Expected Workflow

### For New Features
1. **Check existing specs** - Look in `.kiro/specs/` first
2. **Create spec if missing** - Use requirements.md, design.md, tasks.md structure
3. **Identify target service** - Work within appropriate service directory
4. **Write unit tests** - Test-driven development for all new features

### For Cross-Service Changes
1. **Plan at meta-repo level** - Consider impact across services
2. **Update shared infrastructure** - Modify `services/infra/` if needed (independent repository)
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

## Services Overview

| Service | Type | Stack | Description |
|---------|------|-------|-------------|
| **jawafdehi-api** | Backend | Django, DRF, PostgreSQL, Poetry | Core accountability API |
| **jawafdehi-frontend** | Frontend | React, TypeScript, Vite, Bun | Public-facing website |
| **nes** | Backend | Python, Poetry | Nepal entity database |
| **nes-tundikhel** | Frontend | React, TypeScript, Vite | NES explorer UI |
| **nes-assets** | Static | Jekyll | NES static assets site |
| **newnepal-website** | Frontend | React, TypeScript, Docusaurus | NewNepal.org main website |

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
- **Runtime**: Bun (CloudFlare)
- **Testing**: Vitest

### Infrastructure
- **Platform**: Google Cloud Platform
- **Compute**: Cloud Run
- **IaC**: Terraform
- **CI/CD**: Cloud Build

### External Integrations
- **PostgreSQL** - Primary database for all services
- **Google Cloud Storage** - File storage and static assets
- **Nepal Entity Service** - Government entity data

## Development Guidelines

### Service Selection
- **Jawafdehi corruption cases** → Work in `services/jawafdehi-api/`
- **Jawafdehi public website** → Work in `services/jawafdehi-frontend/`
- **Entity management** → Work in `services/nes/`
- **NewNepal.org website** → Work in `services/newnepal-website/`
- **Infrastructure changes** → Work in `services/infra/` (independent repository)

### Cross-Service Coordination
- **API changes** → Update both backend and frontend services
- **Database schema** → Consider impact on all consuming services
- **Authentication** → Coordinate across all user-facing services
- **Cross-platform features** → Consider impact across Jawafdehi, NES, and NGM

### Quality Assurance
- **Test at service level** → Each service has comprehensive test suite
- **Integration testing** → Test service interactions
- **End-to-end testing** → Test complete user workflows

---

*For service-specific development patterns and commands, refer to each service's README.md or documentation.*