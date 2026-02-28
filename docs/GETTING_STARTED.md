# Getting Started with NewNepal.org

Welcome to NewNepal.org! This guide will help you get started whether you're a team member, intern, or open source contributor.

## For Team Members and Interns

### 1. Clone the Meta Repository

```bash
git clone git@github.com:NewNepal-org/newnepal-meta.git
cd newnepal-meta
```

This gives you the meta-repo structure including documentation, research materials, and tooling for all NewNepal.org projects (Jawafdehi, NES, NGM).

### 2. Clone the Services You Need

Clone only the services you're working on into the services/ directory:

```bash
cd services

# For Jawafdehi frontend work
git clone git@github.com:NewNepal-org/Jawafdehi.git jawafdehi-frontend

# For Jawafdehi backend work
git clone git@github.com:NewNepal-org/JawafdehiAPI.git jawafdehi-api
git clone git@github.com:NewNepal-org/NepalEntityService.git nes

# For NGM (judicial data) work
git clone git@github.com:NewNepal-org/ngm.git ngm
git clone git@github.com:NewNepal-org/NepalEntityService.git nes

# For infrastructure work
git clone git@github.com:NewNepal-org/GCP-deployment.git infra

# For full-stack Jawafdehi work
git clone git@github.com:NewNepal-org/JawafdehiAPI.git jawafdehi-api
git clone git@github.com:NewNepal-org/Jawafdehi.git jawafdehi-frontend
git clone git@github.com:NewNepal-org/NepalEntityService.git nes
git clone git@github.com:NewNepal-org/GCP-deployment.git infra

cd ..
```

### 3. Set Up Your Development Environment

#### For Python Services (jawafdehi-api, nes, ngm)

```bash
cd services/jawafdehi-api  # or services/nes or services/ngm
poetry install
poetry shell
cp .env.example .env
# Edit .env with your configuration
```

#### For TypeScript Services (jawafdehi-frontend, nes-tundikhel, newnepal-website)

```bash
cd services/jawafdehi-frontend  # or services/nes-tundikhel or services/newnepal-website
bun install
cp .env.example .env
# Edit .env with your configuration
```

### 4. Explore the Documentation

- **Meta-repo docs**: `/docs/` - Cross-cutting concerns, architecture, presentations
- **Service docs**: `services/{service}/docs/` - Service-specific features and APIs
- **Specs**: `.kiro/specs/` - Feature specifications
- **Steering**: `.kiro/steering/` - AI development guidelines

### 5. Check the Project Board

Visit our [Trello board](https://trello.com/b/zSNsFJvU/jawafdehiorg) to see current tasks and priorities.

### 6. Start Contributing

1. Create a branch for your work
2. Make your changes
3. Run tests: `poetry run pytest` (Python) or `bun test` (TypeScript)
4. Format code: `poetry run black . && poetry run isort .` (Python) or `bun run lint` (TypeScript)
5. Commit and push your changes
6. Create a pull request

## For Open Source Contributors

### Quick Start

1. **Choose a service** - We recommend starting with [Nepal Entity Service (NES)](https://github.com/NewNepal-org/nes)
2. **Fork the repository** - Click "Fork" on GitHub
3. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nes.git
   cd nes
   ```
4. **Set up the service** - Follow the README in the service repository
5. **Make your changes** - Create a branch, make changes, test
6. **Submit a PR** - Push to your fork and create a pull request

### Where to Contribute

| Service | Good For | Repository | Clone Command |
|---------|----------|------------|---------------|
| **nes** | Python, data processing, entity management | [NewNepal-org/NepalEntityService](https://github.com/NewNepal-org/NepalEntityService) | `git clone git@github.com:NewNepal-org/NepalEntityService.git nes` |
| **jawafdehi-api** | Django, REST APIs, backend | [NewNepal-org/JawafdehiAPI](https://github.com/NewNepal-org/JawafdehiAPI) | `git clone git@github.com:NewNepal-org/JawafdehiAPI.git jawafdehi-api` |
| **jawafdehi-frontend** | React, TypeScript, UI/UX | [NewNepal-org/Jawafdehi](https://github.com/NewNepal-org/Jawafdehi) | `git clone git@github.com:NewNepal-org/Jawafdehi.git jawafdehi-frontend` |
| **nes-tundikhel** | React, data visualization | [NewNepal-org/NepalEntityService-tundikhel](https://github.com/NewNepal-org/NepalEntityService-tundikhel) | `git clone git@github.com:NewNepal-org/NepalEntityService-tundikhel.git nes-tundikhel` |
| **ngm** | Python, web scraping, judicial data | [NewNepal-org/ngm](https://github.com/NewNepal-org/ngm) | `git clone git@github.com:NewNepal-org/ngm.git ngm` |

## Understanding the Architecture

### NewNepal.org Projects

1. **Jawafdehi.org** - Open database of corruption and accountability
2. **NES (Nepal Entity Service)** - Comprehensive database of Nepali public entities
3. **NGM (Nepal Governance Modernization)** - Judicial data collection and governance analysis

### Service Dependencies

```
jawafdehi-frontend → jawafdehi-api → nes
jawafdehi-frontend → nes
nes-tundikhel → nes
ngm → nes (for entity resolution; near future plan)
```

### Technology Stack

- **Backend**: Python 3.12+, Django 5.2+, Poetry
- **Frontend**: TypeScript, React 18, Vite, Bun
- **Database**: PostgreSQL
- **Infrastructure**: Google Cloud Platform, Terraform

## Getting Help

- **Documentation**: Check `/docs/` and service-specific docs
- **Issues**: Open an issue on the relevant service repository
- **Discussions**: Use GitHub Discussions for questions
- **Project Board**: [Trello](https://trello.com/b/zSNsFJvU/jawafdehiorg)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:
- Use authentic Nepali names and contexts in examples
- Support bilingual (English/Nepali) content
- Follow accessibility guidelines (WCAG 2.1 AA)
- Be respectful and constructive in all interactions

## Next Steps

- **Team members**: Explore the meta repo structure and check the project board
- **Open source contributors**: Pick a service, read its README, and find a good first issue
- **Questions?**: Open a discussion or reach out to the maintainers

Welcome to the team! 🇳🇵
