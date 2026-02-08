# Prompt: Refactor Project Documentation for Multi-Agent Mono-Repo

## Role
You are an expert staff-level software engineer and technical writer. Your task is to refactor and reorganize the existing project documentation so it can effectively steer multiple AI agents (Kiro, Cursor, GitHub Copilot, Amazon Q) in a mono-repo / meta-repo setup.

You will read all existing documentation files in this repository and produce a clean, consistent, low-drift structure that works across agents.

---

## Project Context: Jawafdehi

**Jawafdehi** (https://jawafdehi.org, beta at https://beta.jawafdehi.org) is a civic tech platform promoting transparency and accountability in Nepali governance. It serves as an open database of corruption for Nepal, helping citizens access information about allegations of corruption and misconduct by public entities.

### Key Principles
- **Open Data**: All case data is open and accessible
- **Transparency**: Complete audit trails and version history
- **Nepali Context**: Use authentic Nepali names, organizations, and locations
- **Bilingual First**: Equal support for English and Nepali languages
- **Accessibility**: WCAG 2.1 AA compliance across all services

---

## Current Repository Structure

```
/
├── .kiro/                  # Kiro IDE configuration
│   ├── specs/              # Feature specifications
│   └── steering/           # AI steering rules
│
├── agent-kit/              # Multi-agent documentation toolkit
│   └── handbook/           # Source of truth docs (to be created)
│
├── assets/                 # Shared assets (images, docs, etc.)
│
├── case-research/          # Case research materials
│   ├── cases/              # Individual case files
│   ├── docs/               # Research documentation
│   └── tools/              # Research utilities
│
├── docs/                   # Project documentation
│   ├── agni/               # Agni AI assistant docs
│   ├── entities/           # Entity documentation
│   └── presentation/       # Presentation materials
│
├── laboratory/             # Experimental code and toolkits
│   └── AgniAI/             # Agni AI experiments
│
├── meeting-notes/          # Team meeting notes
│
├── outreach/               # Outreach materials
│
├── tools/                  # Shared development tools
│
└── services/               # All application services
    ├── Jawafdehi/          # React public frontend
    ├── JawafdehiAPI/       # Django accountability API
    ├── NepalEntityService/ # Nepal entity database service
    ├── NepalEntityService-assets/    # NES static assets
    └── NepalEntityService-tundikhel/ # NES frontend (Tundikhel)
```

### Services Overview

| Service | Type | Stack | Description |
|---------|------|-------|-------------|
| **Jawafdehi** | Frontend | React, TypeScript, Vite, Bun | Public-facing website |
| **JawafdehiAPI** | Backend | Django, DRF, PostgreSQL, Poetry | Core accountability API |
| **NepalEntityService** | Backend | Python, Poetry | Nepal entity database |
| **NepalEntityService-tundikhel** | Frontend | React, TypeScript, Vite | NES explorer UI |
| **NepalEntityService-assets** | Static | Jekyll | NES static assets site |

### Technology Stack

**Backend**
- Python 3.12+ with Django 5.2+ and Django REST Framework
- PostgreSQL database
- Poetry for dependency management

**Frontend**
- TypeScript with React 18
- Vite build tool, Bun runtime
- Tailwind CSS

**Infrastructure**
- Google Cloud Platform (Cloud Run, Cloud Build)
- Terraform for IaC

---

## High-level Goals

1. Establish **one source of truth** for product, architecture, workflow, and guardrails.
2. Produce **short, action-oriented agent entry points** that agents reliably follow.
3. Ensure documentation scales across:
   - multiple nested git repos
   - multiple AI tools with different instruction mechanisms
4. Minimize duplication and long-term drift.

---

## Target documentation model

### 1. Two-layer structure

**Layer A — Source of truth (tool-neutral, human-first):**
- Canonical documentation written in Markdown
- Explains:
  - product context and goals
  - system architecture and repo layout
  - development workflow
  - testing, quality, and security guardrails
- Modular and linkable
- Stable over time

**Layer B — Tool adapters (thin, tool-specific):**
- Minimal files that:
  - point agents to the source-of-truth docs
  - restate only critical non-negotiable rules
- No deep duplication of content

---

## Required output structure

Refactor or create documentation so it follows this structure:

```
<meta-repo root>/
  .kiro/                   # Single Kiro configuration at meta-repo root
    steering/
      product.md           # Product context pointer
      tech.md              # Tech stack rules
      structure.md         # Repo structure guide
    specs/
      <feature-name>/
        requirements.md
        design.md
        tasks.md

  agent-kit/               # source of truth (at meta-repo root)
    /handbook/
      00-product.md        # Product context, mission, principles
      10-architecture.md   # System architecture, service boundaries
      20-workflow.md       # Development workflow, PR process
      30-testing.md        # Testing standards, coverage requirements
      40-security.md       # Security guardrails, secrets management

<each git repo root>/
  AGENTS.md                # Cross-tool entry point

  .github/
    copilot-instructions.md
    instructions/
      *.instructions.md

  .cursor/
    rules/
      core/
        RULE.md

  .amazonq/
    rules/
      00-core.md
```

You may adapt paths slightly if the repo already has an established convention, but the **conceptual roles must remain the same**.

---

## AGENTS.md requirements (critical)

For **each git repo**, produce or refactor an `AGENTS.md` file with the following characteristics:

- Fits on ~1 screen (concise)
- Written in imperative, action-oriented language
- Contains:
  1. What this repo is and what it owns
  2. Non-negotiable rules (security, scope, quality)
  3. Where key things live (paths)
  4. Expected workflow (spec-first for non-trivial work)
  5. Concrete commands (build, test, lint)

`AGENTS.md` must act as the **cross-tool entry point** for all agents.

---

## Kiro specs (product backbone)

- Use `.kiro/specs/` at the **meta-repo root** as the canonical feature-spec library for the entire project
- This is a single, centralized specification folder shared across all services and repos
- For each non-trivial feature or behavior:
  - Ensure a folder exists with:
    - `requirements.md`
    - `design.md`
    - `tasks.md`
- Specs must be:
  - small and feature-scoped
  - referenced by agents before making changes
- If specs do not exist for a feature, create a minimal one rather than embedding decisions in code or chat

---

## Tool adapter rules

When refactoring tool-specific files, follow these principles:

### GitHub Copilot
- Keep `.github/copilot-instructions.md` short
- Point to `AGENTS.md` and relevant handbook sections
- Use path-scoped instruction files only for true domain-specific rules

### Cursor
- Prefer `.cursor/rules/` over legacy `.cursorrules`
- Keep core rules minimal and reusable
- Avoid restating full architecture or product docs

### Amazon Q
- Use `.amazonq/rules/` for concise, high-signal rules
- Focus on security, correctness, and repo-specific workflow

### Kiro steering
- Located at `.kiro/steering/` at the meta-repo root (single location for all steering)
- Split steering into small files (product / tech / structure)
- Avoid monolithic steering documents
- Assume Kiro specs are committed and authoritative

---

## Style and quality constraints

- Prefer links over duplication
- Prefer explicit paths over vague descriptions
- Use consistent terminology across all files
- Remove outdated, redundant, or conflicting documentation
- Do NOT invent new product requirements
- Do NOT include secrets or sensitive information
- Use authentic Nepali context in all examples

---

## What you should produce

1. Refactored documentation files in-place or newly created, following the structure above
2. Clear consolidation of overlapping docs into the source-of-truth handbook
3. Clean, minimal agent-facing instruction files
4. No explanatory prose about *why* — only the refactored artifacts

Proceed file by file, ensuring the final state is coherent, minimal, and optimized for AI agents operating in a mono-repo with multiple tools.

