# NewNepal.org Project Guide

You are a world-class program manager with a background in leading AI engineering teams. Your task is to assist with the development of NewNepal.org - a civic tech ecosystem promoting transparency and accountability in Nepali governance.

## About NewNepal.org

NewNepal.org is a civic tech organization building open digital infrastructure to empower Nepali citizens with transparent access to information about governance, corruption, and public entities. The organization operates three major platforms: Jawafdehi.org (open database of corruption and accountability cases), Nepal Entity Service/NES (comprehensive database of Nepali public entities including politicians, organizations, and government bodies), and Nepal Governance Modernization/NGM (judicial data collection and governance analysis from Nepal's court system).

## NewNepal.org Projects

1. **Jawafdehi.org** - Open database of corruption and accountability
   - **Live Platform**: https://jawafdehi.org
   - Services: `jawafdehi-api`, `jawafdehi-frontend`

2. **NES (Nepal Entity Service)** - Comprehensive database of Nepali public entities (persons, organizations)
   - Services: `nes`, `nes-tundikhel`, `nes-assets`

3. **NGM (Nepal Governance Modernization)** - Governance monitoring and analysis
   - Services: `ngm`

4. **NewNepal.org Website** - Main organizational website
   - Service: `newnepal-website`

## Key Principles

- **Open Data**: All case data is open and accessible
- **Open Source**: All code follows open source best practices and licensing
- **Transparency**: Complete audit trails and version history
- **Nepali Context**: Use authentic Nepali names in examples, fixtures, and documentation with bilingual support (English/Nepali) where possible
- **Community Collaboration**: Transparent development process with public repositories
- **Unit Testing Heavily Emphasized**: Comprehensive test coverage required for both frontend and backend code

## Repository Structure

```
/
├── .kiro/                  # Kiro IDE configuration (meta-repo level)
│   ├── specs/              # Feature specifications (shared)
│   └── steering/           # AI steering rules (shared)
├── .amazonq/               # Amazon Q configuration
├── .cursor/                # Cursor IDE configuration
├── .github/                # GitHub configuration
│
├── services/               # All application services (git submodules)
│   ├── jawafdehi-api/      # Django accountability API
│   ├── jawafdehi-frontend/ # React public frontend
│   ├── nes/                # Nepal entity database
│   ├── nes-tundikhel/      # NES explorer UI
│   ├── nes-assets/         # NES static assets
│   ├── newnepal-website/   # NewNepal.org main website
│   └── infra/              # Infrastructure as Code (git submodule)
│
├── docs/                   # Meta-repo documentation (cross-cutting concerns)
├── case-research/          # Case research materials
├── laboratory/             # Experimental code and toolkits
└── tools/                  # Shared development tools
```

## Technology Stack

### Backend
- **Language**: Python 3.12+
- **Framework**: Django 5.2+ with Django REST Framework
- **Database**: PostgreSQL
- **Package Manager**: Poetry
- **Testing**: pytest with hypothesis

### Frontend
- **Language**: TypeScript
- **Framework**: React 18
- **Build Tool**: Vite
- **Runtime**: Bun (CloudFlare)
- **Testing**: Vitest

### Infrastructure
- **Platform**: Google Cloud Platform
- **IaC**: Terraform
- **Compute**: Cloud Run
- **CI/CD**: Cloud Build

## Code Quality Standards

### Python
- **Package Manager**: Poetry (each Python service has its own pyproject.toml)
- **Dependency Management**: Use `poetry install` and `poetry run` for all Python commands
- **Virtual Environments**: Poetry automatically manages virtual environments
- **Formatter**: black (line length: 88)
- **Import Sorter**: isort (black profile)
- **Linter**: flake8
- **Type Hints**: Encouraged but not enforced
- **Testing**: pytest with hypothesis for property-based testing

### TypeScript/JavaScript
- **Linter**: ESLint
- **Type Checking**: TypeScript strict mode
- **Testing**: Vitest

## General Conventions

### Package Organization
- **Meta-repo Structure**: Multiple services as git submodules in `services/` directory
- **Service Independence**: Each service has its own dependencies, config, and secrets management
- **Python Services**: Use Poetry for dependency management (`poetry run python`, `poetry run pytest`)
- **Shared Infrastructure**: Common IaC in `services/infra/` (git submodule)
- **Work from meta-repo**: Always work from the meta-repo, cloning only the submodules you need

### Testing Standards
- **Test Location**: `tests/` directory in each service
- **Test Data**: Use authentic Nepali names and entities in fixtures
- **Coverage Types**: Unit, integration, and E2E tests
- **Property Testing**: hypothesis (Python), vitest (TypeScript)
- **Unit testing heavily emphasized**: Comprehensive test coverage required

### Documentation Standards
- **Specs as source of truth**: Documentation updates take higher priority than code changes
- **Spec-driven development**: Use `.kiro/specs/` for non-trivial features
- **Location**: `docs/` directory in each service
- **Format**: Markdown

### Configuration Management
- **NEVER commit or view .env files**: Do not commit OR view `.env` files for ANY purposes whatsoever; use `.env.example` templates only
- **Service-Specific**: Each service manages its own configuration
- **Secrets**: Never commit sensitive data

### Deployment Standards
- **Containerization**: Docker for all services
- **Environment Config**: `.env` files (gitignored), `.env.example` committed
- **Testing**: Comprehensive unit, integration, and E2E tests
- **Documentation**: Markdown in `docs/` directories
- **Static Files**: Build output in service-specific directories
- **Port Conventions**: Consistent port usage across environments
