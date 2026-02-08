# Entity Extraction & Resolution Design

**Author:** Agni Team  
**Date:** December 24, 2025  
**Status:** Draft

## Problem Statement

The current entity extraction pipeline in Agni has discrepancies between what the GenAI extracts and what gets successfully resolved/persisted. The goal is to use GenAI to:
1. Identify entities from documents
2. Build a diff (create new vs. update existing)
3. Take feedback from users
4. Submit to the NES database

This document focuses specifically on the entity extraction and resolution flow—not the broader Agni architecture.

---

## Out of Scope

The following are explicitly out of scope for this design:

- **Confidence scoring algorithms** - How match confidence is calculated
- **Search algorithm improvements** - NES search ranking, fuzzy matching, query optimization
- **Matching heuristics** - Name similarity scoring, transliteration matching

---

## Proposed Flow

```
Document → ai_background_research() → ResolvedEntity[] → ai_resolve_entity(entity_id) → EntityMatchState → User Review → Persist
```

### Two-Stage Extraction

**Stage 1: `ai_background_research`**
- Extracts document metadata (title, author, date, etc.)
- Returns a list of **resolved entities** - entity references identified in the document
- Fast, single LLM call for the entire document

**Stage 2: `ai_resolve_entity(entity_id)`**
- Resolves the entity with the given unique identifier to NES matches
- Searches for existing NES matches
- Can be called per-entity, enabling incremental processing and user feedback

---

## Contract Definitions

> **Note:** These definitions are authoritative. Any changes to entity schemas should be reflected here first.

### EntityName

A single name variant for an entity.

```python
@dataclass
class EntityName:
    """A single name variant for an entity."""
    
    name: str
    """The name text"""
    
    language: str
    """Language code: 'en' or 'ne'"""
    
    is_primary: bool = False
    """Whether this is the primary/preferred name"""
```

### ResolvedEntity

An entity reference extracted during metadata extraction. Contains the information needed to identify and match the entity.

```python
@dataclass
class ResolvedEntity:
    """
    Entity reference from initial document extraction.
    
    This is what ai_background_research() returns - information
    needed to identify an entity for later matching.
    """
    
    entity_type: str
    """Combined entity type. e.g., "person", "organization/political_party"""
    
    # Identity
    names: List[EntityName] = field(default_factory=list)
    """All name variants found in the document"""
    
    # Context from document
    attributes: Dict[str, Any] = field(default_factory=dict)
    """
    Contextual attributes extracted from document.
    Examples:
    - person: {"position": "Minister", "organization": "Ministry of Finance"}
    - organization: {"sector": "government", "level": "federal"}
    - location: {"district": "Kathmandu", "province": "Bagmati"}
    """

    # Extraction metadata
    mentions: List[str] = field(default_factory=list)
    """Text snippets where this entity was mentioned (for context)"""
```

**Entity Type Format:**

Entity types use a combined string format with optional subtype after a slash:
- `"person"` - Person without subtype
- `"organization"` - Default organization
- `"organization/political_party"` - Organization with political_party subtype
- `"organization/government_body"` - Organization with government_body subtype
- `"organization/ngo"` - Organization with ngo subtype

Helper functions `parse_entity_type()` and `format_entity_type()` are available for converting between combined strings and separate type/subtype values.

### EntityMatchCandidate

A potential NES match candidate for an extracted entity.

```python
@dataclass
class EntityMatchCandidate:
    """A potential NES match candidate."""
    
    nes_id: str
    """NES entity identifier"""
    
    nes_record: Optional[Entity] = None
    """The full NES Entity record if loaded"""
    
    confidence: float
    """Match confidence score"""
```

### ResolutionStatus

Resolution state enum for tracking entity matching progress:

```python
class ResolutionStatus(str, Enum):
    """Resolution state for an entity."""
    
    PENDING = "pending"
    """Not yet resolved"""
    
    MATCHED = "matched"
    """Matched to existing NES entity"""
    
    CREATE_NEW = "create_new"
    """Confirmed as new entity to create"""
    
    NEEDS_REVIEW = "needs_review"
    """Multiple candidates, needs human disambiguation"""
    
    SKIPPED = "skipped"
    """User chose to skip this entity"""
```

### EntityMatchState

Match state for a resolved entity. Contains match candidates, resolution status, and user decisions.

```python
@dataclass
class EntityMatchState:
    """Entity extracted from document by AI."""

    entity_id: str
    """Unique identifier for this entity match."""

    entity_type: EntityType
    """NES entity type enum"""
    
    entity_subtype: EntitySubType
    """NES entity subtype enum"""

    # Source reference
    resolved_entity: ResolvedEntity
    """The ResolvedEntity this match state is for"""

    # Resolution status
    resolution_status: ResolutionStatus = ResolutionStatus.PENDING
    """Current resolution state"""

    # Entity matching properties (populated during resolution)
    candidates: List[EntityMatchCandidate] = field(default_factory=list)
    """Potential NES matches found during resolution"""

    # User-made decisions
    matched_nes_id: Optional[str] = None
    """A particular candidate has been selected as the match."""

    needs_creation: bool = False
    """No candidate is satisfactory; we need to create one."""

    proposed_changes: Dict[str, Any] = field(default_factory=dict)
    """Proposed changes to apply (for updates or new entity creation)"""
```

### EntityChange

Represents an entity change to be persisted to NES.

```python
@dataclass
class EntityChange:
    """Entity change to be persisted."""

    entity_type: EntityType
    """NES entity type"""
    
    entity_subtype: Optional[EntitySubType] = None
    """NES entity subtype"""

    entity_data: Dict[str, Any] = field(default_factory=dict)
    """The changes to apply"""

    entity_id: Optional[str] = None
    """NES entity ID (None for new entities)"""

    change_type: str = Literal["create", "update"]
    """Whether this is a create or update operation"""
```

### AgniExtractionSession

Session container for the extraction process:

```python
@dataclass
class AgniExtractionSession:
    """Processing session container."""
    
    source_document: Optional[Path] = None
    """Path to the source document being processed"""
    
    guidance: Optional[str] = None
    """Optional guidance text to steer AI extraction behavior"""

    metadata: Optional[DocumentMetadata] = None
    """Extracted document metadata"""
    
    conversations: Dict[str, Conversation] = field(default_factory=dict)
    """Conversation threads for user feedback, keyed by ConversationKey"""

    entities: List[EntityMatchState] = field(default_factory=list)
    """
    Entities extracted from the document.
    Entity matching (matches, status, matched_entity) are properties on each.
    """

    def get_conversation(self, key: str) -> Conversation:
        """Get or create a conversation for the given key."""
        if key not in self.conversations:
            self.conversations[key] = Conversation()
        return self.conversations[key]
```

### ConversationKey

Constants for conversation thread keys:

```python
class ConversationKey:
    """Conversation key constants and templates."""

    METADATA_EXTRACTION = "metadata_extraction"
    ENTITY_EXTRACTION = "entity_extraction"

    @staticmethod
    def entity(entity_id: int) -> str:
        """Key for conversation about a specific extracted entity."""
        return f"entity:{entity_id}"
```

---

## Current Approach (for reference)

The current implementation extracts entities in a single pass:

```python
# Current: Single-stage extraction
async def ai_background_research(self, session):
    raw = await self.genai.extract_metadata(document, session)
    session.metadata = self._parse_metadata(raw["metadata"])
    session.entities = self._parse_entities(raw["entities"])  # Full entities
    return session
```

### Issues with Current Approach

1. **All-or-nothing extraction** - Can't get partial results or resolve incrementally
2. **No separation of concerns** - Extraction and resolution are conflated
3. **Schema mismatch** - Extracted entities don't match NES schema
4. **No deduplication** - Same entity mentioned multiple times creates duplicates

---

## Migration Path

### Phase 1: Introduce ResolvedEntity

1. Update `ai_background_research` to return `ResolvedEntity[]` instead of full entities
2. Add `resolved_entities` field to session
3. Keep existing `entities` field for backward compatibility

### Phase 2: Implement ai_resolve_entity

1. Add `ai_resolve_entity(entity_id)` method to AgniService
2. Implement NES search and candidate matching
3. Populate `entity_match_states[entity_id]` with match data

### Phase 3: Update UI/API

1. Update API endpoints to expose two-stage flow
2. Allow UI to trigger resolution per-entity
3. Enable user feedback between resolution steps

### Phase 4: Deprecate Old Flow

1. Remove single-stage entity extraction
2. Clean up backward compatibility code

---

## Open Questions

1. **Deduplication timing** - Should we deduplicate resolved entities before matching, or during?
2. **Batch resolution** - Should `ai_resolve_entity` support batch mode for efficiency?
3. **Caching** - Should entity match states be cached to avoid re-resolution?
4. **Partial persistence** - Can we persist some entities while others are still being resolved?

---

## Next Steps

1. [x] Define ResolvedEntity and EntityMatchState in `agni_models.py`
2. [ ] Update GenAI prompts to return resolved entity format
3. [ ] Implement `ai_resolve_entity()` in AgniService
4. [ ] Add integration tests for two-stage flow
5. [ ] Update API endpoints
