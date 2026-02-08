# Meta-Repo Structure Guide

## Repository Overview
Jawafdehi meta-repository containing multiple independent services for Nepal's transparency platform.

## Directory Structure

```
/
├── AGENTS.md               # Cross-tool entry point (meta-repo)
├── .kiro/                  # Kiro configuration (meta-repo level)
│   ├── specs/              # Feature specifications (shared)
│   └── steering/           # AI steering rules (shared)
│
├── services/               # All application services
│   ├── jawafdehi-api/      # Django accountability API
│   │   └── AGENTS.md       # Service-specific entry point
│   ├── jawafdehi-frontend/ # React public frontend
│   │   └── AGENTS.md       # Service-specific entry point
│   ├── nes/                # Nepal entity database
│   ├── nes-tundikhel/      # NES explorer UI
│   ├── nes-assets/         # NES static assets
│   └── infra/              # Infrastructure as Code (git submodule)
│       ├── terraform/      # Terraform configuration
│       └── misc/           # Build configs and scripts
│
├── docs/                   # Project documentation
├── case-research/          # Case research materials
├── laboratory/             # Experimental code and toolkits
├── tools/                  # Shared development tools
└── agent-kit/              # Multi-agent documentation toolkit
```

## Service Responsibilities

### JawafdehiAPI (Django Backend)
- Corruption case management
- User authentication and permissions
- RESTful API for frontend consumption
- Integration with Nepal Entity Service

### Jawafdehi (React Frontend)
- Public-facing website
- Case browsing and search
- User interface for transparency data
- Responsive design with accessibility

### NepalEntityService (Entity Database)
- Government entity data management
- Entity search and validation
- API for entity information
- Data scraping and updates
- The actual database is in the `nes-db/v2` folder in the service directory. It is quite large and we should be careful about the read operations we make. Write operations through CLI operations are forbidden.

### Infrastructure (services/infra - git submodule)
- Terraform configuration for GCP
- Container deployment setup
- Database provisioning
- CI/CD pipeline configuration

## Development Workflow

### Service-Specific Work
1. Navigate to service directory: `cd services/<service-name>`
2. Read service AGENTS.md for specific guidance
3. Use service package manager (Poetry/Bun)
4. Follow service testing patterns

### Cross-Service Work
1. Plan changes at meta-repo level
2. Consider impact on all affected services
3. Update multiple services consistently
4. Test service interactions

### Infrastructure Work
1. Navigate to services/infra directory (git submodule)
2. Use Terraform for infrastructure changes
3. Test in staging environment first
4. Coordinate with service deployments

## Key Integration Points

### API Dependencies
- jawafdehi-frontend → jawafdehi-api (case data)
- jawafdehi-api → nes (entity data)
- nes-tundikhel → nes (entity explorer)

### Shared Resources
- PostgreSQL databases (via Cloud SQL)
- File storage (via Cloud Storage)
- Authentication system (across services)
- Monitoring and logging (centralized)

## Navigation Patterns

### For Feature Development
```bash
# Check specs first
ls .kiro/specs/

# Navigate to target service
cd services/jawafdehi-api
# or
cd services/jawafdehi-frontend
```

### For Infrastructure Changes
```bash
cd services/infra
terraform plan
```

### For Documentation Updates
```bash
# Project-wide docs
edit docs/

# Service-specific docs
cd services/<service-name>/docs/
```