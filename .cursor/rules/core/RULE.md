# Cursor Rules - NewNepal.org Meta-Repo

## Context
NewNepal.org civic tech ecosystem meta-repository with multiple services across three major platforms:
1. **Jawafdehi.org** - Open database of corruption and accountability
2. **NES (Nepal Entity Service)** - Comprehensive database of Nepali public entities
3. **NGM (Nepal Governance Modernization)** - Judicial data collection and governance analysis

See `AGENTS.md` for complete context.

## Core Rules

### Service Navigation
- **Work from meta-repo**: Always work from the meta-repo, cloning only needed services
- **Clone missing services**: If needed, use `cd services && git clone git@github.com:NewNepal-org/<repo-name>.git <service-name>` (see README.md or AGENTS.md for mappings)
- Navigate to specific service directory before making changes
- Each service has its own README.md with specific patterns
- Use service-appropriate package managers (Poetry for Python, Bun for TypeScript)

### Meta-Repo Patterns
- **Specs first**: Check `.kiro/specs/` before implementing features
- **Specs as source of truth**: Documentation updates take higher priority than code changes
- **Cross-service coordination**: Consider impact across Jawafdehi, NES, and NGM
- **Infrastructure changes**: Work in `services/infra/` directory (independent repository)
- **Documentation**: Update `docs/` for project-wide changes, `services/{service}/docs/` for service-specific

### Code Quality & Standards
- **Python**: `poetry run <command>` (never pip), black + isort formatting
- **TypeScript**: Bun runtime, ESLint, Vite build tool
- **Unit testing heavily emphasized**: Comprehensive test coverage required for both frontend and backend
- **Testing frameworks**: pytest with hypothesis (Python), vitest (TypeScript)
- **Nepali context**: Use authentic Nepali names in examples, fixtures, and documentation with bilingual support (English/Nepali) where possible

### Security
- **NEVER commit or view .env files**: Do not commit OR view `.env` files for ANY purposes whatsoever
- Use `.env.example` templates only

### Architecture
- **Meta-repo structure**: Multiple independent service repositories
- **Service independence**: Each service has own dependencies, config, and secrets management
- **Shared infrastructure**: Common IaC in `services/infra/` (independent repository)
- **Selective cloning**: Clone only the services you need
- **Integration testing**: Test service interactions across platforms

### Open Source & Transparency
- All code follows open source best practices and licensing
- Open data principles - all case data must remain open and accessible
- Complete audit trails - maintain version history for transparency

Refer to `AGENTS.md` for detailed workflow and architecture guidance.