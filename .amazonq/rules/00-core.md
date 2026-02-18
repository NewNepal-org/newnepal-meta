# Amazon Q Rules - NewNepal.org Meta-Repo

## About NewNepal.org
NewNepal.org is a civic tech organization building open digital infrastructure for transparency and accountability in Nepal. Three major platforms:
1. **Jawafdehi.org** - Open database of corruption and accountability
2. **NES (Nepal Entity Service)** - Comprehensive database of Nepali public entities
3. **NGM (Nepal Governance Modernization)** - Judicial data collection and governance analysis

## Meta-Repo Architecture
- **Work from meta-repo**: Always work from the meta-repo, cloning only needed services
- **Clone missing services**: `cd services && git clone git@github.com:NewNepal-org/<repo-name>.git <service-name>` (see README.md or AGENTS.md for mappings)
- Navigate to specific service directory before making changes
- Consider cross-service impact for API or schema changes (Jawafdehi, NES, NGM)
- Use shared infrastructure patterns in `services/infra/` (independent repository)
- Follow spec-driven development with `.kiro/specs/`

## Code Quality & Standards
- **Python services**: Use Poetry exclusively (`poetry run <command>`)
- **TypeScript services**: Use Bun runtime with Vite build tool
- **Unit testing heavily emphasized**: Comprehensive test coverage required for both frontend and backend
- **Testing frameworks**: pytest with hypothesis (Python), vitest (TypeScript)
- **Formatting**: black + isort (Python), ESLint (TypeScript)
- **NEVER commit or view .env files**: Do not commit OR view `.env` files for ANY purposes whatsoever; use `.env.example` templates only

## Nepali Context
- Use authentic Nepali names in examples, fixtures, and documentation with bilingual support (English/Nepali) where possible
- Consider local governance structures in system design

## Documentation & Specifications
- **Specs as source of truth**: Documentation updates take higher priority than code changes
- **Spec-driven development**: Use `.kiro/specs/` for non-trivial features
- **Open source principles**: All code follows open source best practices and licensing

## Service Coordination
- Services are independent repositories in `services/` directory
- Check individual service README.md for specific patterns
- Maintain API compatibility between frontend and backend
- Cross-platform features: Consider impact across Jawafdehi, NES, and NGM

See `AGENTS.md` for complete workflow and architecture details.