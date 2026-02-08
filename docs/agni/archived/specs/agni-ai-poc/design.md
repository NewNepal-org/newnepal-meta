# Design Document: Agni AI POC

## Overview

Agni AI is an AI-assisted data enrichment system for the Nepal Entity Service (NES). This POC validates the core workflow: document ingestion → AI extraction → change request generation → human review → persistence stub. The system uses an interactive CLI to process local document files (.txt, .md, .doc, .docx) and extract structured entity data with AI assistance.

The design emphasizes simplicity and rapid validation. By focusing on file-based input and CLI interaction, we can quickly test the AI extraction quality and human review workflow without building web infrastructure.

## Architecture

### High-Level Architecture

The system follows a four-stage pipeline architecture:

```
┌─────────────────┐
│   CLI Interface │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│              Four-Stage Pipeline                          │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Stage 1:   │  │   Stage 2:   │  │   Stage 3:   │   │
│  │  Processor   │─▶│  Extraction  │─▶│   Matching   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│         │                  │                  │           │
│         │                  │                  │           │
│         └──────────────────┴──────────────────┘           │
│                            │                              │
│                            ▼                              │
│                 ┌─────────────────────┐                  │
│                 │ DocumentProcessing  │                  │
│                 │       State         │                  │
│                 │   (In-Memory)       │                  │
│                 └─────────────────────┘                  │
│                            │                              │
│                            ▼                              │
│                    ┌──────────────┐                      │
│                    │   Stage 4:   │                      │
│                    │    Review    │                      │
│                    └──────────────┘                      │
│                            │                              │
│                            ▼                              │
│                    ┌──────────────┐                      │
│                    │ Persistence  │                      │
│                    │     Stub     │                      │
│                    └──────────────┘                      │
└──────────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│   LLM Provider  │  │  NES Database   │
│   (Vertex AI)   │  │   (Read-only)   │
└─────────────────┘  └─────────────────┘
```

### Pipeline Stages

**Stage 1: Processor**
- Accept document file path and optional guidance
- Read files from disk (.txt, .md, .doc, .docx)
- Extract text content from various formats
- Store document in DocumentProcessingState
- Pass document to Extraction stage

**Stage 2: Extraction**
- Extract document metadata (author, date, type, source) using AI
- Extract person and organization entities with bilingual names
- Extract entity attributes (roles, positions, affiliations)
- Assign confidence scores to all extracted fields
- Store extraction results in DocumentProcessingState
- Pass extracted entities to Matching stage

**Stage 3: Matching**
- Use InMemoryCachedReadDatabase.search_entities() to query NES
- Compare extracted entities against known entities
- Return match candidates with similarity scores
- Support bilingual matching (Nepali and English)
- Leverage in-memory cache for fast lookups
- Store matching results in DocumentProcessingState
- Pass complete results to Review stage

**Stage 4: Review**
- Generate change requests from extraction and matching results
- Present change requests for human review via CLI
- Highlight low-confidence extractions (< 0.7)
- Collect approval/rejection feedback
- Parse feedback and route to appropriate pipeline stage
- Support reprocessing with feedback as context
- Pass approved change requests to Persistence Stub

**Supporting Components**

**CLI Interface**
- Present interactive menu for document submission and review
- Accept file paths and optional guidance text
- Display change requests in readable format
- Collect approval/rejection feedback

**DocumentProcessingState (In-Memory Storage)**
- Store current document being processed
- Store extraction results from Stage 2
- Store matching results from Stage 3
- Store change requests from Stage 4
- Store reviewer feedback
- Maintain processing state for the session

**Persistence Stub**
- Validate change request structure
- Log persistence operations
- Return success without modifying databases

## Components and Interfaces

### DocumentProcessingState

```python
class DocumentProcessingState:
    def __init__(self):
        self.current_document: Optional[Document] = None
        self.extraction_result: Optional[ExtractionResult] = None
        self.matching_result: Optional[MatchingResult] = None
        self.change_request: Optional[ChangeRequest] = None
        self.feedback: Optional[Dict[str, List[str]]] = None
        
    def store_document(self, document: Document) -> None:
        """Store document from Stage 1 (Processor)."""
        
    def store_extraction_result(self, result: ExtractionResult) -> None:
        """Store extraction result from Stage 2 (Extraction)."""
        
    def store_matching_result(self, result: MatchingResult) -> None:
        """Store matching result from Stage 3 (Matching)."""
        
    def store_change_request(self, request: ChangeRequest) -> None:
        """Store change request from Stage 4 (Review)."""
        
    def store_feedback(self, feedback: Dict[str, List[str]]) -> None:
        """Store parsed reviewer feedback for reprocessing."""
        
    def clear(self) -> None:
        """Clear all stored state."""
```

### Stage 1: Processor

```python
class Processor:
    def __init__(self, state: DocumentProcessingState):
        self.state = state
        
    async def process(
        self, 
        file_path: str, 
        guidance: Optional[str] = None,
        feedback: Optional[List[str]] = None
    ) -> Document:
        """
        Stage 1: Process document file.
        
        Accept document file and optional guidance.
        Read and extract text content from file.
        Store document in DocumentProcessingState.
        Return Document object for next stage.
        
        Feedback (if provided) is combined with guidance to provide
        additional context for document processing and extraction.
        """
        
    async def read_document(self, file_path: str) -> str:
        """
        Read and extract text from document file.
        Supports .txt, .md, .doc, .docx formats.
        """
```

### Stage 2: Extraction

```python
class Extraction:
    def __init__(self, state: DocumentProcessingState, llm_provider: GoogleVertexAIProvider):
        self.state = state
        self.llm_provider = llm_provider
        
    async def extract(
        self, 
        document: Document,
        feedback: Optional[List[str]] = None
    ) -> ExtractionResult:
        """
        Stage 2: Extract structured data from document.
        
        Extract metadata (author, date, type, source).
        Extract entities (persons, organizations) with bilingual names.
        Extract entity attributes (roles, positions, affiliations).
        Assign confidence scores to all fields.
        
        If feedback is provided, include it as context in AI prompt.
        Store result in DocumentProcessingState.
        Return ExtractionResult for next stage.
        """
        
    async def extract_with_ai(
        self, 
        content: str,
        guidance: Optional[str] = None,
        feedback: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Call LLM to extract structured data.
        Returns raw extraction result with metadata and entities.
        """
```

### Stage 3: Matching

```python
class Matching:
    def __init__(self, state: DocumentProcessingState, nes_db: InMemoryCachedReadDatabase):
        self.state = state
        self.nes_db = nes_db
        
    async def match(
        self, 
        extraction_result: ExtractionResult,
        feedback: Optional[List[str]] = None
    ) -> MatchingResult:
        """
        Stage 3: Match extracted entities against NES database.
        
        For each extracted entity:
        - Search NES database using search_entities()
        - Compare against known entities
        - Return match candidates with similarity scores
        - Support bilingual matching (Nepali and English)
        
        If feedback is provided, use it to override or guide matching decisions.
        Store result in DocumentProcessingState.
        Return MatchingResult for next stage.
        """
        
    async def match_entity(
        self, 
        entity: ExtractedEntity,
        feedback: Optional[List[str]] = None
    ) -> List[EntityMatch]:
        """
        Match single entity against NES database.
        Returns list of potential matches with similarity scores.
        """
        
    async def search_nes(
        self, 
        query: str,
        entity_type: str
    ) -> List[Entity]:
        """
        Search NES database using InMemoryCachedReadDatabase.search_entities().
        Returns full NES Entity objects matching the query.
        """
```

### Stage 4: Review

```python
class Review:
    def __init__(self, state: DocumentProcessingState):
        self.state = state
        
    async def review(
        self, 
        matching_result: MatchingResult
    ) -> ChangeRequest:
        """
        Stage 4: Generate change request for human review.
        
        Create change request from extraction and matching results.
        Include metadata, entities to create/update, and explanations.
        Store change request in DocumentProcessingState.
        Return ChangeRequest for display.
        """
        
    async def approve_change_request(self, request_id: str) -> None:
        """Mark change request as approved and ready for persistence."""
        
    async def reject_change_request(
        self, 
        request_id: str, 
        feedback: str
    ) -> None:
        """
        Reject change request with raw feedback text.
        Parse feedback and store for reprocessing.
        
        Feedback should use prefixes to indicate target stage:
        - "processor: <feedback>" for Stage 1 (document processing guidance)
        - "extraction: <feedback>" for Stage 2 (metadata and entity extraction)
        - "matching: <feedback>" for Stage 3 (entity matching decisions)
        
        The raw feedback text is stored in ChangeRequest.feedback.
        The parsed feedback dict is stored in DocumentProcessingState.feedback.
        """
        
    def parse_feedback(self, feedback: str) -> Dict[str, List[str]]:
        """
        Parse raw feedback text into stage-specific instructions.
        
        Returns dict with keys: 'processor', 'extraction', 'matching'
        Each key maps to a list of feedback items for that stage.
        Lines without a recognized prefix are ignored.
        """
```

### Pipeline Orchestrator

```python
class Pipeline:
    def __init__(
        self,
        processor: Processor,
        extraction: Extraction,
        matching: Matching,
        review: Review,
        state: DocumentProcessingState
    ):
        self.processor = processor
        self.extraction = extraction
        self.matching = matching
        self.review = review
        self.state = state
        
    async def run(
        self,
        file_path: str,
        guidance: Optional[str] = None
    ) -> ChangeRequest:
        """
        Run complete pipeline: Processor → Extraction → Matching → Review.
        Returns change request ready for human review.
        """
        # Stage 1: Process document
        document = await self.processor.process(file_path, guidance)
        
        # Stage 2: Extract structured data
        extraction_result = await self.extraction.extract(document)
        
        # Stage 3: Match entities
        matching_result = await self.matching.match(extraction_result)
        
        # Stage 4: Generate change request
        change_request = await self.review.review(matching_result)
        
        return change_request
        
    async def reprocess_with_feedback(
        self,
        request_id: str
    ) -> ChangeRequest:
        """
        Reprocess document using stored feedback.
        Routes feedback to appropriate pipeline stages.
        
        The parsed feedback dict is retrieved from DocumentProcessingState.feedback.
        """
        feedback = self.state.feedback
        document = self.state.current_document
        
        # Stage 1: Reprocess with processor feedback
        document = await self.processor.process(
            document.file_path,
            document.guidance,
            feedback.get('processor', [])
        )
        
        # Stage 2: Extract with feedback
        extraction_result = await self.extraction.extract(
            document, 
            feedback.get('extraction', [])
        )
        
        # Stage 3: Match with feedback
        matching_result = await self.matching.match(
            extraction_result,
            feedback.get('matching', [])
        )
        
        # Stage 4: Generate new change request
        change_request = await self.review.review(matching_result)
        
        return change_request
```

### Persistence Stub

```python
class PersistenceStub:
    async def persist(self, change_request: ChangeRequest) -> PersistenceResult:
        """
        Validate and log persistence operation.
        Does not modify external databases.
        """
```

## Data Models

### Document

```python
@dataclass
class Document:
    id: str  # Unique processing identifier
    file_path: str
    content: str
    guidance: Optional[str]
    submitted_at: datetime
```

### DocumentMetadata

```python
@dataclass
class DocumentMetadata:
    author: Optional[str]
    publication_date: Optional[date]
    document_type: Optional[str]  # e.g., "press release", "report", "article"
    source: Optional[str]  # Original source/publisher
    confidence_scores: Dict[str, float]  # Field name -> confidence
```

### Entity

The system will use the existing `Entity` model from NES (`nes.core.models.entity.Entity`). For extraction purposes, we'll work with a rich extraction format that closely matches the NES schema:

```python
@dataclass
class ExtractedEntity:
    """Entity representation for AI extraction matching NES schema structure."""
    type: str  # "person" or "organization"
    sub_type: Optional[str]  # EntitySubType value (e.g., "government_body", "political_party")
    
    # Names following NES Name model structure
    names: List[Dict[str, Any]]  # List of Name objects with kind, en/ne NameParts
    
    # Entity-specific details
    personal_details: Optional[Dict[str, Any]] = None  # For Person: birth_date, gender, positions, education, etc.
    electoral_details: Optional[Dict[str, Any]] = None  # For Person: candidacies
    
    # Organization-specific fields
    organization_details: Optional[Dict[str, Any]] = None  # For Organization: address, government_type, etc.
    
    # Common fields
    short_description: Optional[Dict[str, str]] = None  # LangText: {"en": "...", "ne": "..."}
    description: Optional[Dict[str, str]] = None  # LangText: {"en": "...", "ne": "..."}
    contacts: Optional[List[Dict[str, str]]] = None  # List of Contact objects
    identifiers: Optional[List[Dict[str, str]]] = None  # List of ExternalIdentifier objects
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None  # Additional custom attributes
    
    # Extraction metadata
    confidence_scores: Dict[str, float]  # Field path -> confidence (e.g., "names.0.en.full": 0.95)
    
    def to_nes_entity(self, slug: str, version_summary: VersionSummary) -> Entity:
        """Convert to full NES Entity model (Person, Organization, or Location)."""
        # Implementation will map extracted data to appropriate NES Entity subclass
        pass
```

**Schema Alignment with NES:**

The extraction format follows NES entity structure:

**Person Entities:**
- `names`: List of Name objects with `kind` (PRIMARY/ALIAS/etc.), `en`/`ne` NameParts (full, given, middle, family)
- `personal_details`: PersonDetails with birth_date, gender, address, father_name, mother_name, spouse_name, education (list of Education), positions (list of Position)
- `electoral_details`: ElectoralDetails with candidacies (list of Candidacy)

**Organization Entities:**
- `names`: Same structure as Person
- `sub_type`: One of POLITICAL_PARTY, GOVERNMENT_BODY, NGO, INTERNATIONAL_ORG, HOSPITAL
- `organization_details`: Subtype-specific fields:
  - PoliticalParty: address, party_chief, registration_date, symbol
  - GovernmentBody: government_type (federal/provincial/local)
  - Hospital: beds, services, ownership, address

**Common Fields (All Entities):**
- `short_description`/`description`: LangText with en/ne values
- `contacts`: List of Contact (type, value) - EMAIL, PHONE, URL, social media
- `identifiers`: List of ExternalIdentifier (scheme, value, url) - WIKIPEDIA, WIKIDATA, social media
- `tags`: List of string tags for categorization
- `attributes`: Flexible dict for additional custom data

**Note:** The extraction service will produce `ExtractedEntity` objects with rich NES-compatible structure which will be converted to full NES `Entity` objects (Person, Organization, or Location) during the change request generation phase.

### EntityMatch

```python
@dataclass
class EntityMatch:
    nes_entity_id: str
    nes_entity_name_en: Optional[str]
    nes_entity_name_ne: Optional[str]
    similarity_score: float
    match_explanation: str
```

### ExtractionResult

```python
@dataclass
class ExtractionResult:
    document_id: str
    metadata: DocumentMetadata
    entities: List[ExtractedEntity]
    extracted_at: datetime
```

### MatchingResult

```python
@dataclass
class MatchingResult:
    document_id: str
    extraction_result: ExtractionResult
    entity_matches: Dict[int, List[EntityMatch]]  # Entity index -> matches
    matched_at: datetime
```

### ChangeRequest

```python
@dataclass
class EntityUpdate:
    """Represents an update to an existing entity."""
    nes_entity_id: str
    current_data: Dict[str, Any]  # Current entity data from NES
    proposed_changes: Dict[str, Any]  # Proposed changes with new/updated fields
    explanation: str

@dataclass
class ChangeRequest:
    id: str
    document_id: str
    metadata: DocumentMetadata
    entities_to_create: List[ExtractedEntity]  # Will be converted to NES Entity on persistence
    entities_to_update: List[EntityUpdate]  # Rich update structure with before/after
    explanations: Dict[str, str]  # Field path -> explanation
    status: str  # "pending", "approved", "rejected"
    feedback: Optional[str]  # Raw feedback text with stage prefixes (processor:, extraction:, matching:)
    created_at: datetime
    processing_time: Optional[float] = None  # Total processing time in seconds
    stage_times: Optional[Dict[str, float]] = None  # Stage name -> time in seconds
```

### PersistenceResult

```python
@dataclass
class PersistenceResult:
    success: bool
    change_request_id: str
    logged_at: datetime
    validation_errors: List[str]
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Document submission accepts valid file formats

*For any* valid file path with extension .txt, .md, .doc, or .docx, and any optional guidance text, submitting the document should return a Document object and store the document for processing.

**Validates: Requirements 1.1, 6.2**

### Property 2: File reading round-trip preserves content

*For any* document file with known text content, reading and extracting the text should return content equivalent to the original.

**Validates: Requirements 1.2**

### Property 3: Metadata extraction completeness

*For any* processed document, the extraction result should contain all required metadata fields (author, publication_date, document_type, source), though values may be None if not found in the document.

**Validates: Requirements 2.1**

### Property 4: Entity extraction structure

*For any* processed document, all extracted entities should have a valid type ("person" or "organization"), and should include bilingual names when available in the document content.

**Validates: Requirements 2.2**

### Property 5: Entity attributes validity

*For any* extraction result, all entity attributes should be non-empty dictionaries containing roles, positions, or affiliations.

**Validates: Requirements 2.3**

### Property 6: Confidence scores are bounded

*For any* extraction result, all confidence scores (in metadata and entities) should be between 0.0 and 1.0 inclusive.

**Validates: Requirements 2.4**

### Property 7: Entity matching is attempted

*For any* extraction result with entities, the result should include entity matches for each extracted entity (matches may be empty if no candidates found).

**Validates: Requirements 2.5**

### Property 8: Change request structure completeness

*For any* change request generated from an extraction result, the change request should contain metadata, lists of entities to create and update, and explanations.

**Validates: Requirements 3.1**

### Property 9: Change request traceability

*For any* change request, it should include a document_id reference and explanations should be provided for all proposed changes.

**Validates: Requirements 3.2**

### Property 10: Change request serialization round-trip

*For any* change request, serializing to JSON and then deserializing should produce an equivalent change request with all fields preserved.

**Validates: Requirements 3.3**

### Property 11: Change request display completeness

*For any* change request displayed to a reviewer, the display output should include all sections: metadata, entity creations, and entity updates with before/after comparisons.

**Validates: Requirements 4.1, 6.3**

### Property 12: Low-confidence highlighting

*For any* change request display, all fields with confidence scores below 0.7 should be marked or highlighted as low-confidence. (Note: The 0.7 threshold is hardcoded in the display logic.)

**Validates: Requirements 4.2**

### Property 13: Approval state transition

*For any* pending change request, approving it should change its status to "approved".

**Validates: Requirements 4.3**

### Property 14: Feedback storage and reprocessing

*For any* rejected change request with feedback, the raw feedback text should be stored in ChangeRequest.feedback, the parsed feedback dict should be stored in DocumentProcessingState.feedback, and reprocessing should include that feedback as context to the appropriate pipeline stages.

**Validates: Requirements 4.4, 6.5**

### Property 16: Feedback parsing correctness

*For any* feedback text with valid stage prefixes (processor:, extraction:, matching:), parsing should correctly route each feedback item to the appropriate stage key in the returned dict.

**Validates: Feedback Routing section**

### Property 17: Feedback parsing handles invalid input

*For any* feedback text with lines lacking recognized prefixes or malformed structure, parsing should ignore those lines and return only valid feedback items grouped by stage.

**Validates: Error Handling section**

### Property 15: Persistence validation

*For any* change request with invalid or incomplete structure, calling the persistence stub should return validation errors and not report success.

**Validates: Requirements 5.2**

### Property 18: Async consistency

*For all* pipeline stages and their methods, async methods should be consistently used throughout the pipeline to maintain uniform execution patterns.

**Validates: Architecture consistency**

## Feedback Routing

When a reviewer rejects a change request, they provide feedback as free-form text. The system uses simple prefix-based routing to direct feedback to the appropriate pipeline stage:

### Feedback Format

Feedback should use one of these prefixes to target specific pipeline stages:

- **`processor:`** - Feedback for Stage 1 (file reading, document guidance)
- **`extraction:`** - Feedback for Stage 2 (metadata, entities, attributes)
- **`matching:`** - Feedback for Stage 3 (entity matching decisions)

### Examples

```
processor: Focus on the section titled "कार्यकारी सारांश" for entity extraction
extraction: The author is actually "राम बहादुर थापा" not "राम थापा"
extraction: The person's role is "सचिव" (Secretary), not "मन्त्री" (Minister)
matching: This is a different person than the existing entity, create a new one
```

### Multi-line Feedback

Reviewers can provide multiple feedback items, one per line:

```
processor: Ignore the footer section when extracting entities
extraction: Publication date should be 2024-01-15
extraction: Organization name in Nepali is "नेपाल सरकार"
matching: Match this to entity:organization/government_body/nepal-government
```

### Feedback Parsing

The `Review.parse_feedback()` method will:

1. Split feedback text by newlines
2. Extract prefix from each line (text before first `:`)
3. Group feedback by stage ('processor', 'extraction', 'matching')
4. Return dict mapping stage names to lists of feedback items

Example:
```python
feedback_text = """
processor: Focus on the executive summary section
extraction: Author is "राम बहादुर थापा"
matching: Create new entity, don't match
"""

parsed = review.parse_feedback(feedback_text)
# Returns:
# {
#   'processor': ['Focus on the executive summary section'],
#   'extraction': ['Author is "राम बहादुर थापा"'],
#   'matching': ['Create new entity, don\'t match']
# }
```

### Reprocessing with Feedback

When reprocessing a rejected change request via `Pipeline.reprocess_with_feedback()`:

1. **Stage 1 (Processor)**: Re-reads the original document with `feedback['processor']` as additional guidance
2. **Stage 2 (Extraction)**: Receives `feedback['extraction']` as additional context in AI prompt
3. **Stage 3 (Matching)**: Receives `feedback['matching']` to override or guide matching decisions
4. **Stage 4 (Review)**: Generates new change request from updated results

The pipeline orchestrator routes feedback to the appropriate stages automatically.

## Error Handling

### File Reading Errors

- **Unsupported file format**: Return clear error message listing supported formats
- **File not found**: Return error with file path and suggestion to check path
- **File read permission denied**: Return error indicating permission issue
- **Corrupted file**: Return error indicating file cannot be parsed

### AI Extraction Errors

- **LLM API failure**: Retry with exponential backoff (max 3 attempts), then fail with clear error
- **Invalid LLM response**: Log raw response, attempt to parse partial results, return what can be extracted
- **Rate limiting**: Implement backoff and queue requests
- **Timeout**: Set reasonable timeout (60s), fail gracefully with partial results if available

### NES Matching Errors

- **NES database unavailable**: Log error, continue with empty match results (matching is optional)
- **Query timeout**: Return empty matches for that entity, continue processing
- **Invalid entity format**: Skip matching for that entity, log warning

### Review Errors

- **Invalid feedback format**: Validate feedback structure, return error if malformed
- **Change request not found**: Return clear error with available request IDs

### Persistence Errors

- **Invalid change request structure**: Return validation errors listing missing/invalid fields
- **Logging failure**: Attempt to log to stderr, continue with warning

### General Error Handling Principles

1. **Fail gracefully**: Never crash the CLI, always return to menu
2. **Clear error messages**: Include context and suggested actions
3. **Partial results**: When possible, return partial results rather than failing completely
4. **Logging**: Log all errors with full context for debugging
5. **User guidance**: Provide actionable next steps in error messages

## Testing Strategy

### Unit Testing

We will use **pytest** as the testing framework for Python. Unit tests will cover:

- **File reading**: Test each supported format (.txt, .md, .doc, .docx) with sample files
- **Data model validation**: Test serialization/deserialization of all data models
- **Error handling**: Test each error condition returns appropriate error messages
- **NES matching logic**: Test similarity scoring and match ranking
- **Change request generation**: Test that extraction results correctly map to change requests

### Property-Based Testing

We will use **Hypothesis** for property-based testing in Python. Each property-based test will:

- Run a minimum of 100 iterations
- Be tagged with a comment referencing the correctness property from this design document
- Use the format: `# Feature: agni-ai-poc, Property {number}: {property_text}`

Property-based tests will cover:

- **Property 1**: Generate random file paths with valid extensions and guidance text
- **Property 2**: Create files with random content, read them, verify content matches
- **Property 3**: Generate random extraction results, verify metadata structure
- **Property 4**: Generate random entities, verify type and name structure
- **Property 5**: Generate random extraction results, verify attribute validity
- **Property 6**: Generate random extraction results, verify all confidence scores in [0.0, 1.0]
- **Property 7**: Generate random extraction results with entities, verify matches exist
- **Property 8**: Generate random change requests, verify structure completeness
- **Property 9**: Generate random change requests, verify traceability fields present
- **Property 10**: Generate random change requests, test JSON round-trip
- **Property 11**: Generate random change requests, verify display includes all sections
- **Property 12**: Generate random change requests with varying confidence scores, verify highlighting
- **Property 13**: Generate random pending change requests, approve them, verify status change
- **Property 14**: Generate random change requests, reject with feedback, verify raw text in ChangeRequest.feedback and parsed dict in DocumentProcessingState.feedback, verify reprocessing uses parsed feedback
- **Property 15**: Generate invalid change requests, verify persistence validation catches errors
- **Property 16**: Generate random feedback text with various stage prefixes, verify parsing correctly routes to stage keys
- **Property 17**: Generate feedback with invalid/missing prefixes, verify parser ignores invalid lines
- **Property 18**: Verify all pipeline stage methods are async and can be awaited

### Integration Testing

Integration tests will verify:

- **End-to-end workflow**: Submit document → extract → review → persist
- **CLI interaction**: Test menu navigation and user input handling
- **LLM integration**: Test with real LLM API (using test API key)
- **NES database integration**: Test with test NES database instance

### Test Data

All test data will use authentic Nepali names and entities:

- **Persons**: नारायण खड्का (Narayan Khadka), विद्या देवी भण्डारी (Bidya Devi Bhandari)
- **Organizations**: नेपाल सरकार (Nepal Government), राष्ट्रिय योजना आयोग (National Planning Commission)
- **Documents**: Sample press releases, government reports, news articles in Nepali and English

## Implementation Notes

### Technology Stack

- **Language**: Python 3.12+
- **LLM Integration**: Google Vertex AI (gemini-2.5-flash) via GoogleVertexAIProvider from NES
- **Document Parsing**: 
  - `python-docx` for .docx files
  - `python-doc` or `antiword` for .doc files
  - Built-in file reading for .txt and .md
- **CLI Framework**: `click` or `rich` for interactive menus
- **Testing**: pytest + hypothesis
- **Data Validation**: pydantic for data models (reuse NES Entity model)
- **JSON Serialization**: Built-in json module with custom encoders
- **NES Integration**: 
  - Import `nes.core.models.entity.Entity` from NepalEntityService
  - Use `nes.database.in_memory_cached_read_database.InMemoryCachedReadDatabase` for entity matching
  - Use `nes.services.scraping.providers.google.GoogleVertexAIProvider` for AI extraction

### Configuration

Configuration will be managed via environment variables and a config file:

```python
# .env
NES_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
NES_DATABASE_URL=postgresql://...
LOG_LEVEL=INFO
```

### AI Integration Plan

**LLM Provider:** Google Vertex AI (gemini-2.5-flash)
- Use existing `GoogleVertexAIProvider` from NepalEntityService
- Vertex AI provides enterprise-grade reliability and security
- Single API call per document to extract all information
- Structured output using JSON schema with `response_schema` parameter

**Extraction Strategy:**

Stage 2 (Extraction) will use `GoogleVertexAIProvider.extract_structured_data()` to make a single LLM call that extracts:
1. Document metadata (author, publication_date, document_type, source)
2. All entities (persons and organizations) with bilingual names
3. Entity attributes (roles, positions, affiliations)
4. Confidence scores for each extracted field

**Implementation:**

```python
from nes.services.scraping.providers.google import GoogleVertexAIProvider

# In Extraction.__init__
provider = GoogleVertexAIProvider(
    project_id=os.environ["NES_PROJECT_ID"],
    model_id="gemini-2.5-flash",
    temperature=0.3,
)

# In Extraction.extract_with_ai()
extraction_schema = {
    "type": "object",
    "properties": {
        "metadata": {...},
        "entities": {...}
    }
}

result = await provider.extract_structured_data(
    text=document_content,
    schema=extraction_schema,
    instructions=EXTRACTION_INSTRUCTIONS
)
```

**Prompt Structure:**

```
You are extracting structured information from a Nepali government document.

Document:
{document_content}

{optional_guidance}

{feedback_context}

Extract the following information in JSON format:
1. Metadata: author, publication_date, document_type, source
2. Entities: persons and organizations with Nepali and English names
3. Attributes: roles, positions, affiliations for each entity

For each extracted field, provide a confidence score between 0.0 and 1.0.

Return JSON with this structure:
{
  "metadata": {
    "author": {"value": "...", "confidence": 0.9},
    "publication_date": {"value": "2024-01-15", "confidence": 0.95},
    "document_type": {"value": "press_release", "confidence": 0.8},
    "source": {"value": "...", "confidence": 0.9}
  },
  "entities": [
    {
      "type": "person",
      "name_en": "Ram Bahadur Thapa",
      "name_ne": "राम बहादुर थापा",
      "attributes": {
        "role": "Secretary",
        "organization": "Ministry of Finance"
      },
      "confidence_scores": {
        "name_en": 0.95,
        "name_ne": 0.9,
        "role": 0.85
      }
    }
  ]
}
```

**Feedback Integration:**

When reprocessing with feedback, the prompt will include phase-specific feedback:

```
{feedback_context}

Previous extraction had these issues:
- Metadata: {metadata_feedback}
- Entity extraction: {entity_feedback}

Please correct these issues in your extraction.
```

**Cost Optimization:**

- Use Gemini 2.5 Flash for excellent cost/performance ratio
- Single call per document (no separate calls for metadata, entities, etc.)
- GoogleVertexAIProvider includes built-in token usage tracking
- Vertex AI offers competitive pricing and excellent multilingual support for Nepali/English
- Built-in rate limiting and retry logic with exponential backoff

### NES Database Integration

The POC will use `InMemoryCachedReadDatabase` from NepalEntityService:

- **search_entities()**: Search by name (bilingual), entity type, and attributes
- **In-memory cache**: Fast lookups without database queries
- **Read-only**: No write operations needed for matching
- **Async interface**: All database operations are async

The matcher will use `search_entities(query, entity_type)` to find potential matches by searching entity names in both English and Nepali.

### Future Enhancements (Out of Scope for POC)

- Web-based UI for review
- Batch document processing
- Actual NES database persistence
- Entity disambiguation with human input
- Feedback-based model fine-tuning
- Multi-user support with authentication
- Document version tracking
- Export to various formats
