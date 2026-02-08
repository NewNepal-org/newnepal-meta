# Implementation Plan: Agni AI POC (Test-Driven Development)

## Overview
This plan implements the Agni AI POC using Test-Driven Development (TDD) with the red-green-refactor methodology. Each feature is developed by:
1. **RED**: Write a failing test first
2. **GREEN**: Write minimal code to make the test pass
3. **REFACTOR**: Improve code quality while keeping tests green

The implementation follows a four-stage pipeline architecture: Processor → Extraction → Matching → Review, with an interactive CLI interface.

---

## Phase 1: Project Setup and Core Infrastructure

- [x] 1. Set up project configuration and test infrastructure
  - [x] 1.1 **RED**: Write test for configuration loading in `tests/test_config.py`
    - Test that config loads GOOGLE_APPLICATION_CREDENTIALS path
    - Test that config extracts project_id from service account JSON
    - Test that config loads NES_DATABASE_URL and LOG_LEVEL
    - _Requirements: Implementation Notes - Configuration_
  
  - [x] 1.2 **GREEN**: Implement `agni/config.py` to make tests pass
    - Load environment variables using python-dotenv
    - Read and parse GOOGLE_APPLICATION_CREDENTIALS JSON file
    - Extract project_id from service account JSON
    - Provide config values as module-level variables or Config class
  
  - [x] 1.3 **REFACTOR**: Improve config module
    - Add error handling for missing files or invalid JSON
    - Add validation for required fields
    - Add helpful error messages
  
  - [x] 1.4 Create `.env.example` with required variables
    - GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
    - NES_DATABASE_URL=postgresql://...
    - LOG_LEVEL=INFO

---

## Phase 2: Core Data Models (TDD)

- [ ] 2. Implement Document and DocumentMetadata models
  - [x] 2.1 **RED**: Write tests in `tests/test_models.py` for Document model
    - Test Document creation with all required fields
    - Test Document with optional guidance field
    - _Requirements: Data Models - Document_
  
  - [x] 2.2 **GREEN**: Create `agni/models/document.py` with Document dataclass
    - Fields: id, file_path, content, guidance, submitted_at
  
  - [x] 2.3 **RED**: Write tests for DocumentMetadata model
    - Test DocumentMetadata creation with all fields
    - Test confidence_scores dict structure
    - _Requirements: 2.1, Data Models - DocumentMetadata_
  
  - [x] 2.4 **GREEN**: Create `agni/models/metadata.py` with DocumentMetadata dataclass
    - Fields: author, publication_date, document_type, source, confidence_scores
  
  - [x] 2.5 **REFACTOR**: Add validation and type hints to both models

- [x] 3. Implement ExtractedEntity and EntityMatch models
  - [x] 3.1 **RED**: Write tests for ExtractedEntity model
    - Test entity creation with NES-compatible structure
    - Test names list with bilingual NameParts
    - Test confidence_scores dict
    - _Requirements: 2.2, 2.3, Data Models - ExtractedEntity_
  
  - [x] 3.2 **GREEN**: Create `agni/models/entity.py` with ExtractedEntity dataclass
    - Fields following NES schema: type, sub_type, names, personal_details, electoral_details, organization_details, short_description, description, contacts, identifiers, tags, attributes, confidence_scores
    - Include `to_nes_entity()` method stub
  
  - [x] 3.3 **RED**: Write tests for EntityMatch model
    - Test EntityMatch creation with all fields
    - Test similarity_score is float between 0.0 and 1.0
    - _Requirements: 2.5, Data Models - EntityMatch_
  
  - [x] 3.4 **GREEN**: Create `agni/models/matching.py` with EntityMatch dataclass
    - Fields: nes_entity_id, nes_entity_name_en, nes_entity_name_ne, similarity_score, match_explanation
  
  - [x] 3.5 **REFACTOR**: Add validation for confidence scores and similarity scores

- [x] 4. Implement Result and ChangeRequest models
  - [x] 4.1 **RED**: Write tests for ExtractionResult and MatchingResult
    - Test ExtractionResult with metadata and entities list
    - Test MatchingResult with entity_matches dict
    - _Requirements: Data Models - ExtractionResult, MatchingResult_
  
  - [x] 4.2 **GREEN**: Create `agni/models/results.py` with both dataclasses
    - ExtractionResult: document_id, metadata, entities, extracted_at
    - MatchingResult: document_id, extraction_result, entity_matches, matched_at
  
  - [x] 4.3 **RED**: Write tests for EntityUpdate and ChangeRequest
    - Test ChangeRequest structure with all fields
    - Test JSON serialization round-trip (**Property 10**)
    - _Requirements: 3.1, 3.2, 3.3, Data Models - ChangeRequest_
  
  - [x] 4.4 **GREEN**: Create `agni/models/change_request.py` with both dataclasses
    - EntityUpdate: nes_entity_id, current_data, proposed_changes, explanation
    - ChangeRequest: id, document_id, metadata, entities_to_create, entities_to_update, explanations, status, feedback, created_at, processing_time, stage_times
    - Add JSON serialization support
  
  - [x] 4.5 **RED**: Write tests for PersistenceResult
    - Test success and failure cases
    - Test validation_errors list
    - _Requirements: 5.2, Data Models - PersistenceResult_
  
  - [x] 4.6 **GREEN**: Create `agni/models/persistence.py` with PersistenceResult dataclass
    - Fields: success, change_request_id, logged_at, validation_errors
  
  - [x] 4.7 **REFACTOR**: Add comprehensive validation and helper methods

- [x] 5. Implement DocumentProcessingState
  - [x] 5.1 **RED**: Write tests in `tests/test_state.py` for DocumentProcessingState
    - Test storing and retrieving document
    - Test storing and retrieving extraction_result
    - Test storing and retrieving matching_result
    - Test storing and retrieving change_request
    - Test storing and retrieving feedback
    - Test clear() method resets all state
    - _Requirements: Architecture - DocumentProcessingState_
  
  - [x] 5.2 **GREEN**: Create `agni/state.py` with DocumentProcessingState class
    - Implement in-memory storage attributes
    - Implement store methods for each stage
    - Implement clear() method
  
  - [x] 5.3 **REFACTOR**: Add thread-safety if needed, improve error handling

---

## Phase 3: Stage 1 - Document Processor (TDD)

- [x] 6. Implement file reading functionality
  - [x] 6.1 **RED**: Write tests in `tests/test_file_reader.py`
    - Test `read_txt()` with sample .txt file (**Property 2: round-trip**)
    - Test `read_md()` with sample .md file
    - Test `read_docx()` with sample .docx file
    - Test error handling: file not found, unsupported format, permission denied
    - _Requirements: 1.2, Error Handling - File Reading Errors_
  
  - [x] 6.2 **GREEN**: Create `agni/processors/file_reader.py` with file reading functions
    - Implement `read_txt()` for .txt files
    - Implement `read_md()` for .md files
    - Implement `read_docx()` for .docx files using python-docx
    - Implement `read_doc()` for .doc files using antiword or python-doc
    - Add error handling with clear error messages
  
  - [x] 6.3 **REFACTOR**: Extract common error handling, improve file format detection
  
  - [x] 6.4 Create test fixtures in `tests/fixtures/documents/`
    - Create sample .txt, .md, .docx files with Nepali and English content
    - Use authentic Nepali names and organizations

- [x] 7. Implement Processor class
  - [x] 7.1 **RED**: Write tests in `tests/test_processor.py`
    - Test Processor initialization with DocumentProcessingState
    - Test async `process()` accepts valid file paths and guidance (**Property 1**)
    - Test async `process()` stores Document in state
    - Test async `read_document()` delegates to correct file_reader function
    - Test error handling for invalid file paths
    - _Requirements: 1.1, 6.2, Stage 1 - Processor_
  
  - [x] 7.2 **GREEN**: Create `agni/processors/processor.py` with Processor class
    - Implement `__init__(state: DocumentProcessingState)`
    - Implement async `process(file_path, guidance, feedback)` method
    - Implement async `read_document(file_path)` method
    - Store Document in DocumentProcessingState
  
  - [x] 7.3 **REFACTOR**: Improve error messages, add logging, optimize file reading

---

## Phase 4: Stage 2 - AI Extraction (TDD)

- [x] 8. Implement extraction prompt and schema
  - [x] 8.1 **RED**: Write tests in `tests/test_extraction_schema.py`
    - Test extraction schema structure is valid JSON schema
    - Test prompt template includes all required sections
    - Test prompt template supports optional guidance and feedback
    - _Requirements: 2.1, 2.2, 2.3, 2.4, AI Integration Plan - Prompt Structure_
  
  - [x] 8.2 **GREEN**: Create extraction schema and prompt in `agni/extractors/prompts.py`
    - Define EXTRACTION_SCHEMA as dict with metadata and entities structure
    - Define EXTRACTION_INSTRUCTIONS as string template
    - Create helper function to build prompt with guidance and feedback
  
  - [x] 8.3 **REFACTOR**: Improve prompt clarity, add examples to schema

- [x] 9. Implement Extraction class
  - [x] 9.1 **RED**: Write tests in `tests/test_extraction.py`
    - Test Extraction initialization with state and llm_provider
    - Test async `extract()` returns ExtractionResult
    - Test async `extract()` stores result in state
    - Test metadata extraction completeness (**Property 3**)
    - Test entity extraction structure (**Property 4**)
    - Test entity attributes validity (**Property 5**)
    - Test confidence scores are bounded [0.0, 1.0] (**Property 6**)
    - Test error handling: LLM API failure, invalid response, timeout
    - _Requirements: 2.1, 2.2, 2.3, 2.4, Stage 2 - Extraction, Error Handling - AI Extraction Errors_
  
  - [x] 9.2 **GREEN**: Create `agni/extractors/extraction.py` with Extraction class
    - Implement `__init__(state: DocumentProcessingState, llm_provider: GoogleVertexAIProvider)`
    - Import GoogleVertexAIProvider from nes.services.scraping.providers.google
    - Implement async `extract(document, feedback)` method
    - Implement async `extract_with_ai(content, guidance, feedback)` method
    - Parse raw extraction into ExtractionResult
    - Validate confidence scores
    - Store ExtractionResult in DocumentProcessingState
  
  - [x] 9.3 **REFACTOR**: Improve error handling, add retry logic, optimize LLM calls

---

## Phase 5: Stage 3 - Entity Matching (TDD)

- [x] 10. Implement Matching class
  - [x] 10.1 **RED**: Write tests in `tests/test_matching.py`
    - Test Matching initialization with state and nes_db
    - Test async `match()` returns MatchingResult
    - Test async `match()` stores result in state
    - Test entity matching is attempted for all entities (**Property 7**)
    - Test async `match_entity()` returns list of EntityMatch objects
    - Test async `search_nes()` calls nes_db.search_entities()
    - Test bilingual matching (English and Nepali names)
    - Test error handling: NES unavailable, query timeout, invalid entity
    - _Requirements: 2.5, Stage 3 - Matching, NES Database Integration, Error Handling - NES Matching Errors_
  
  - [x] 10.2 **GREEN**: Create `agni/processors/matching.py` with Matching class
    - Implement `__init__(state: DocumentProcessingState, nes_db: InMemoryCachedReadDatabase)`
    - Import InMemoryCachedReadDatabase from nes.database.in_memory_cached_read_database
    - Implement async `match(extraction_result, feedback)` method
    - Implement async `match_entity(entity, feedback)` method
    - Implement async `search_nes(query, entity_type)` method
    - Calculate similarity scores
    - Store MatchingResult in DocumentProcessingState
  
  - [x] 10.3 **REFACTOR**: Improve similarity scoring algorithm, add caching, optimize queries

---

## Phase 6: Stage 4 - Review and Change Requests (TDD)

- [x] 11. Implement feedback parsing
  - [x] 11.1 **RED**: Write tests in `tests/test_feedback_parsing.py`
    - Test `parse_feedback()` with valid stage prefixes (**Property 16**)
    - Test `parse_feedback()` ignores invalid lines (**Property 17**)
    - Test `parse_feedback()` handles multi-line feedback
    - Test `parse_feedback()` handles empty feedback
    - _Requirements: Feedback Routing - Feedback Parsing_
  
  - [x] 11.2 **GREEN**: Implement `parse_feedback()` in `agni/reviewers/review.py`
    - Split feedback by newlines
    - Extract prefix from each line
    - Group by stage ('processor', 'extraction', 'matching')
    - Return dict mapping stage names to feedback lists
  
  - [x] 11.3 **REFACTOR**: Improve parsing robustness, add validation

- [x] 12. Implement Review class
  - [x] 12.1 **RED**: Write tests in `tests/test_review.py`
    - Test Review initialization with state
    - Test async `review()` generates ChangeRequest (**Property 8: structure completeness**)
    - Test async `review()` includes traceability (**Property 9**)
    - Test async `review()` separates entities_to_create and entities_to_update
    - Test async `review()` stores ChangeRequest in state
    - Test async `approve_change_request()` changes status (**Property 13**)
    - Test async `reject_change_request()` stores feedback (**Property 14**)
    - Test feedback is parsed and stored in state
    - _Requirements: 3.1, 3.2, 4.3, 4.4, 6.5, Stage 4 - Review, Feedback Routing_
  
  - [x] 12.2 **GREEN**: Complete `agni/reviewers/review.py` with Review class
    - Implement `__init__(state: DocumentProcessingState)`
    - Implement async `review(matching_result)` method
    - Implement async `approve_change_request(request_id)` method
    - Implement async `reject_change_request(request_id, feedback)` method
    - Generate EntityUpdate objects for matched entities
    - Include explanations for all changes
  
  - [x] 12.3 **REFACTOR**: Improve change request generation logic, add validation

---

## Phase 7: Pipeline Orchestration (TDD)

- [x] 13. Implement Pipeline class
  - [x] 13.1 **RED**: Write tests in `tests/test_pipeline.py`
    - Test Pipeline initialization with all components
    - Test async `run()` executes all stages in order
    - Test async `run()` tracks processing time and stage times
    - Test async `run()` returns ChangeRequest
    - Test async `reprocess_with_feedback()` routes feedback to stages
    - Test async `reprocess_with_feedback()` generates new ChangeRequest
    - Test all pipeline methods are async (**Property 18**)
    - _Requirements: Pipeline Orchestrator, Feedback Routing - Reprocessing with Feedback_
  
  - [x] 13.2 **GREEN**: Create `agni/pipeline.py` with Pipeline class
    - Implement `__init__(processor, extraction, matching, review, state)`
    - Implement async `run(file_path, guidance)` method
    - Implement async `reprocess_with_feedback(request_id)` method
    - Track timing for each stage
  
  - [x] 13.3 **REFACTOR**: Add error handling, improve timing accuracy, add logging

---

## Phase 8: Persistence Stub (TDD)

- [x] 14. Implement PersistenceStub
  - [x] 14.1 **RED**: Write tests in `tests/test_persistence.py`
    - Test async `persist()` validates ChangeRequest structure (**Property 15**)
    - Test async `persist()` returns success for valid requests
    - Test async `persist()` returns validation errors for invalid requests
    - Test async `persist()` logs operations
    - _Requirements: 5.1, 5.2, 5.3, Persistence Stub_
  
  - [x] 14.2 **GREEN**: Create `agni/persistence.py` with PersistenceStub class
    - Implement async `persist(change_request)` method
    - Validate ChangeRequest structure
    - Log persistence operation
    - Return PersistenceResult
  
  - [x] 14.3 **REFACTOR**: Improve validation logic, add detailed logging

---

## Phase 9: Interactive CLI (TDD)

- [x] 15. Implement CLI display functions
  - [x] 15.1 **RED**: Write tests in `tests/test_cli_display.py`
    - Test change request display includes all sections (**Property 11**)
    - Test low-confidence fields are highlighted (**Property 12**)
    - Test display formatting is readable
    - _Requirements: 4.1, 4.2, 6.3, CLI Interface_
  
  - [x] 15.2 **GREEN**: Create `agni/cli/display.py` with display functions
    - Implement `format_change_request()` function
    - Implement `highlight_low_confidence()` helper
    - Use rich library for colored output
  
  - [x] 15.3 **REFACTOR**: Improve formatting, add more visual indicators

- [x] 16. Implement CLI main application
  - [x] 16.1 **RED**: Write tests in `tests/test_cli_main.py`
    - Test main menu displays options
    - Test document submission flow accepts file path and guidance
    - Test review flow lists pending change requests
    - Test approval flow calls correct methods
    - Test rejection flow prompts for feedback
    - Test reprocessing flow works end-to-end
    - Test error handling returns to menu
    - _Requirements: 6.1, 6.2, 6.4, 6.5, CLI Interface, Error Handling - General Principles_
  
  - [x] 16.2 **GREEN**: Create `agni/cli/main.py` with CLI application
    - Use click or rich for interactive menus
    - Implement main menu
    - Implement document submission flow
    - Implement review flow
    - Implement approval/rejection/reprocessing flows
    - Add comprehensive error handling
  
  - [x] 16.3 **REFACTOR**: Improve UX, add progress indicators, improve error messages

---

## Phase 10: Integration Testing

- [x] 17. Create end-to-end integration tests
  - [x] 17.1 **RED**: Write integration test in `tests/test_integration.py`
    - Test complete workflow: submit → extract → match → review → persist
    - Use sample Nepali document with known entities
    - Verify all stages execute successfully
    - Verify change request is generated correctly
    - Verify persistence succeeds
    - _Requirements: Testing Strategy - Integration Testing_
  
  - [x] 17.2 **GREEN**: Make integration test pass
    - Fix any integration issues discovered
    - Ensure all components work together
  
  - [x] 17.3 **REFACTOR**: Add more integration test scenarios
    - Test with different document types
    - Test with feedback and reprocessing
    - Test error scenarios

- [x] 18. Create comprehensive test fixtures
  - Create sample documents in `tests/fixtures/documents/`
  - Include .txt, .md, .docx files with Nepali and English content
  - Use authentic Nepali names: नारायण खड्का, विद्या देवी भण्डारी
  - Use authentic organizations: नेपाल सरकार, राष्ट्रिय योजना आयोग
  - _Requirements: Testing Strategy - Test Data_

---

## Phase 11: Final Testing and Refinement

- [x] 19. Run full test suite and fix issues
  - Run pytest with all tests
  - Verify all unit tests pass
  - Verify all property-based tests pass with 100+ iterations
  - Verify integration tests pass
  - Fix any failing tests
  - Achieve high test coverage

- [x] 20. Final checkpoint - Manual testing and polish
  - Manually test CLI with real documents
  - Test with various Nepali documents
  - Test error scenarios
  - Improve error messages based on testing
  - Update documentation
  - Ask the user if questions arise

---

## TDD Principles Applied

Throughout this implementation:

1. **RED**: Always write the test first. The test should fail initially because the functionality doesn't exist yet.

2. **GREEN**: Write the minimal code needed to make the test pass. Don't over-engineer or add features not covered by tests.

3. **REFACTOR**: Once tests are green, improve the code quality:
   - Remove duplication
   - Improve naming
   - Extract functions/classes
   - Add error handling
   - Optimize performance
   - Keep tests passing throughout refactoring

4. **Test Coverage**: Every feature has corresponding tests. Property-based tests validate universal properties across many inputs.

5. **Incremental Development**: Build one small piece at a time, always keeping the codebase in a working state.

---

## Notes

- Each property-based test should run a minimum of 100 iterations
- All property-based tests must be tagged with comments: `# Feature: agni-ai-poc, Property {number}: {property_text}`
- Use authentic Nepali names and entities in all test data
- All pipeline methods must be async
- Error handling should fail gracefully and provide clear user guidance
- Configuration extracts project_id from GOOGLE_APPLICATION_CREDENTIALS JSON file
