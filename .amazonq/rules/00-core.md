# Amazon Q Rules - Jawafdehi Meta-Repo

## Meta-Repo Architecture
- Navigate to specific service directory before making changes
- Consider cross-service impact for API or schema changes
- Use shared infrastructure patterns in `services/infra/` (git submodule)
- Follow spec-driven development with `.kiro/specs/`

## Code Correctness
- **Python services**: Use Poetry exclusively (`poetry run <command>`)
- **TypeScript services**: Use Bun runtime with Vite build tool
- **Testing**: pytest (Python) - comprehensive coverage
- **Formatting**: black + flake8 (Python), ESLint (TypeScript)

## Nepali Context
- Use authentic Nepali names in all examples and fixtures
- Support bilingual content (English/Nepali)
- Consider local governance structures in system design
- Maintain WCAG 2.1 AA accessibility compliance

## Service Coordination
- Services are located in services/<ServiceName>
- Check individual service AGENTS.md files for specific patterns
- Maintain API compatibility between frontend and backend

See `AGENTS.md` for complete workflow and architecture details.