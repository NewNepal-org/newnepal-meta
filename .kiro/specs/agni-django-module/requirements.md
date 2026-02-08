# Requirements Document

## Introduction

The Agni Django Module integrates AI-assisted document processing into the JawafdehiAPI Django application. This module enables data enrichment specialists to upload documents, extract entities and cases using AI, resolve entity matches against the Nepal Entity Service (NES), and create/update cases in the Jawafdehi database. The workflow follows a 5-step pipeline: document submission → metadata extraction → entity processing with match resolution → entity updates → case processing.

## Glossary

- **Agni**: The AI-assisted document processing system
- **JawafdehiAPI**: The Django backend for the Jawafdehi corruption database
- **NES**: Nepal Entity Service - external database of Nepali public entities (persons, organizations, locations)
- **Case**: A corruption or misconduct allegation record in the Jawafdehi database
- **Entity**: A person, organization, or location that can be linked to cases
- **Match Resolution**: The process of linking extracted entities to existing NES records or creating new ones
- **Processing Session**: A single document processing workflow instance that tracks the complete lifecycle from document upload through final persistence. Each session maintains state (current step, extracted data, user decisions, feedback) and can be paused and resumed. A session is tied to one uploaded document and one user.
- **Confidence Score**: A value between 0.0 and 1.0 indicating AI certainty about an extraction

## Requirements

### Requirement 1: Document Submission

**User Story:** As a data enrichment specialist, I want to upload documents for AI processing, so that I can extract entity and case data without manual entry.

#### Acceptance Criteria

1. WHEN a user uploads a document file (.txt, .md, .doc, .docx, .pdf) with optional guidance text, THE Agni Module SHALL create a new processing session and store the document
2. WHEN a document is uploaded, THE Agni Module SHALL validate the file type and reject unsupported formats with a clear error message
3. WHEN a processing session is created, THE Agni Module SHALL assign a unique session identifier and track the session state (pending, processing, awaiting_review, completed, failed)
4. WHEN a user provides guidance text, THE Agni Module SHALL store the guidance and pass it to the AI extraction service

### Requirement 2: Document Metadata Extraction

**User Story:** As a data enrichment specialist, I want the AI to extract document metadata, so that I can understand the source and context of the information.

#### Acceptance Criteria

1. WHEN the AI processes a document, THE Agni Module SHALL extract metadata including source, publication date, document type, and case reference (if present)
2. WHEN metadata is extracted, THE Agni Module SHALL assign confidence scores (0.0-1.0) to each metadata field
3. WHEN metadata extraction completes, THE Agni Module SHALL display the metadata with confidence indicators and allow user feedback
4. WHEN a user provides feedback on metadata, THE Agni Module SHALL store the feedback and allow reprocessing with the feedback incorporated

### Requirement 3: Entity Extraction and Match Resolution

**User Story:** As a data enrichment specialist, I want the AI to extract entities and match them against existing records, so that I can avoid creating duplicates.

#### Acceptance Criteria

1. WHEN the AI processes a document, THE Agni Module SHALL extract person and organization entities with bilingual names (English and Nepali)
2. WHEN entities are extracted, THE Agni Module SHALL query NES to find potential matches and assign match confidence scores
3. WHEN a high-confidence match (≥95%) is found, THE Agni Module SHALL auto-match the entity and display it as resolved
4. WHEN multiple potential matches exist (confidence between 45% and 95%), THE Agni Module SHALL present disambiguation options to the user
5. WHEN no matches are found, THE Agni Module SHALL mark the entity for creation as a new NES record
6. WHEN a user selects a match or confirms creation, THE Agni Module SHALL update the entity resolution status
7. WHEN a user wants to override an auto-matched entity, THE Agni Module SHALL allow changing the match to a different NES entity or creating a new entity
8. WHEN a user wants to search for an entity manually, THE Agni Module SHALL provide NES search functionality to find and select existing entities
9. WHEN all entities are resolved, THE Agni Module SHALL enable proceeding to entity updates

### Requirement 4: Entity Update Review

**User Story:** As a data enrichment specialist, I want to review proposed entity changes before they are applied, so that I can ensure data accuracy.

#### Acceptance Criteria

1. WHEN entity resolution completes, THE Agni Module SHALL generate entity update proposals categorized as CREATE, UPDATE, or NO_CHANGE
2. WHEN displaying a CREATE proposal, THE Agni Module SHALL show fields according to the NES entity type schema (Person, PoliticalParty, GovernmentBody, Organization, Location, etc.)
3. WHEN displaying an UPDATE proposal, THE Agni Module SHALL show current values, proposed values, and a diff view using the appropriate entity type schema
4. WHEN displaying a NO_CHANGE proposal, THE Agni Module SHALL indicate the entity was matched but requires no updates
5. WHEN a user approves an entity proposal, THE Agni Module SHALL mark it as approved and ready for persistence
6. WHEN a user rejects an entity proposal, THE Agni Module SHALL mark it as rejected and exclude it from persistence
7. WHEN a user provides feedback on an entity, THE Agni Module SHALL send the feedback to the AI for reprocessing and update the proposal based on the AI response
8. WHEN the AI responds to feedback, THE Agni Module SHALL display the updated proposal and store the conversation in a discussion thread

### Requirement 5: Case Processing

**User Story:** As a data enrichment specialist, I want the AI to identify cases and link entities to them, so that I can build the corruption database efficiently.

#### Acceptance Criteria

1. WHEN entity processing completes, THE Agni Module SHALL identify cases mentioned in the document
2. WHEN a new case is identified, THE Agni Module SHALL generate a CREATE CASE proposal with fields matching the Jawafdehi Case model schema (title bilingual, case type, status, investigating body, case reference, date reported, estimated loss, summary bilingual, involved entities with roles)
3. WHEN an existing case is found that relates to the document, THE Agni Module SHALL generate an UPDATE CASE proposal showing current vs proposed changes according to the Case model schema
4. WHEN an entity may be linked to an existing case, THE Agni Module SHALL generate a LINK ENTITY proposal with the proposed role and AI reasoning
5. WHEN a user approves a case proposal, THE Agni Module SHALL mark it as approved and ready for persistence
6. WHEN a user rejects a case proposal, THE Agni Module SHALL mark it as rejected and exclude it from persistence
7. WHEN a user provides feedback on a case, THE Agni Module SHALL store the feedback in a discussion thread

### Requirement 6: Persistence and Completion

**User Story:** As a data enrichment specialist, I want approved changes to be saved to the database, so that the Jawafdehi database is enriched with new data.

#### Acceptance Criteria

1. WHEN all proposals are reviewed, THE Agni Module SHALL enable final submission
2. WHEN final submission is triggered, THE Agni Module SHALL persist approved entity changes to NES via API
3. WHEN final submission is triggered, THE Agni Module SHALL persist approved case changes to the Jawafdehi database
4. WHEN persistence completes successfully, THE Agni Module SHALL mark the session as completed and display a summary
5. IF persistence fails, THEN THE Agni Module SHALL mark the session as failed, log the error, and allow retry

### Requirement 7: Session Management

**User Story:** As a data enrichment specialist, I want to manage my processing sessions, so that I can track progress and resume incomplete work.

#### Acceptance Criteria

1. WHEN a user accesses the Agni Module, THE Agni Module SHALL display a list of their processing sessions with status
2. WHEN a user selects an incomplete session, THE Agni Module SHALL resume from the last completed step
3. WHEN a user views a completed session, THE Agni Module SHALL display a read-only summary of all changes made
4. WHEN a user deletes a session, THE Agni Module SHALL remove the session and all associated data

### Requirement 8: Django Admin Integration

**User Story:** As an administrator, I want to manage Agni processing through Django Admin, so that I can monitor and troubleshoot the system.

#### Acceptance Criteria

1. WHEN an administrator accesses Django Admin, THE Agni Module SHALL display processing sessions with filtering by status, date, and user
2. WHEN an administrator views a session, THE Agni Module SHALL display all session data including document, extractions, proposals, and feedback
3. WHEN an administrator needs to debug, THE Agni Module SHALL provide access to raw AI responses and processing logs

