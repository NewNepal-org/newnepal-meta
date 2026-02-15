# Meta-Repo Structure Guide

## Repository Overview
NewNepal.org meta-repository containing multiple independent services for Nepal's civic tech ecosystem. This meta-repo serves as the central hub, consolidating all projects, services, infrastructure code, documentation, and research materials.

> Repository: https://github.com/NewNepal-org/newnepal-meta

## Directory Structure

```
/
├── .kiro/                  # Kiro IDE configuration (meta-repo level)
│   ├── specs/              # Feature specifications (shared)
│   └── steering/           # AI steering rules (shared)
├── .amazonq/               # Amazon Q configuration
├── .cursor/                # Cursor IDE configuration
├── .github/                # GitHub configuration (workflows, templates)
│
├── services/               # All application services (git submodules)
│   ├── jawafdehi-api/      # Django accountability API
│   ├── jawafdehi-frontend/ # React public frontend
│   ├── nes/                # Nepal entity database
│   ├── nes-tundikhel/      # NES explorer UI
│   ├── nes-assets/         # NES static assets
│   ├── newnepal-website/   # NewNepal.org main website
│   └── infra/              # Infrastructure as Code (git submodule)
│       ├── terraform/      # Terraform configuration
│       └── misc/           # Build configs and scripts
│
├── docs/                   # Meta-repo documentation (cross-cutting concerns)
├── case-research/          # Case research materials
├── laboratory/             # Experimental code and toolkits
└── tools/                  # Shared development tools

Note: Services are git submodules. You can clone selectively based on your needs.
For full details on repository setup and selective cloning, see docs/GETTING_STARTED.md.
```

## Service Responsibilities

### Jawafdehi.org Platform
**jawafdehi-api** (Django Backend)
- Corruption case management
- User authentication and permissions
- RESTful API for frontend consumption
- Integration with Nepal Entity Service

**jawafdehi-frontend** (React Frontend)
- Public-facing website at https://jawafdehi.org
- Case browsing and search
- User interface for transparency data
- Responsive design with accessibility

### Nepal Entity Service (NES)
**nes** (Entity Database)
- Government entity data management
- Entity search and validation
- API for entity information
- Data scraping and updates
- The actual database is in the `nes-db/v2` folder in the service directory. It is quite large and we should be careful about the read operations we make. Write operations through CLI operations are forbidden.

**nes-tundikhel** (NES Explorer UI)
- Entity browsing and search interface
- Visualization of entity relationships

**nes-assets** (Static Assets)
- Static assets and documentation for NES

### Nepal Governance Modernization (NGM)
**ngm** (Judicial Data Collection)
- Scrapes judicial data from Nepal's court system
- Structures court case information
- Provides data for governance analysis

### NewNepal.org Website
**newnepal-website** (Main Website)
- Organizational website
- Project information and documentation

### Infrastructure (services/infra - git submodule)
- Terraform configuration for GCP
- Container deployment setup
- Database provisioning
- CI/CD pipeline configuration

## Development Workflow

### Service-Specific Work
1. Navigate to service directory: `cd services/<service-name>`
2. Check service README.md for specific guidance
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

### Selective Service Cloning
```bash
# Clone meta-repo without services
git clone https://github.com/NewNepal-org/newnepal-meta

# Clone specific service(s)
git submodule update --init services/jawafdehi-api
git submodule update --init services/nes

# Clone all services
git submodule update --init --recursive
```

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
# Meta-repo documentation (cross-cutting concerns)
edit docs/

# Service-specific docs
cd services/<service-name>/docs/
```