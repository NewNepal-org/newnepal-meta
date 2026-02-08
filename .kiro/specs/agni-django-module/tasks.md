# Implementation Plan

## Overview

This implementation follows Test-Driven Development (TDD) with UI-driven testing from the start. Each feature begins with admin UI tests that define expected behavior, followed by implementation.

**Keep it simple, stupid (KISS)** - Avoid over-engineering. Build the simplest thing that works.

## Scope

**Two services involved:**
- **nes**: Core entity processing - direct implementations (no protocols) in `services/nes/nes/services/agni/`
- **jawafdehi-api**: Case processing extensions, Django models for session/change storage, and Django admin UI in `services/jawafdehi-api/agni/`

---

## Part 1: Django App Setup and Document Upload UI

- [x] 1. Remove protocols and simplify NES agni structure
  - [x] 1.1 Remove protocol abstractions from NES agni
    - Delete `services/NepalEntityService/nes/services/agni/protocols.py`
    - Update `agni_service.py` to use concrete implementations directly
    - Update imports in `__init__.py`
    - _Requirements: Simplification_

- [x] 2. Set up Django app structure and core models
  - [x] 2.1 Create the `agni` Django app with initial structure
    - Create `services/jawafdehi-api/agni/` directory structure
    - Create `__init__.py`, `apps.py`, `admin.py`, `models.py`
    - Register app in Django settings
    - _Requirements: 8.1_

  - [x] 2.2 Create StoredExtractionSession Django model
    - Implement model with fields: id (UUID), document (FileField), guidance, session_data (JSON), status, created_by, created_at, updated_at
    - Add status choices: pending, processing, awaiting_review, completed, failed
    - _Requirements: 1.3, 7.1, 7.2_

  - [x] 2.3 Create ApprovedEntityChange Django model
    - Implement model with fields: id (UUID), change_type, entity_type, entity_sub_type, nes_entity_id, entity_data (JSON), description, approved_by, approved_at
    - Add model Meta for ordering and verbose names
    - _Requirements: 6.2, 6.3_

  - [x] 2.4 Create and run migrations
    - Generate migrations for new models
    - Apply migrations to database
    - _Requirements: 1.3, 6.2_

- [ ] 3. Implement document upload admin view (first visible UI)
  - [x] 3.1 Write admin UI test for session list view
    - Test that admin displays session list with status, date, user columns
    - Test filtering by status works
    - Test filtering by user works
    - _Requirements: 7.1, 8.1_

  - [x] 3.2 Implement basic admin registration for models
    - Register ApprovedEntityChange with list display and filters
    - Register StoredExtractionSession with list display and filters
    - _Requirements: 8.1, 8.2_

  - [x] 3.3 Write property test for file type validation
    - **Property 1: File Type Validation**
    - *For any* file upload, the system SHALL accept only files with extensions in {.txt, .md, .doc, .docx, .pdf} and reject all others
    - **Validates: Requirements 1.2**

  - [x] 3.4 Implement file type validation utility
    - Create validation function for allowed file types
    - Return clear error messages for unsupported formats
    - _Requirements: 1.2_

  - [x] 3.5 Write admin UI test for document upload workflow
    - Test that upload form accepts valid file types
    - Test that upload form rejects invalid file types with error message
    - Test that guidance textarea is optional
    - Test that successful upload creates session and redirects to detail view
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 3.6 Implement custom admin view for document upload
    - Create upload form with file input and guidance textarea
    - Validate file type on submission
    - Create StoredExtractionSession on success
    - Initialize AgniService and begin_session
    - _Requirements: 1.1, 1.3, 1.4_

  - [x] 3.7 Write unit tests for document upload
    - Test session creation with valid document
    - Test session stores guidance text
    - Test unique session ID generation
    - _Requirements: 1.1, 1.3, 1.4_

- [ ] 4. Checkpoint - Document upload UI working
  - Ensure all tests pass, ask the user if questions arise.

---

## Part 2: Metadata Extraction UI

- [ ] 5. Implement AI metadata extraction (backend for UI)
  - [ ] 5.1 Write unit tests for AI metadata extraction
    - Test extract_metadata returns valid DocumentMetadata
    - Test conversation history influences extraction results
    - _Requirements: 2.1, 2.2_

  - [ ] 5.2 Implement metadata extraction in agni_service.py
    - Implement `extract_metadata()` with AI integration
    - Handle conversation history for iterative refinement
    - _Requirements: 2.1, 2.2_

  - [ ] 5.3 Write property test for confidence score range
    - **Property 2: Confidence Score Range**
    - *For any* extracted metadata field, the confidence score SHALL be within the range [0.0, 1.0]
    - **Validates: Requirements 2.2**

- [ ] 6. Implement session detail admin view with metadata
  - [ ] 6.1 Write admin UI test for session detail view
    - Test that session detail shows document info
    - Test that metadata section displays extracted fields
    - Test that confidence indicators appear for each field
    - Test that conversation thread displays messages
    - _Requirements: 2.3, 7.2, 8.2_

  - [ ] 6.2 Implement session detail admin view
    - Create custom change_view for StoredExtractionSession
    - Display document info and current status
    - Display metadata with confidence scores
    - Display conversation thread for metadata feedback
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ] 6.3 Implement metadata feedback submission
    - Add form for posting feedback to metadata conversation
    - Call AgniService.post_message_to_metadata()
    - Trigger metadata re-extraction
    - Update session_data with new metadata
    - _Requirements: 2.4_

- [ ] 7. Checkpoint - Metadata extraction UI working
  - Ensure all tests pass, ask the user if questions arise.

---

## Part 3: Entity Extraction and Resolution UI

- [ ] 8. Implement AI entity extraction (backend for UI)
  - [ ] 8.1 Write unit tests for AI entity extraction
    - Test extract_entities returns list of ExtractedEntity with bilingual names
    - Test conversation history influences extraction results
    - _Requirements: 3.1_

  - [ ] 8.2 Implement entity extraction in agni_service.py
    - Implement `extract_entities()` with bilingual name extraction
    - Handle conversation history for iterative refinement
    - _Requirements: 3.1_

  - [ ] 8.3 Write property test for entity confidence score range
    - **Property 2b: Entity Confidence Score Range**
    - *For any* extracted entity, the confidence score SHALL be within the range [0.0, 1.0]
    - **Validates: Requirements 3.2**

- [ ] 9. Implement entity list display UI
  - [ ] 9.1 Write admin UI test for entity list display
    - Test that extracted entities appear in list
    - Test that each entity shows type, names, status
    - Test that confidence scores display correctly
    - _Requirements: 3.1, 3.2_

  - [ ] 9.2 Implement entity list in session detail view
    - Display entity list with type, names, confidence
    - Show status indicator for each entity
    - _Requirements: 3.1, 3.2_

- [ ] 10. Implement NES search and entity resolution (backend for disambiguation UI)
  - [ ] 10.1 Write unit tests for entity search and resolution
    - Test search returns entities matching query
    - Test find_candidates returns ranked matches
    - Test resolve sets matched_id for high confidence (≥95%)
    - Test resolve sets candidates for medium confidence (45-95%)
    - Test resolve sets needs_creation for no matches
    - _Requirements: 3.2, 3.3, 3.4, 3.5_

  - [ ] 10.2 Implement search and resolve in agni_service.py
    - Implement `search()` using NES entity search
    - Implement `find_candidates()` with confidence scoring
    - Implement `resolve()` with confidence thresholds
    - _Requirements: 3.2, 3.3, 3.4, 3.5_

  - [ ] 10.3 Write property test for entity status derivation
    - **Property 3: Entity Status Derivation**
    - *For any* ExtractedEntity: needs_creation=True → "create_new", matched_id set → "matched", candidates non-empty → "needs_disambiguation"
    - **Validates: Requirements 3.3, 3.4, 3.5**

- [ ] 11. Implement entity disambiguation UI
  - [ ] 11.1 Write admin UI test for entity disambiguation
    - Test that disambiguation UI shows candidate list
    - Test that selecting candidate updates entity match
    - Test that "create new" option marks entity for creation
    - Test that override option allows changing auto-matched entity
    - _Requirements: 3.4, 3.6, 3.7_

  - [ ] 11.2 Implement entity resolution admin view
    - Display entity list with status indicators
    - Show disambiguation UI for needs_disambiguation entities
    - Implement candidate selection action
    - Implement "create new" action
    - Implement override action for auto-matched entities
    - _Requirements: 3.3, 3.4, 3.5, 3.6, 3.7_

  - [ ] 11.3 Implement NES search in entity resolution
    - Add search input for manual entity lookup
    - Display search results with select action
    - Update entity match on selection
    - _Requirements: 3.8_

- [ ] 12. Checkpoint - Entity extraction and resolution UI working
  - Ensure all tests pass, ask the user if questions arise.

---

## Part 4: Entity Update Review UI

- [ ] 13. Implement entity update review admin view
  - [ ] 13.1 Write admin UI test for entity proposal display
    - Test that CREATE proposals show all entity fields
    - Test that UPDATE proposals show diff view (current vs proposed)
    - Test that NO_CHANGE proposals indicate no updates needed
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ] 13.2 Write admin UI test for entity approval workflow
    - Test that approve button marks proposal as approved
    - Test that reject button marks proposal as rejected
    - Test that feedback submission triggers AI reprocessing
    - _Requirements: 4.5, 4.6, 4.7_

  - [ ] 13.3 Implement entity proposal display view
    - Display proposals categorized by type (CREATE, UPDATE, NO_CHANGE)
    - Show entity fields according to NES entity type schema
    - Show diff view for UPDATE proposals
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ] 13.4 Implement entity approval actions
    - Add approve/reject buttons for each proposal
    - Track approval status in session_data
    - Implement feedback form with AI reprocessing
    - Display conversation thread for entity feedback
    - _Requirements: 4.5, 4.6, 4.7, 4.8_

- [ ] 14. Checkpoint - Entity review UI working
  - Ensure all tests pass, ask the user if questions arise.

---

## Part 5: Case Processing UI

- [ ] 15. Implement case extraction and processing
  - [ ] 15.1 Write admin UI test for case identification display
    - Test that identified cases appear after entity processing
    - Test that CREATE CASE proposals show all case fields
    - Test that UPDATE CASE proposals show diff view
    - Test that LINK ENTITY proposals show role and reasoning
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ] 15.2 Implement case extraction in AgniService
    - Add case identification to AgniService
    - Extract case fields matching Jawafdehi Case model schema
    - Identify entity-case relationships with roles
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ] 15.3 Write admin UI test for case approval workflow
    - Test that approve button marks case proposal as approved
    - Test that reject button marks case proposal as rejected
    - Test that feedback is stored in discussion thread
    - _Requirements: 5.5, 5.6, 5.7_

  - [ ] 15.4 Implement case proposal display and approval
    - Display case proposals with approve/reject actions
    - Track case approval status in session_data
    - Store feedback in discussion thread
    - _Requirements: 5.5, 5.6, 5.7_

- [ ] 16. Checkpoint - Case processing UI working
  - Ensure all tests pass, ask the user if questions arise.

---

## Part 6: Final Submission and Persistence

- [ ] 17. Implement persistence (backend for final submission)
  - [ ] 17.1 Write unit tests for persistence
    - Test queue_entity_change creates pending change record
    - Test get_pending_changes returns all pending changes
    - Test apply_change persists entity to NES database
    - _Requirements: 6.2, 6.3_

  - [ ] 17.2 Implement persistence in agni_service.py
    - Implement `queue_entity_change()` to store pending changes
    - Implement `get_pending_changes()` to retrieve queue
    - Implement `apply_change()` to persist to NES
    - _Requirements: 6.2, 6.3_

  - [ ] 17.3 Write property test for persist requires resolution
    - **Property 4: Persist Requires Resolution**
    - *For any* call to persist(), all entities SHALL have status "create_new" or "matched"
    - **Validates: Requirements 6.1**

  - [ ] 17.4 Write property test for entity change queue integrity
    - **Property 5: Entity Change Queue Integrity**
    - *For any* queued entity change, entity_data SHALL contain all required fields for the entity_type
    - **Validates: Requirements 6.2**

- [ ] 18. Implement final submission UI
  - [ ] 18.1 Write admin UI test for final submission
    - Test that submit button appears when all proposals reviewed
    - Test that submit button is disabled when unresolved entities exist
    - Test that successful submission shows completion summary
    - Test that failed submission shows error and retry option
    - _Requirements: 6.1, 6.4, 6.5_

  - [ ] 18.2 Implement final submission view
    - Validate all entities are resolved before enabling submit
    - Call AgniService.persist() with approved entities
    - Persist approved case changes to Jawafdehi database
    - Create ApprovedEntityChange records for each entity
    - Update session status to completed
    - Display summary of changes made
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ] 18.3 Implement error handling for persistence
    - Catch persistence errors and log details
    - Update session status to failed
    - Display error message with retry option
    - _Requirements: 6.5_

- [ ] 19. Checkpoint - Final submission UI working
  - Ensure all tests pass, ask the user if questions arise.

---

## Part 7: Session Management and Polish

- [ ] 20. Implement session management features
  - [ ] 20.1 Write admin UI test for session resume
    - Test that incomplete session shows resume option
    - Test that resume loads session at last completed step
    - Test that completed session shows read-only summary
    - _Requirements: 7.2, 7.3_

  - [ ] 20.2 Implement session resume functionality
    - Deserialize session_data to AgniExtractionSession
    - Determine current step from session state
    - Redirect to appropriate view for current step
    - _Requirements: 7.2_

  - [ ] 20.3 Implement completed session summary view
    - Display read-only summary of all changes made
    - Show entities created/updated
    - Show cases created/updated
    - _Requirements: 7.3_

  - [ ] 20.4 Implement session deletion
    - Add delete action to session admin
    - Remove session and associated document
    - _Requirements: 7.4_

- [ ] 21. Final integration and polish
  - [ ] 21.1 Write admin UI test for admin filtering and search
    - Test filtering sessions by status
    - Test filtering sessions by date range
    - Test filtering sessions by user
    - Test search by document name
    - _Requirements: 8.1_

  - [ ] 21.2 Implement admin list customizations
    - Add list_filter for status, date, user
    - Add search_fields for document name
    - Add list_display for key session info
    - _Requirements: 8.1_

  - [ ] 21.3 Implement debug view for administrators
    - Display raw AI responses
    - Display processing logs
    - Display full session_data JSON
    - _Requirements: 8.3_

  - [ ] 21.4 Write integration test for full extraction workflow
    - Test complete flow: upload → metadata → entities → resolve → cases → persist
    - Verify ApprovedEntityChange records created correctly
    - Verify case records created/updated correctly
    - Verify session status transitions correctly
    - _Requirements: 1.1, 2.1, 3.1, 5.1, 6.1_

  - [ ] 21.5 Write end-to-end test for complete workflow
    - Test full user journey from upload to completion
    - Verify all UI elements render correctly
    - Verify all actions produce expected results
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1_

- [ ] 22. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
