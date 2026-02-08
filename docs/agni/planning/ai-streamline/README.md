# AI Integration Approaches for Agni AI

## Overview

This document explores different architectural approaches for integrating AI capabilities into the Agni AI service, specifically focusing on context management strategies for document processing and entity extraction workflows.

## Context Management Strategies

### 1. Single-Session Context Approach

**Description**: All AI interactions for a given document or case occur within a single, long-lived conversation context.

**Architecture**:
```
Document Upload → Initialize Session → Sequential Processing → Session Close
                        ↓
                  [Persistent Context]
                        ↓
        Entity Extraction → Relationship Mapping → Validation
```

**Advantages**:
- **Contextual Continuity**: AI maintains full awareness of previous extractions and decisions
- **Cross-Reference Resolution**: Can reference earlier entities when processing later sections
- **Iterative Refinement**: Easy to ask follow-up questions or request clarifications
- **Reduced Redundancy**: No need to re-explain document structure or domain context

**Disadvantages**:
- **Token Accumulation**: Context grows with each interaction, increasing costs
- **Session Management Complexity**: Need to handle session persistence, timeouts, and recovery
- **Scalability Concerns**: Long-running sessions may block resources
- **Error Propagation**: Early mistakes can influence later extractions

**Best For**:
- Complex documents requiring deep analysis
- Cases with intricate entity relationships
- Interactive workflows with human-in-the-loop validation
- Documents in Nepali requiring consistent translation context

**Implementation Considerations**:
```python
class SingleSessionProcessor:
    def __init__(self, document_id: str):
        self.session = AISession(document_id)
        self.context_history = []
    
    async def process_document(self, document: Document):
        # Initialize with document context
        await self.session.add_context(document.content)
        
        # Sequential processing with accumulated context
        entities = await self.extract_entities()
        relationships = await self.map_relationships(entities)
        validated = await self.validate_with_context(relationships)
        
        return validated
```

---

### 2. Multi-Session Context Approach

**Description**: Each processing stage or document section gets its own independent AI session with targeted context.

**Architecture**:
```
Document Upload → Chunk/Stage Identification
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   Session A       Session B       Session C
   (Entities)    (Relationships)  (Validation)
        ↓               ↓               ↓
        └───────────────┼───────────────┘
                        ↓
                  Merge Results
```

**Advantages**:
- **Parallel Processing**: Multiple stages can run concurrently
- **Cost Efficiency**: Each session has minimal, focused context
- **Fault Isolation**: Errors in one session don't affect others
- **Scalability**: Easy to distribute across multiple AI instances
- **Clear Boundaries**: Each session has a specific, well-defined task

**Disadvantages**:
- **Context Loss**: No awareness of decisions made in other sessions
- **Duplicate Context**: May need to repeat document/domain context
- **Integration Complexity**: Need robust result merging logic
- **Inconsistency Risk**: Different sessions may make conflicting interpretations

**Best For**:
- Large documents that can be meaningfully chunked
- Independent processing tasks (e.g., entity extraction vs. sentiment analysis)
- High-throughput batch processing
- Cost-sensitive deployments

**Implementation Considerations**:
```python
class MultiSessionProcessor:
    async def process_document(self, document: Document):
        # Create independent sessions for each stage
        tasks = [
            self.extract_entities_session(document),
            self.extract_dates_session(document),
            self.extract_amounts_session(document),
        ]
        
        # Process in parallel
        results = await asyncio.gather(*tasks)
        
        # Merge with conflict resolution
        return self.merge_results(results)
    
    async def extract_entities_session(self, document: Document):
        session = AISession(task="entity_extraction")
        return await session.process(document.content)
```

---

### 3. Hybrid Approach: Staged Sessions with Handoff

**Description**: Combines benefits of both approaches - multiple sessions with explicit context handoff between stages.

**Architecture**:
```
Document Upload → Session 1: Initial Extraction
                        ↓
                  [Context Summary]
                        ↓
                  Session 2: Relationship Mapping
                        ↓
                  [Context Summary]
                        ↓
                  Session 3: Validation & Enrichment
```

**Advantages**:
- **Balanced Context**: Each session gets relevant prior context without full history
- **Stage Optimization**: Can tune context size per stage
- **Checkpoint Recovery**: Easy to resume from any stage
- **Cost Control**: Context summaries prevent unbounded growth

**Disadvantages**:
- **Summary Quality**: Depends on effective context compression
- **Implementation Complexity**: Need robust handoff mechanisms
- **Potential Information Loss**: Summaries may omit important details

**Best For**:
- Multi-stage workflows with clear dependencies
- Medium to large documents
- Production systems requiring reliability and cost control

**Implementation Considerations**:
```python
class HybridProcessor:
    async def process_document(self, document: Document):
        # Stage 1: Initial extraction
        session1 = AISession(stage="extraction")
        entities = await session1.extract_entities(document)
        context1 = await session1.summarize_context()
        
        # Stage 2: Relationship mapping with handoff
        session2 = AISession(stage="relationships")
        session2.load_context(context1)
        relationships = await session2.map_relationships(entities)
        context2 = await session2.summarize_context()
        
        # Stage 3: Validation with accumulated context
        session3 = AISession(stage="validation")
        session3.load_context(context2)
        validated = await session3.validate(relationships)
        
        return validated
```

---

## Recommendation for Agni AI

### Proposed Approach: **Hybrid with Nepali Context Optimization**

For the Jawafdehi use case, we recommend a hybrid approach with special considerations for Nepali language processing:

**Stage 1: Document Understanding (Single Session)**
- Parse document structure
- Identify language (Nepali/English/Mixed)
- Extract key sections and metadata
- Build glossary of Nepali terms and entities

**Stage 2: Entity Extraction (Multi-Session per Section)**
- Process document sections in parallel
- Each session receives: document glossary + section content
- Extract: organizations, people, amounts, dates, locations

**Stage 3: Relationship & Validation (Single Session)**
- Consolidate all extracted entities
- Map relationships and cross-references
- Validate against Nepal Entity Service
- Resolve conflicts and ambiguities

**Benefits for Jawafdehi**:
- Handles bilingual content effectively
- Optimizes for Nepali entity recognition
- Balances cost and accuracy
- Supports human review at stage boundaries
- Integrates with existing Nepal Entity Service

**Implementation Priority**:
1. Start with single-session POC for validation
2. Migrate to hybrid once patterns are established
3. Optimize context handoff based on real document characteristics

---

## Technical Considerations

### Context Size Management
- **Token Limits**: GPT-4: 128K tokens, Claude: 200K tokens
- **Cost per 1M tokens**: GPT-4: $10-30, Claude: $8-24
- **Nepali Text**: ~1.5x token overhead vs English

### Session Persistence
- Store session state in PostgreSQL
- Cache active sessions in Redis
- Implement session timeout (30 min default)
- Support session resume for long documents

### Error Handling
- Retry logic for transient failures
- Fallback to simpler extraction on complex failures
- Human escalation for low-confidence results
- Audit trail for all AI decisions

### Monitoring & Observability
- Track token usage per document/session
- Measure extraction accuracy by entity type
- Monitor session duration and failure rates
- A/B test different context strategies

---

## Next Steps

1. **POC Implementation**: Build single-session prototype with sample Nepali documents
2. **Benchmark Testing**: Compare approaches on real Jawafdehi cases
3. **Cost Analysis**: Model token usage and API costs for each approach
4. **Integration Design**: Define interfaces with JawafdehiAPI and Nepal Entity Service
5. **Evaluation Framework**: Establish metrics for extraction quality and consistency
