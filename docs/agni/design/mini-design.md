# Mini Design: AgniService Architecture

## Overview

A simplified architecture with five core components: `AgniService`, `SearchService`, `GenAIService`, `State`, and `Persistence`. All components live in NepalEntityService.

```
┌─────────────────────────────────────────────────────────────────┐
│                      NepalEntityService                          │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                       AgniService                          │  │
│  │   - Orchestrates extraction and resolution pipeline       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                │               │               │                 │
│                ▼               ▼               ▼                 │
│  ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │  SearchService   │ │ GenAIService │ │ Persistence  │         │
│  │  - Entity search │ │ - Extraction │ │ - Queue ops  │         │
│  │  - Matching      │ │ - AI calls   │ │ - NES writes │         │
│  └──────────────────┘ └──────────────┘ └──────────────┘         │
│                                                │                 │
│         ┌──────────┐                           ▼                 │
│         │  State   │                    ┌────────────┐          │
│         └──────────┘                    │ NES Models │          │
│                                         └────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. State

Holds the current processing context. Passed into AgniService methods.

```python
@dataclass
class State:
    """Processing state container."""
    document: Optional[Path] = None
    metadata: Optional[DocumentMetadata] = None
    extracted_entities: List[ExtractedEntity] = field(default_factory=list)
    resolved_entities: List[ResolvedEntity] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
```

### 2. Persistence

Handles all NES database operations.

```python
class Persistence(Protocol):
    """NES database operations interface."""
    
    def queue_entity_change(self, change: EntityChange) -> str:
        """Queue entity change. Returns change ID."""
        ...
    
    def get_pending_changes(self) -> List[EntityChange]:
        """Retrieve pending entity changes."""
        ...
    
    def apply_change(self, change_id: str) -> None:
        """Apply a pending change to NES."""
        ...
```

### 3. SearchService

Handles entity search and matching against NES.

```python
class SearchService(Protocol):
    """Entity search and matching operations."""
    
    def search(self, query: str, entity_type: Optional[str] = None) -> List[NESEntity]:
        """Search NES entities."""
        ...
    
    def find_matches(self, entity: ExtractedEntity) -> List[EntityMatch]:
        """Find potential NES matches for an extracted entity."""
        ...
    
    def resolve(self, entity: ExtractedEntity, matches: List[EntityMatch]) -> ResolvedEntity:
        """Resolve entity to NES match or mark for creation."""
        ...
```

### 4. GenAIService

Handles AI-powered extraction.

```python
class GenAIService(Protocol):
    """AI extraction operations."""
    
    def extract_metadata(self, document: str) -> DocumentMetadata:
        """Extract document metadata using AI."""
        ...
    
    def extract_entities(self, document: str, metadata: DocumentMetadata) -> List[ExtractedEntity]:
        """Extract entities from document using AI."""
        ...
```

### 5. AgniService

Orchestrates the pipeline using injected services.

```python
# services/nes/nes/services/agni_service.py

class AgniService:
    """Orchestrates entity extraction and resolution pipeline."""
    
    def __init__(
        self, 
        search: SearchService, 
        genai: GenAIService, 
        persistence: Persistence
    ):
        self.search = search
        self.genai = genai
        self.persistence = persistence
    
    # --- Extraction Methods ---
    
    def extract_metadata(self, state: State) -> State:
        """Extract document metadata."""
        state.metadata = self.genai.extract_metadata(state.document)
        return state
    
    def extract_entities(self, state: State) -> State:
        """Extract entities from document."""
        state.extracted_entities = self.genai.extract_entities(
            state.document, 
            state.metadata
        )
        return state
    
    # --- Resolution Methods ---
    
    def resolve_entities(self, state: State) -> State:
        """Match extracted entities against NES."""
        for entity in state.extracted_entities:
            matches = self.search.find_matches(entity)
            resolved = self.search.resolve(entity, matches)
            state.resolved_entities.append(resolved)
        return state
    
    # --- Persistence Methods ---
    
    def commit(self, state: State) -> State:
        """Persist approved entity changes."""
        for entity in state.resolved_entities:
            if entity.needs_creation:
                self.persistence.queue_entity_change(entity.to_change())
        return state
```

---

## Usage

```python
# Initialize services
search = NESSearchService()
genai = OpenAIGenAIService()
persistence = NESPersistence()

agni = AgniService(search, genai, persistence)

# Process document
state = State(document=Path("/docs/report.pdf"))

state = agni.extract_metadata(state)
state = agni.extract_entities(state)
state = agni.resolve_entities(state)

# After user review/approval
state = agni.commit(state)
```

---

## Data Classes

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import date

@dataclass
class DocumentMetadata:
    """Extracted document metadata."""
    title: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[date] = None
    document_type: Optional[str] = None
    source: Optional[str] = None

@dataclass
class ExtractedEntity:
    """Entity extracted from document by AI."""
    entity_type: str  # "person" | "organization"
    names: List[Dict[str, Any]]  # [{lang: "en", name: "..."}, {lang: "ne", name: "..."}]
    entity_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0

@dataclass
class EntityMatch:
    """Potential NES match for an extracted entity."""
    nes_id: str
    name_en: Optional[str] = None
    name_ne: Optional[str] = None
    score: float = 0.0

@dataclass
class ResolvedEntity:
    """Extracted entity with resolution status."""
    entity: ExtractedEntity
    matches: List[EntityMatch] = field(default_factory=list)
    status: str = "pending"  # "matched" | "create_new" | "pending"
    matched_nes_id: Optional[str] = None
    
    @property
    def needs_creation(self) -> bool:
        return self.status == "create_new"
    
    def to_change(self) -> "EntityChange":
        return EntityChange(
            change_type="create",
            entity_type=self.entity.entity_type,
            entity_data=self.entity.entity_data
        )

@dataclass
class EntityChange:
    """Entity change to be persisted."""
    change_type: str  # "create" | "update"
    entity_type: str
    entity_data: Dict[str, Any]
    nes_id: Optional[str] = None  # For updates

@dataclass
class NESEntity:
    """NES entity reference."""
    nes_id: str
    entity_type: str
    name_en: Optional[str] = None
    name_ne: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| All in NepalEntityService | Single service, no separate AgniAI package |
| State as input/output | Enables pipeline composition, easy testing, clear data flow |
| SearchService injected | Decouples search/matching logic, allows different strategies |
| GenAIService injected | Decouples AI provider, allows swapping (OpenAI, Claude, etc.) |
| Persistence as protocol | Allows swapping implementations (Django ORM, mock, etc.) |
| AgniService orchestrates | Single entry point, delegates to specialized services |
