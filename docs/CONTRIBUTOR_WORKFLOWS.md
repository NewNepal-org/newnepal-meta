# Contributor Workflows

This document explains the different workflows for contributing to Jawafdehi based on your role.

## Two Types of Contributors

### Team Members (Use Meta Repo)

**Who**: Jawafdehi team members, interns, core contributors

**Why use the meta repo**:
- Access to complete project context across all services
- Shared documentation, research materials, and specifications
- AI-enriched context for development tools (Cursor, Kiro, GitHub Copilot)
- Easier cross-service coordination
- Infrastructure management visibility

**Workflow**: Clone meta repo → Mount needed services → Work across services

### Open Source Contributors (Use Individual Repos)

**Who**: External contributors, first-time contributors, focused contributors

**Why use individual repos**:
- Simpler setup - just one service
- No need to understand the full ecosystem
- Standard GitHub fork/PR workflow
- Faster onboarding

**Workflow**: Fork service repo → Clone → Make changes → Submit PR

---

## Team Member Workflow

### Initial Setup

1. **Clone the meta repository**
   ```bash
   git clone https://github.com/NewNepal-org/jawafdehi-meta.git
   cd jawafdehi-meta
   ```

2. **Mount services you need**
   ```bash
   # Example: Full-stack developer
   git submodule update --init services/jawafdehi-api services/jawafdehi-frontend services/nes
   ```

3. **Set up each service**
   ```bash
   # Python services
   cd services/jawafdehi-api
   poetry install
   cp .env.example .env
   
   # TypeScript services
   cd services/jawafdehi-frontend
   bun install
   cp .env.example .env
   ```

### Daily Development

1. **Check project board** - [Trello](https://trello.com/b/zSNsFJvU/jawafdehiorg)
2. **Review specs** - Check `.kiro/specs/` for feature specifications
3. **Work in service directory** - `cd services/{service-name}`
4. **Create feature branch** - `git checkout -b feature/your-feature`
5. **Make changes** - Edit code, add tests
6. **Test locally** - Run service-specific tests
7. **Commit changes** - In the service directory
8. **Push and PR** - Push to service repo and create PR

### Cross-Service Changes

When your work affects multiple services:

1. **Plan at meta-repo level** - Document in `/docs/` or `.kiro/specs/`
2. **Update services in order**:
   - Backend first (jawafdehi-api, nes)
   - Frontend second (jawafdehi-frontend, nes-tundikhel)
   - Infrastructure if needed (services/infra)
3. **Test integration** - Verify services work together
4. **Create PRs** - One PR per service
5. **Link PRs** - Reference related PRs in descriptions

### Updating Submodules

```bash
# Update a specific service to latest
cd services/jawafdehi-api
git pull origin main
cd ../..

# Update all mounted services
git submodule update --remote --merge

# Update meta repo reference to new service commits
git add services/jawafdehi-api
git commit -m "Update jawafdehi-api to latest"
```

---

## Open Source Contributor Workflow

### First-Time Setup

1. **Choose a service** - We recommend [NES](https://github.com/NewNepal-org/nes) for first contributions

2. **Fork the repository** - Click "Fork" on GitHub

3. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/nes.git
   cd nes
   ```

4. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/NewNepal-org/nes.git
   ```

5. **Set up the service** - Follow the README in the service

### Making a Contribution

1. **Sync with upstream**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b fix/issue-123
   ```

3. **Make your changes**
   - Edit code
   - Add tests
   - Update documentation

4. **Test your changes**
   ```bash
   # Python services
   poetry run pytest
   poetry run black .
   poetry run isort .
   
   # TypeScript services
   bun test
   bun run lint
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Fix: Description of your fix"
   ```

6. **Push to your fork**
   ```bash
   git push origin fix/issue-123
   ```

7. **Create a Pull Request**
   - Go to your fork on GitHub
   - Click "Compare & pull request"
   - Fill in the PR template
   - Submit!

### Finding Issues to Work On

- Look for `good first issue` labels
- Check the project board for "Help Wanted" items
- Read the service README for contribution guidelines
- Ask in GitHub Discussions if unsure

---

## Comparison: Meta Repo vs Individual Repo

| Aspect | Meta Repo (Team) | Individual Repo (OSS) |
|--------|------------------|----------------------|
| **Setup Complexity** | Higher (multiple services) | Lower (single service) |
| **Context** | Full ecosystem | Single service |
| **AI Tools** | Rich context | Service-only context |
| **Cross-service work** | Easy | Requires multiple forks |
| **Documentation** | Complete | Service-specific |
| **Onboarding** | Longer | Faster |
| **Best for** | Team members, interns | External contributors |

---

## Service-Specific Workflows

### jawafdehi-api (Django Backend)

```bash
cd services/jawafdehi-api
poetry install
poetry shell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Common tasks**:
- `python manage.py makemigrations` - Create migrations
- `python manage.py migrate` - Apply migrations
- `poetry run pytest` - Run tests
- `poetry run black . && poetry run isort .` - Format code

### jawafdehi-frontend (React Frontend)

```bash
cd services/jawafdehi-frontend
bun install
bun run dev
```

**Common tasks**:
- `bun run dev` - Start dev server
- `bun test` - Run tests
- `bun run build` - Build for production
- `bun run lint` - Lint code

### nes (Nepal Entity Service)

```bash
cd services/nes
poetry install
poetry shell
```

**Common tasks**:
- `poetry run pytest` - Run tests
- `poetry run nes-api` - Start API server
- `poetry run black . && poetry run isort .` - Format code

---

## Best Practices

### For All Contributors

1. **Write tests** - All new features need tests
2. **Follow code style** - Use provided formatters
3. **Update documentation** - Keep docs in sync with code
4. **Use authentic Nepali context** - Names, organizations, locations
5. **Support bilingual content** - English and Nepali
6. **Ensure accessibility** - Follow WCAG 2.1 AA guidelines

### For Team Members

1. **Check specs first** - Look in `.kiro/specs/` before starting
2. **Update project board** - Keep Trello current
3. **Coordinate changes** - Discuss cross-service impacts
4. **Review meta-repo docs** - Keep `/docs/` updated

### For Open Source Contributors

1. **Start small** - Pick a good first issue
2. **Ask questions** - Use GitHub Discussions
3. **Follow the PR template** - Helps reviewers
4. **Be patient** - Reviews may take time

---

## Getting Help

- **Team members**: Ask in team channels, check project board
- **Open source contributors**: Open a GitHub Discussion or issue
- **Documentation**: Check `/docs/` (meta repo) or service README
- **Code questions**: Comment on relevant issues or PRs

---

## Summary

**Team members**: Use the meta repo for full context and cross-service work.

**Open source contributors**: Fork individual service repos for focused contributions.

Both workflows are valid and welcome! Choose what works best for your situation.
