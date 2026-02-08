# Requirements Document

## Introduction

Agni AI is an AI-assisted data enrichment system designed to accelerate the enrichment of entity data in the Nepal Entity Service (NES) by automatically extracting and structuring information from government documents. This POC focuses on establishing the core workflow: document ingestion → AI extraction → change request generation → human review → persistence. The POC uses plain text documents (not PDFs) to validate the approach quickly and enable measurement of results.

## Glossary

- **Agni AI**: The AI-assisted data enrichment system
- **NES**: Nepal Entity Service - database of Nepali public entities (persons, organizations, locations)
- **Change Request**: A structured proposal containing entities to create or update
- **Entity**: A person, organization, or location in the NES database
- **Human Reviewer**: A domain expert who verifies and approves AI-generated change requests

## Requirements

### Requirement 1: Document Submission

**User Story:** As a data enrichment specialist, I want to submit document files for processing, so that I can extract entity data without manual entry.

#### Acceptance Criteria

1. WHEN a user provides a document file path (.txt, .md, .doc, .docx) with optional guidance, THE Agni AI SHALL accept and store the input for processing
2. WHEN a document file is provided, THE Agni AI SHALL read and extract the text content from the file

### Requirement 2: AI Extraction

**User Story:** As a data enrichment specialist, I want the AI to extract metadata, entities, and attributes, so that I can enrich the NES database with comprehensive information.

#### Acceptance Criteria

1. WHEN the AI processes a document, THE Agni AI SHALL extract document metadata (author, publication date, document type, source)
2. WHEN the AI processes a document, THE Agni AI SHALL extract person and organization entities with bilingual names (Nepali and English)
3. WHEN the AI extracts entities, THE Agni AI SHALL extract attributes (roles, positions, affiliations)
4. WHEN the AI extracts information, THE Agni AI SHALL assign confidence scores between 0.0 and 1.0 to all extracted fields
5. WHEN the AI extracts entities, THE Agni AI SHALL attempt to match them against existing NES entities

### Requirement 3: Change Request Generation

**User Story:** As a data enrichment specialist, I want structured change requests, so that I can review all proposed modifications before applying them.

#### Acceptance Criteria

1. WHEN extraction completes, THE Agni AI SHALL generate a change request with extracted metadata and entities (new entities to create and existing entities to update)
2. WHEN generating a change request, THE Agni AI SHALL include document source references and explanations for each change
3. WHEN generating a change request, THE Agni AI SHALL serialize the request to JSON format

### Requirement 4: Human Review

**User Story:** As a human reviewer, I want to review and approve change requests, so that I can verify accuracy before persistence.

#### Acceptance Criteria

1. WHEN a change request is presented, THE Agni AI SHALL display extracted metadata and entities (creations and updates with before/after comparisons)
2. WHEN a change request is presented, THE Agni AI SHALL highlight low-confidence extractions (confidence < 0.7)
3. WHEN a reviewer approves a change request, THE Agni AI SHALL mark it as approved and ready for persistence
4. WHEN a reviewer rejects a change request, THE Agni AI SHALL store feedback with phase-specific prefixes (metadata:, entity:, matching:) and route feedback to the appropriate processing phase during reprocessing

### Requirement 5: Persistence Interface

**User Story:** As a data enrichment specialist, I want approved changes ready for persistence, so that external systems can apply them to NES.

#### Acceptance Criteria

1. WHEN a change request is approved, THE Agni AI SHALL provide a stub persistence interface
2. WHEN the persistence stub is called, THE Agni AI SHALL validate the change request structure and log the operation
3. WHEN the persistence stub completes, THE Agni AI SHALL return success without modifying external databases

**Note:** Actual NES database persistence will be developed separately.

### Requirement 6: Interactive CLI

**User Story:** As a data enrichment specialist, I want an interactive command-line interface, so that I can process documents and review extractions in a simple terminal environment.

#### Acceptance Criteria

1. WHEN the CLI starts, THE Agni AI SHALL present a menu for submitting documents and reviewing change requests
2. WHEN a user submits a document via CLI, THE Agni AI SHALL accept file path input (.txt, .md, .doc, .docx) with optional guidance text
3. WHEN extraction completes, THE Agni AI SHALL display the change request in a readable format with all extracted information
4. WHEN reviewing via CLI, THE Agni AI SHALL allow the user to approve, reject with feedback, or edit individual fields interactively
5. WHEN the user provides feedback, THE Agni AI SHALL accept text input and store it with the change request
