# Cursor Rules - Jawafdehi Meta-Repo

## Context
Nepal transparency platform meta-repository with multiple services. See `AGENTS.md` for complete context.

## Core Rules

### Service Navigation
- Navigate to specific service directory before making changes
- Each service has its own AGENTS.md with specific rules
- Use service-appropriate package managers (Poetry/Bun)

### Meta-Repo Patterns
- **Specs first**: Check `.kiro/specs/` before implementing features
- **Cross-service coordination**: Consider impact on all services
- **Infrastructure changes**: Work in `services/infra/` directory (git submodule)
- **Documentation**: Update `docs/` for project-wide changes

### Code Quality
- **Python**: `poetry run <command>`, black + isort formatting
- **TypeScript**: Bun runtime, ESLint, Vite build tool
- **Testing**: pytest (Python), vitest (TypeScript)
- **Nepali context**: Use authentic Nepali names in examples

### Security
- Never commit secrets or `.env` files
- Use `.env.example` templates

### Architecture
- Monorepo with independent services
- Shared infrastructure in `services/infra/` (git submodule)
- Service-specific dependencies and config
- Integration testing across services

Refer to individual service AGENTS.md files for service-specific guidance.