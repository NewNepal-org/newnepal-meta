# Design Document: Agni Django Module

## Overview

The Agni Django Module integrates AI-assisted document processing into the JawafdehiAPI Django application. It provides a UI in the Django admin panel for data enrichment specialists to process documents, extract entities using AI, resolve entity matches against the Nepal Entity Service (NES), and persist approved changes.

### Design Goals

1. **Seamless Integration**: Integrate with existing JawafdehiAPI Django admin infrastructure
2. **Session-Based Processing**: Use NES AgniService's session-based extraction pipeline
3. **Human-in-the-Loop**: Support user review, feedback, and approval of AI extractions via conversations
4. **Bilingual Support**: Full English/Nepali support throughout the workflow

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Django admin panel UI | Leverages existing auth, admin infrastructure; no separate frontend needed |
| NES AgniService as core | Reuses proven extraction pipeline from `nes.services.agni` |
| Session-based workflow | Supports iterative refinement with conversation threads |
| Direct NES integration | No API calls - imports NES models and services directly |

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           JawafdehiAPI                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Agni Django Module                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │   │
│  │  │   Admin      │  │   Django     │  │   Protocol           │  │   │
│  │  │   Views      │  │   Models     │  │   Implementations    │  │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │   │
│  │         │                 │                      │              │   │
│  │         └─────────────────┼──────────────────────┘              │   │
│  │                           │                                      │   │
│  └───────────────────────────┼──────────────────────────────────────┘   │
│                              │                                          │
│  ┌───────────────────────────┼──────────────────────────────────────┐   │
│  │                    NES Agni Service (imported)                    │   │
│  │  ┌──────────────┐  ┌──────┴───────┐  ┌──────────────────────┐   │   │
│  │  │ AgniService  │  │   Models     │  │   Protocols          │   │   │
│  │  │              │  │ (dataclasses)│  │   (interfaces)       │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    NES Core (imported)                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │   │
│  │  │   Entity     │  │   Search     │  │   Database           │   │   │
│  │  │   Models     │  │   Services   │  │   (Direct)           │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### Processing Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Begin     │    │  Extract    │    │  Extract    │    │   Persist   │
│   Session   │───▶│  Metadata   │───▶│  Entities   │───▶│   Changes   │
│             │    │             │    │  + Resolve  │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                  │                  │                  │
      ▼                  ▼                  ▼                  ▼
 ┌─────────┐       ┌─────────┐       ┌─────────┐       ┌─────────┐
 │ Session │       │Metadata │       │Resolved │       │ Queued  │
 │ Created │       │ + Conv  │       │Entities │       │ Changes │
 └─────────┘       └─────────┘       └─────────┘       └─────────┘
```

## Components and Interfaces

### Django App Structure

```
services/jawafdehi-api/agni/
├── __init__.py
├── admin.py              # Django Admin configuration and views
├── apps.py               # App configuration
├── models.py             # Django ORM models (session storage, change queue)
├── services/
│   ├── __init__.py
│   ├── genai.py          # GenAIService protocol implementation
│   ├── search.py         # SearchService protocol implementation
│   └── persistence.py    # Persistence protocol implementation
└── migrations/
    └── __init__.py
```

### Core Service (from NES)

The core extraction logic is provided by `nes.services.agni.AgniService`:

```python
from nes.services.agni import AgniService, AgniExtractionSession

class AgniService:
    """Orchestrates entity extraction and resolution pipeline.
    
    Imported from: nes.services.agni
    """
    
    def __init__(
        self,
        search: SearchService,
        genai: GenAIService,
        persistence: Persistence,
    ):
        """Initialize with protocol implementations."""
        pass

    def begin_session(
        self, document: Path, guidance: Optional[str] = None
    ) -> AgniExtractionSession:
        """Begin a new extraction session with a document."""
        pass

    def extract_metadata(
        self, session: AgniExtractionSession
    ) -> AgniExtractionSession:
        """Extract document metadata using AI.
        
        Uses the METADATA_EXTRACTION conversation for feedback.
        """
        pass

    def extract_entities(
        self, session: AgniExtractionSession
    ) -> AgniExtractionSession:
        """Extract entities from document using AI.
        
        Requires metadata to be extracted first.
        Uses the ENTITY_EXTRACTION conversation for feedback.
        """
        pass

    def set_nes_id_for_extracted_entity(
        self, session: AgniExtractionSession, entity_index: int, nes_id: str
    ) -> AgniExtractionSession:
        """Set the matched NES ID for an extracted entity (user disambiguation)."""
        pass

    def post_message_to_metadata(
        self, session: AgniExtractionSession, text: str
    ) -> AgniExtractionSession:
        """Post feedback to metadata extraction conversation."""
        pass

    def post_message_to_entity_extraction(
        self, session: AgniExtractionSession, text: str
    ) -> AgniExtractionSession:
        """Post feedback to entity extraction conversation."""
        pass

    def post_message_to_entity(
        self, session: AgniExtractionSession, entity_id: int, text: str
    ) -> AgniExtractionSession:
        """Post feedback to a specific entity's conversation."""
        pass

    def persist(
        self, session: AgniExtractionSession, description: str, author_id: str
    ) -> AgniExtractionSession:
        """Persist all resolved entities to the change queue.
        
        All entities must have status 'create_new' or 'matched'.
        """
        pass
```

### Protocol Implementations (Jawafdehi provides)

Jawafdehi must implement these protocols from `nes.services.agni.protocols`:

#### SearchService

```python
from nes.services.agni.protocols import SearchService
from nes.services.agni.models import ExtractedEntity, MatchEntityCandidate
from nes.core.models.entity import Entity, EntityType

class JawafSearchService(SearchService):
    """NES search operations for Jawafdehi."""

    def search(
        self, query: str, entity_type: Optional[EntityType] = None
    ) -> List[Entity]:
        """Search NES entities."""
        ...

    def find_candidates(self, entity: ExtractedEntity) -> List[MatchEntityCandidate]:
        """Find potential NES matches for an extracted entity."""
        ...

    def resolve(self, entity: ExtractedEntity) -> ExtractedEntity:
        """Resolve entity to NES match or mark for creation.
        
        Updates entity.candidates, entity.matched_id, or entity.needs_creation.
        """
        ...
```

#### GenAIService

```python
from nes.services.agni.protocols import GenAIService
from nes.services.agni.models import Conversation, DocumentMetadata, ExtractedEntity

class JawafGenAIService(GenAIService):
    """AI extraction operations for Jawafdehi."""

    def extract_metadata(
        self, document: Path, conversation: Conversation
    ) -> DocumentMetadata:
        """Extract document metadata using AI.
        
        Should consider conversation history for iterative refinement.
        """
        ...

    def extract_entities(
        self,
        document: Path,
        metadata: DocumentMetadata,
        conversation: Conversation,
    ) -> List[ExtractedEntity]:
        """Extract entities from document using AI.
        
        Should consider conversation history for iterative refinement.
        """
        ...
```

#### Persistence

```python
from nes.services.agni.protocols import Persistence
from nes.services.agni.models import EntityChange

class JawafPersistence(Persistence):
    """Persistence operations for Jawafdehi."""

    def queue_entity_change(
        self, change: EntityChange, description: str, author_id: str
    ) -> str:
        """Queue entity change to ApprovedEntityChange table.
        
        Returns change ID.
        """
        ...

    def get_pending_changes(self) -> List[EntityChange]:
        """Retrieve pending entity changes."""
        ...

    def apply_change(self, change_id: str) -> None:
        """Apply a pending change to NES."""
        ...
```

## Data Models

### NES Agni Models (imported)

These dataclasses are imported from `nes.services.agni.models`:

#### AgniExtractionSession

```python
@dataclass
class AgniExtractionSession:
    """Processing session container."""
    document: Optional[Path] = None
    metadata: Optional[DocumentMetadata] = None
    conversations: Dict[str, Conversation] = field(default_factory=dict)
    entities: List[ExtractedEntity] = field(default_factory=list)
    guidance: Optional[str] = None

    def get_conversation(self, key: str) -> Conversation:
        """Get or create a conversation for the given key."""
        pass
```

#### DocumentMetadata

```python
@dataclass
class DocumentMetadata:
    """Extracted document metadata."""
    title: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[date] = None
    document_type: Optional[str] = None
    source: Optional[str] = None
```

#### ExtractedEntity

```python
@dataclass
class ExtractedEntity:
    """Entity extracted from document by AI."""
    entity_type: EntityType
    entity_sub_type: Optional[EntitySubType] = None
    names: List[Dict[str, Any]] = field(default_factory=list)
    entity_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0

    # Matching state (populated during resolution)
    candidates: List[MatchEntityCandidate] = field(default_factory=list)
    matched_id: Optional[str] = None
    needs_creation: bool = False

    # Proposed changes for updates or new entity creation
    proposed_changes: Dict[str, Any] = field(default_factory=dict)

    @property
    def status(self) -> str:
        """Dynamically derived: 'create_new', 'matched', or 'needs_disambiguation'."""
        pass
```

#### MatchEntityCandidate

```python
@dataclass
class MatchEntityCandidate:
    """A potential NES match candidate."""
    nes_id: str
    confidence: float
    reason: str
```

#### EntityChange

```python
@dataclass
class EntityChange:
    """Entity change to be persisted."""
    entity_type: EntityType
    entity_sub_type: Optional[EntitySubType] = None
    entity_data: Dict[str, Any] = field(default_factory=dict)
    entity_id: Optional[str] = None  # For updates

    @property
    def change_type(self) -> str:
        """'update' if entity_id is set, otherwise 'create'."""
        pass
```

#### Conversation & Message

```python
@dataclass
class Message:
    """A message in a conversation thread."""
    author: Author  # USER or AI
    text: str
    timestamp: datetime

@dataclass
class Conversation:
    """Conversation thread for feedback."""
    thread: List[Message] = field(default_factory=list)

    def add(self, author: Author, text: str) -> None:
        """Add a message to the thread."""
        pass

class ConversationKey:
    """Conversation key constants."""
    METADATA_EXTRACTION = "metadata_extraction"
    ENTITY_EXTRACTION = "entity_extraction"

    @staticmethod
    def entity(entity_id: int) -> str:
        """Key for conversation about a specific extracted entity."""
        pass
```

### Django Models (Jawafdehi defines)

#### ApprovedEntityChange

```python
class ApprovedEntityChange(models.Model):
    """Queue of approved entity changes to be applied to NES."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    change_type = models.CharField(max_length=20)  # "create" or "update"
    
    # Entity identification
    entity_type = models.CharField(max_length=20)
    entity_sub_type = models.CharField(max_length=50, blank=True)
    nes_entity_id = models.CharField(max_length=300, blank=True)  # For updates
    
    # Full entity data
    entity_data = models.JSONField()
    
    # Audit
    description = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    approved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Approved Entity Change"
        verbose_name_plural = "Approved Entity Changes"
        ordering = ['-approved_at']
```

#### StoredExtractionSession (optional)

```python
class StoredExtractionSession(models.Model):
    """Persisted extraction session for resumable workflows."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    document = models.FileField(upload_to='agni/documents/')
    guidance = models.TextField(blank=True)
    session_data = models.JSONField()  # Serialized AgniExtractionSession
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Extraction Session"
        ordering = ['-updated_at']
```

## Admin Panel UI

The Jawafdehi admin panel provides the user interface for the extraction workflow.

### Admin Views

| View | Purpose |
|------|---------|
| Session List | List saved extraction sessions |
| New Session | Upload document, set guidance, begin extraction |
| Session Detail | View/edit metadata, entities, conversations |
| Entity Resolution | Disambiguate entity matches, mark for creation |
| Change Queue | View pending entity changes |

### Workflow in Admin

1. **Start**: User uploads document, optionally provides guidance
2. **Metadata**: Review extracted metadata, provide feedback via conversation
3. **Entities**: Review extracted entities, resolve matches or mark for creation
4. **Persist**: Approve and queue entity changes

## Correctness Properties

### Property 1: File Type Validation
*For any* file upload, the system SHALL accept only files with extensions in {.txt, .md, .doc, .docx, .pdf} and reject all others with an error message.

### Property 2: Confidence Score Range
*For any* extracted entity, the confidence score SHALL be within the range [0.0, 1.0].

### Property 3: Entity Status Derivation
*For any* ExtractedEntity:
- If `needs_creation=True` → status is `"create_new"`
- Else if `matched_id` is set → status is `"matched"`
- Else if `candidates` is non-empty → status is `"needs_disambiguation"`

### Property 4: Persist Requires Resolution
*For any* call to `AgniService.persist()`, all entities in the session SHALL have status `"create_new"` or `"matched"`.

### Property 5: Entity Change Queue Integrity
*For any* queued entity change, the entity_data SHALL contain all required fields for the specified entity_type.

## Error Handling

### Error Categories

| Category | Handling Strategy |
|----------|-------------------|
| Validation Errors | Show field-specific error messages in admin |
| AI Service Errors | Log error, show retry option |
| File Processing Errors | Show specific error about file issue |
| Resolution Errors | Prevent persist until all entities resolved |

## Testing Strategy

### Test Location
`services/jawafdehi-api/tests/agni/`

### Test Categories

| Category | Description |
|----------|-------------|
| Protocol Tests | Verify protocol implementations work with AgniService |
| Admin Tests | Test admin views and workflows |
| Integration Tests | End-to-end extraction flow |
| Model Tests | Django model validation |

### Test Data
- Use authentic Nepali names and entities
- Include bilingual (English/Nepali) test data
