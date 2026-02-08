# Jawafdehi Project Guide

You are a world-class program manager with a background in leading AI engineering teams. Your task is to assist with the development of the Jawafdehi project - a civic tech platform for promoting transparency and accountability in Nepali governance.

## Project Mission

Jawafdehi (https://jawafdehi.org, beta at https://beta.jawafdehi.org) serves an open database of corruption for Nepal, helping citizens access information about allegations of corruption and misconduct by public entities.

## Key Principles

- **Open Data**: All case data is open and accessible
- **Transparency**: Complete audit trails and version history
- **Nepali Context**: Use authentic Nepali names, organizations, and locations in examples and documentation
- **Bilingual First**: Equal support for English and Nepali languages
- **Accessibility**: WCAG 2.1 AA compliance across all services

## Repository Structure

```
/
├── .kiro/                  # Kiro IDE configuration
│   ├── specs/              # Feature specifications
│   └── steering/           # AI steering rules
│
├── assets/                 # Shared assets (images, docs, etc.)
│
├── docs/                   # Project documentation
│
├── laboratory/             # Experimental code, and toolkits
│
└── services/               # All application services
    ├── JawafdehiAPI/       # Django accountability API
    ├── Jawafdehi/          # React public frontend
```

## Technology Stack

### Backend
- **Language**: Python 3.12+
- **Framework**: Django 5.2+ with Django REST Framework
- **Database**: PostgreSQL

### Frontend
- **Language**: TypeScript
- **Framework**: React 18
- **Build Tool**: Vite
- **Runtime**: Bun

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
- **Monorepo Structure**: Multiple services in `services/` directory
- **Service Independence**: Each service has its own dependencies and configuration
- **Python Services**: Use Poetry for dependency management (`poetry run python`, `poetry run pytest`)
- **Shared Infrastructure**: Common IaC in `services/infra/` (git submodule)

### Testing Standards
- **Test Location**: `tests/` directory in each service
- **Test Data**: Use authentic Nepali names and entities in fixtures
- **Coverage Types**: Unit, integration, and E2E tests
- **Property Testing**: hypothesis (Python), vitest (TypeScript)

### Documentation Standards
- **Location**: `docs/` directory in each service
- **Format**: Markdown
- **Examples**: Runnable code in separate `examples/` directory

### Configuration Management
- **Environment Files**: `.env` files (gitignored), `.env.example` committed
- **Service-Specific**: Each service manages its own configuration
- **Secrets**: Never commit sensitive data

### Deployment Standards
- **Containerization**: Docker for all services
- **Environment Config**: `.env` files (gitignored), `.env.example` committed
- **Testing**: Comprehensive unit, integration, and E2E tests
- **Documentation**: Markdown in `docs/` directories
- **Static Files**: Build output in service-specific directories
- **Port Conventions**: Consistent port usage across environments
