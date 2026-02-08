# Jawafdehi Meta-Repository

This is the Jawafdehi meta-repository - a comprehensive civic tech platform promoting transparency and accountability in Nepali governance.

**Mission**: Serve as an open database of corruption for Nepal, helping citizens access information about allegations of corruption and misconduct by public entities.

**Live Platform**: https://jawafdehi.org (beta: https://beta.jawafdehi.org)  
**Project Board**: https://trello.com/b/zSNsFJvU/jawafdehiorg

## Who Should Use This Meta Repo?

### Team Members & Interns
If you're a **Jawafdehi team member** or **intern**, this meta-repository is designed for you. It provides:
- Complete context for all services and their relationships
- Shared documentation, research materials, and tooling
- AI-enriched context for GenAI tools (Cursor, Kiro, GitHub Copilot, etc.)
- Cross-service coordination and infrastructure management

**👉 [Start Here: Getting Started Guide](docs/GETTING_STARTED.md)**

### Open Source Contributors
If you're an **open source contributor**, you can work directly with individual service repositories without needing the meta repo.

**👉 [Learn More: Contributor Workflows](docs/CONTRIBUTOR_WORKFLOWS.md)**

**Primary open source target**: [Nepal Entity Service (NES)](https://github.com/NewNepal-org/nes)

## Available Services

| Service | Description | Repository |
|---------|-------------|------------|
| **jawafdehi-api** | Django accountability API | [NewNepal-org/jawafdehi-api](https://github.com/NewNepal-org/jawafdehi-api) |
| **jawafdehi-frontend** | React public frontend | [NewNepal-org/jawafdehi-frontend](https://github.com/NewNepal-org/jawafdehi-frontend) |
| **nes** | Nepal Entity Service database | [NewNepal-org/nes](https://github.com/NewNepal-org/nes) |
| **nes-tundikhel** | NES explorer UI | [NewNepal-org/nes-tundikhel](https://github.com/NewNepal-org/nes-tundikhel) |
| **nes-assets** | NES static assets site | [NewNepal-org/nes-assets](https://github.com/NewNepal-org/nes-assets) |
| **infra** | Infrastructure as Code (Terraform) | [NewNepal-org/infra](https://github.com/NewNepal-org/infra) |

## Repository Structure

```
/
├── .kiro/                  # Kiro IDE configuration
│   ├── specs/              # Feature specifications
│   └── steering/           # AI steering rules
│
├── services/               # All application services (git submodules)
│   ├── jawafdehi-api/      # Django accountability API
│   ├── jawafdehi-frontend/ # React public frontend
│   ├── nes/                # Nepal entity database
│   ├── nes-tundikhel/      # NES explorer UI
│   ├── nes-assets/         # NES static assets
│   └── infra/              # Infrastructure as Code
│
├── docs/                   # Project documentation
│   ├── GETTING_STARTED.md  # Setup guide for team members
│   └── CONTRIBUTOR_WORKFLOWS.md  # Contribution workflows
│
├── case-research/          # Case research materials
├── laboratory/             # Experimental code and toolkits
└── tools/                  # Shared development tools
```

## Documentation

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Setup instructions for team members and contributors
- **[Contributor Workflows](docs/CONTRIBUTOR_WORKFLOWS.md)** - Understand team vs open source workflows
- **[Project Board](https://trello.com/b/zSNsFJvU/jawafdehiorg)** - Current tasks and priorities

## Technology Stack

- **Backend**: Python 3.12+, Django 5.2+, Poetry
- **Frontend**: TypeScript, React 18, Vite, Bun
- **Database**: PostgreSQL
- **Infrastructure**: Google Cloud Platform, Terraform

## Contributing

See our [Contributor Workflows](docs/CONTRIBUTOR_WORKFLOWS.md) guide to understand the best way to contribute based on your role.

## License

MIT
