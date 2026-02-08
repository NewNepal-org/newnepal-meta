This document outlines the details for Uranium.

## Background

**Nepal Entity Service (NES)** is an open source, open data, and open API platform that provides a comprehensive database of Nepali public entities—including persons (politicians, public officials), organizations (political parties, government bodies), and locations (provinces, districts, municipalities). It features full versioning, relationship tracking, and native bilingual support for Nepali and English. NES serves as the foundational data layer for civic technology applications.

**Jawafdehi** (https://jawafdehi.org) is a civic tech platform built on top of NES that promotes transparency and accountability in Nepali governance. It maintains an open database of corruption cases and allegations of misconduct by public entities, helping citizens access critical information about accountability issues. Together, these platforms enable data-driven transparency and empower citizens to hold public figures and institutions accountable.

## Practical challenge

**The Real Problem:** It takes a long time to build corruption cases based on primary sources.

Building a single case from official government documents currently takes hours or days of manual work. We face three core challenges:

1. **Scraping text from government websites is difficult** - Government websites only support small bandwidth (slow downloads, frequent timeouts), have service availability issues (sites go down unpredictably, maintenance windows without notice), and contain Nepali text which is harder to perform OCR on (especially in scanned documents with poor quality).

2. **Our engineering team size is limited to perform manual data sourcing** - We don't have enough engineers to manually browse government portals, download documents, extract text, identify entities, and structure the data. The manual process doesn't scale with the volume of documents we need to process.

3. **Our content moderation and case worker team size is limited to perform fact checks** - We have a small team of domain experts who can verify source credibility, validate extracted information, cross-reference claims, and review cases before publication. Manual fact-checking creates a bottleneck that limits how many cases we can publish.

**Current workflow:** A researcher manually browses government websites → downloads PDFs → reads and understands the document → extracts relevant information → formats data to match our schema → cross-checks against existing database → creates/updates entities and cases → another person reviews for accuracy → finally publishes. This can take **hours per document**.

## Tenets

Core principles that must guide our solution design:

1. **Scalable** - Must handle 10,000+ cases and 100,000+ entities. Support concurrent processing, scale horizontally as volume increases, and work within infrastructure cost constraints.

2. **Incremental Processing** - Process documents one at a time or in small groups, allowing us to start small and scale up gradually. Each document should be independently processable without requiring the entire corpus.

3. **Integrity** - Data must be factual and traceable. No duplicate entities (e.g., "रामबहादुर श्रेष्ठ" and "Ram Bahadur Shrestha" should resolve to the same entity). No duplicate cases. Every piece of data must be traceable back to its source document with complete audit trails.

4. **Human-in-the-Loop** - AI-assisted but human-verified. The system should accelerate our small team's work, not replace it. Outputs must be easy to review and correct, with clear presentation of extracted data and proposed changes before they're committed to the database.

5. **Transparent and Auditable** - The system must explain its decisions. Show confidence scores for extractions, explain why entities were matched or created as new, flag uncertain extractions for review, and provide clear reasoning that helps reviewers focus their limited time on the right things.

## Solution
1. We scrape verified official document from government websites, and build a solution to update our entity/jawafdehi services.

Input:
1. A semi-strucuted metadata file, describing the content
    1. Where the source is coming from
    1. (Perhaps some other system context)
1. A PDF file or equivalent
1. A human-provided context (think of it as a system prompt for AI)

Output:
1. The list of changes it will make to Entity, Case, and Document Source objects.


## Instructions for AI Agents
Your name is "Agenta" and you are a senior principal engineer, and you are desinging a feature for Jawafdehi and NES. Consider that you are presenting this to your boss, who is a nice, friendly person, and you want to also be nice, friendly, and use simple/easy to understand language (but also technically correct).


---

## Appendix A: Primary Data Models

This section describes the core data models we're working with in NES and Jawafdehi.

### Nepal Entity Service (NES) Models

**Entity (Base Model)**
- Common fields for all entities: `id`, `type`, `sub_type`, `name` (bilingual), `aliases`, `metadata`
- Full versioning support with audit trails
- Relationship tracking between entities

**Person**
- Extends Entity
- Fields: `birth_date`, `birth_place`, `citizenship_place`, `gender`, `address`
- Family: `father_name`, `mother_name`, `spouse_name`
- Professional: `education[]`, `positions[]`
- Used for: Politicians, public officials, public figures

**Organization**
- Extends Entity
- Subtypes:
  - **PoliticalParty**: `address`, `party_chief`, `registration_date`, `symbol`
  - **GovernmentBody**: `government_type` (federal/provincial/local)
  - **Hospital**: `beds`, `services[]`, `ownership`, `address`
- Used for: Political parties, government bodies, NGOs, institutions

**Location**
- Extends Entity
- Fields: `parent` (hierarchical), `area`, `lat`, `lng`, `location_type`, `administrative_level`
- Types: Province, District, Municipality, Rural Municipality, Ward, Constituency
- Hierarchical structure (Province → District → Municipality → Ward)

### Jawafdehi Models

**JawafEntity**
- Links to NES entities or represents custom entities
- Fields:
  - `nes_id`: Reference to NES entity (unique, optional)
  - `display_name`: Custom name (optional if nes_id present, required otherwise)
- Constraint: Must have either `nes_id` OR `display_name` (or both)
- Used to reference entities in cases while maintaining flexibility

**Case**
- Core accountability case model with versioning
- Versioning: `case_id` (shared across versions), `version` (increments)
- State workflow: `DRAFT` → `IN_REVIEW` → `PUBLISHED` → `CLOSED`
- Core fields:
  - `case_type`: Type of misconduct (corruption, broken promises, etc.)
  - `title`: Case title
  - `description`: Rich text description
  - `case_start_date`, `case_end_date`: Incident timeframe
- Entity relationships (many-to-many via JawafEntity):
  - `alleged_entities`: Entities being accused
  - `related_entities`: Other involved entities
  - `locations`: Location entities
- Structured data:
  - `tags[]`: Categorization tags
  - `key_allegations[]`: List of allegation statements
  - `timeline[]`: Chronological events
  - `evidence[]`: Evidence entries with source references
- Metadata:
  - `contributors`: Users assigned to the case
  - `versionInfo`: Version tracking metadata
- Validation: Lenient for DRAFT, strict for IN_REVIEW/PUBLISHED

**DocumentSource**
- Evidence sources referenced by cases
- Fields:
  - `source_id`: Unique identifier
  - `title`: Source title
  - `description`: Source description
  - `url`: Link to source document
  - `source_type`: Type of source (government document, news article, etc.)
  - `publication_date`: When source was published
  - `is_deleted`: Soft delete flag
- Publicly accessible if referenced in evidence of any published case
- Soft-deleted to preserve audit history

### Key Relationships

```
NES Entity (Person/Organization/Location)
    ↓ (referenced by nes_id)
JawafEntity
    ↓ (many-to-many)
Case ← (references) → DocumentSource
    ↓ (versioning)
Case (multiple versions with same case_id)
```

### Data Flow for Uranium

The automated system will need to:

1. **Extract entities** from documents → Create/update NES entities (Person, Organization, Location)
2. **Create JawafEntity records** → Link to NES entities via `nes_id` or use `display_name` for custom entities
3. **Create DocumentSource records** → Store source metadata and URLs
4. **Create/update Case records** → Link entities, sources, and structured data
5. **Maintain relationships** → Connect entities through Case relationships and NES relationship system
