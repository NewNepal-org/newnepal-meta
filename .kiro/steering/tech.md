# Meta-Repo Technical Standards

## Service Navigation Rules

### Before Making Changes
- **Navigate to service directory** - Always `cd services/<service-name>` first
- **Check service README.md** - Each service has specific patterns and commands
- **Check service dependencies** - Use Poetry (Python) or Bun (TypeScript)
- **Work from meta-repo** - Always work from the meta-repo, cloning only the services you need

### Clone Missing Services
If a particular service is needed but doesn't exist locally:
```bash
cd services
git clone git@github.com:NewNepal-org/<repo-name>.git <service-name>
cd ..
```

Example mappings:
- jawafdehi-api → JawafdehiAPI.git
- jawafdehi-frontend → Jawafdehi.git
- nes → NepalEntityService.git
- nes-tundikhel → NepalEntityService-tundikhel.git
- nes-assets → NepalEntityService-assets.git
- ngm → ngm.git
- infra → GCP-deployment.git
- newnepal-website → newnepal-website.git

### Cross-Service Coordination
- **API changes** - Update both backend and frontend services
- **Database schema** - Consider impact on all consuming services
- **Authentication** - Coordinate across all user-facing services
- **Cross-platform features** - Consider impact across Jawafdehi, NES, and NGM

## Package Management

### Python Services
- **Poetry only** - Use `poetry run <command>` (never pip)
- **Service isolation** - Each service has own pyproject.toml
- **Virtual environments** - Poetry manages automatically

### TypeScript Services
- **Bun runtime** - Use Bun for package management and execution
- **Vite build tool** - For frontend applications
- **Service isolation** - Each service has own package.json

## Security & Configuration

### Environment Files
- **NEVER commit or view .env files** - Do NOT commit OR view `.env` files for ANY purposes whatsoever
- **Use .env.example only** - Provide templates without sensitive data
- **Service isolation** - Each service manages its own secrets and configuration

## Infrastructure Management

### Terraform Operations
```bash
cd services/infra
terraform init
terraform plan
terraform apply
```

### GCP Services
- **Cloud Run** - Container deployment
- **Cloud SQL** - PostgreSQL databases
- **Cloud Storage** - File storage and static assets
- **Cloud Build** - CI/CD pipelines

## Testing Strategy

### Unit Testing Heavily Emphasized
- **Comprehensive coverage** - Required for both frontend and backend code
- **Test-driven development** - Write tests for all new features

### Service-Level Testing
- **Unit tests** - Test individual components (pytest for Python, vitest for TypeScript)
- **Integration tests** - Test service interactions
- **API tests** - Test endpoint functionality

### Cross-Service Testing
- **End-to-end tests** - Test complete user workflows
- **Contract testing** - Verify API compatibility
- **Performance testing** - Load and stress testing

## Documentation & Specifications

### Specs as Source of Truth
- **Documentation priority** - Documentation updates take higher priority than code changes
- **Spec-driven development** - Use `.kiro/specs/` for non-trivial features
- **Check existing specs** - Look in `.kiro/specs/` before starting new features

## Essential Commands

### Meta-Repo Navigation
```bash
# Service-specific work
cd services/jawafdehi-api && poetry run python manage.py runserver
cd services/jawafdehi-frontend && bun run dev

# Infrastructure work
cd services/infra && terraform plan

# Documentation updates
# Edit files in docs/ directory for cross-cutting concerns
# Edit files in services/<service-name>/docs/ for service-specific docs
```

### Selective Cloning
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
git clone https://github.com/NewNepal-org/infra
```