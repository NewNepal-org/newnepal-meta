# Meta-Repo Technical Standards

## Service Navigation Rules

### Before Making Changes
- **Navigate to service directory** - Always `cd services/<service-name>` first
- **Read service AGENTS.md** - Each service has specific patterns and commands
- **Check service dependencies** - Use Poetry (Python) or Bun (TypeScript)

### Cross-Service Coordination
- **API changes** - Update both backend and frontend services
- **Database schema** - Consider impact on all consuming services
- **Authentication** - Coordinate across all user-facing services

## Package Management

### Python Services
- **Poetry only** - Use `poetry run <command>` (never pip)
- **Service isolation** - Each service has own pyproject.toml
- **Virtual environments** - Poetry manages automatically

### TypeScript Services
- **Bun runtime** - Use Bun for package management and execution
- **Vite build tool** - For frontend applications
- **Service isolation** - Each service has own package.json

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

### Service-Level Testing
- **Unit tests** - Test individual components
- **Integration tests** - Test service interactions
- **API tests** - Test endpoint functionality

### Cross-Service Testing
- **End-to-end tests** - Test complete user workflows
- **Contract testing** - Verify API compatibility
- **Performance testing** - Load and stress testing

## Essential Commands

### Meta-Repo Navigation
```bash
# Service-specific work
cd services/jawafdehi-api && poetry run python manage.py runserver
cd services/jawafdehi-frontend && bun run dev

# Infrastructure work
cd services/infra && terraform plan

# Documentation updates
# Edit files in docs/ directory
```