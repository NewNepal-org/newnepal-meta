# GitHub Copilot Instructions - Jawafdehi Meta-Repo

## Primary Reference
Read `AGENTS.md` in the root directory for complete context and workflow.

## Meta-Repo Rules
- **Service-specific work** → Navigate to appropriate service directory first
- **Cross-service changes** → Consider impact on all services
- **Infrastructure changes** → Work in `services/infra/` directory (git submodule)
- **Specs first** → Check `.kiro/specs/` before implementing features

## Critical Standards
- **Python services**: Use `poetry run <command>` (never pip)
- **TypeScript services**: Use Bun runtime with Vite
- **Nepali context**: Use authentic Nepali names in examples
- **Security**: Never commit secrets, use `.env.example` templates
- **Testing**: pytest (Python), vitest (TypeScript)

## Service Navigation
```bash
cd services/jawafdehi-api       # Django backend
cd services/jawafdehi-frontend  # React frontend
cd services/nes                 # Entity database
cd services/infra               # Infrastructure (git submodule)
```

## Quick Commands
- Each service has its own AGENTS.md with specific commands
- Documentation: Edit files in docs/ directory

Refer to individual service AGENTS.md files for service-specific patterns and commands.