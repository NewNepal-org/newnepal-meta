# Getting Started with Jawafdehi

Welcome to Jawafdehi! This guide will help you get started whether you're a team member, intern, or open source contributor.

## For Team Members and Interns

### 1. Clone the Meta Repository

```bash
git clone https://github.com/NewNepal-org/jawafdehi-meta.git
cd jawafdehi-meta
```

This gives you the meta-repo structure including documentation, research materials, and tooling.

### 2. Mount the Services You Need

Initialize only the services you're working on:

```bash
# For frontend work
git submodule update --init services/jawafdehi-frontend

# For backend work
git submodule update --init services/jawafdehi-api services/nes

# For infrastructure work
git submodule update --init services/infra

# For full-stack work
git submodule update --init services/jawafdehi-api services/jawafdehi-frontend services/nes services/infra
```

### 3. Set Up Your Development Environment

#### For Python Services (jawafdehi-api, nes)

```bash
cd services/jawafdehi-api  # or services/nes
poetry install
poetry shell
cp .env.example .env
# Edit .env with your configuration
```

#### For TypeScript Services (jawafdehi-frontend, nes-tundikhel)

```bash
cd services/jawafdehi-frontend  # or services/nes-tundikhel
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

| Service | Good For | Repository |
|---------|----------|------------|
| **nes** | Python, data processing, entity management | [NewNepal-org/nes](https://github.com/NewNepal-org/nes) |
| **jawafdehi-api** | Django, REST APIs, backend | [NewNepal-org/jawafdehi-api](https://github.com/NewNepal-org/jawafdehi-api) |
| **jawafdehi-frontend** | React, TypeScript, UI/UX | [NewNepal-org/jawafdehi-frontend](https://github.com/NewNepal-org/jawafdehi-frontend) |
| **nes-tundikhel** | React, data visualization | [NewNepal-org/nes-tundikhel](https://github.com/NewNepal-org/nes-tundikhel) |

## Understanding the Architecture

### Service Dependencies

```
jawafdehi-frontend → jawafdehi-api → nes
nes-tundikhel → nes
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
