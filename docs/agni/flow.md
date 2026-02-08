# Agni Document Processing Flow

## Overview

This document defines the contracts between UI, API, and Worker layers for asynchronous document processing with AI-powered entity extraction.

## Architecture

```
┌──────────────┐
│  UI Layer    │  Django Admin + JavaScript (XHR)
└──────┬───────┘
       │ HTTP/XHR
┌──────▼───────┐
│  API Layer   │  Django Views + REST Endpoints
└──────┬───────┘
       │ Django Q
┌──────▼───────┐
│ Worker Layer │  Async Tasks
└──────┬───────┘
       │
┌──────▼───────┐
│ AgniService  │  Core Processing Logic
└──────────────┘
```

## Contract 1: UI ↔ API Layer

### API Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/agni/sessions/` | Upload document and create session | is_admin |
| GET | `/api/agni/sessions/{id}/` | Get session status and details | is_admin |
| POST | `/api/agni/sessions/{id}/entities/{index}/` | Resolve entity (match or create) | is_admin |
| POST | `/api/agni/sessions/{id}/conversations/{key}/` | Post message to conversation | is_admin |
| POST | `/api/agni/sessions/{id}/persist/` | Persist approved changes | is_admin |

### Document Upload
```
POST /api/agni/sessions/
Content-Type: multipart/form-data
Authorization: Required (is_admin)

Request:
- document: File (.txt, .md, .doc, .docx, .pdf)
- guidance: Optional[str]

Response: 201 Created
{
  "id": "uuid",
  "status": "pending",
  "document_url": "/media/agni/documents/file.pdf",
  "created_at": "2024-12-18T10:00:00Z"
}
```

### Get Session Status
```
GET /api/agni/sessions/{session_id}/
Authorization: Required (is_admin)

Response: {
  "id": "uuid",
  "status": "processing_entities",
  "task_status": "running",
  "progress": {"current": 3, "total": 10, "stage": "extracting_entities"},
  "error_message": null,
  "metadata": {
    "title": "...",
    "summary": "...",
    "publication_date": "2024-01-15"
  },
  "entities": [
    {
      "entity_type": "PERSON",
      "names": [{"text": "राम बहादुर", "language": "ne"}],
      "confidence": 0.85,
      "status": "needs_disambiguation",
      "candidates": [
        {"nes_id": "person_123", "confidence": 0.92, "reason": "Name match"}
      ]
    }
  ],
  "updated_at": "2024-12-18T10:30:00Z"
}
```

### Resolve Entity (Match, Create, or Skip)
```
POST /api/agni/sessions/{session_id}/entities/{entity_index}/
Authorization: Required (is_admin)

Request (Match to existing):
{
  "action": "match",
  "nes_id": "person_123"
}

Request (Create new):
{
  "action": "create",
  "confirmed": true
}

Request (Skip entity):
{
  "action": "skip",
  "reason": "Not relevant to case"
}

Response: {
  "success": true,
  "entity_status": "matched" | "create_new" | "skipped"
}

Validation:
- NES ID format: person_\d+, org_\d+, location_\d+
- Entity index must be valid
- Action must be "match", "create", or "skip"
- Skip reason is optional but recommended
```

### Post Conversation Message
```
POST /api/agni/sessions/{session_id}/conversations/{conversation_key}/
Authorization: Required (is_admin)

Request: {
  "message": "Please extract more person names"
}

Response: {
  "success": true,
  "message_id": "msg_123"
}

Conversation Keys:
- "metadata_extraction"
- "entity_extraction"
- "entity:0", "entity:1", ... (per-entity conversations)
```



### Persist Changes
```
POST /api/agni/sessions/{session_id}/persist/
Authorization: Required (is_admin)

Request: {
  "description": "Extracted from corruption case document",
  "confirm": true
}

Response: {
  "success": true,
  "change_ids": ["change_abc", "change_def"],
  "message": "2 changes queued for persistence"
}

Validation:
- All entities must have status "matched", "create_new", or "skipped"
```



### NES Entity Search (Client-Side)
```
# UI calls NES API directly (no server proxy)
GET https://nes-api.jawafdehi.org/entities/search/?q=राम बहादुर&type=PERSON

# Server only validates NES ID format when user selects match
```

## API Implementation

### States

Session states define the current processing stage and determine which actions are allowed. All actions require `is_admin` permission from `cases.rules.predicates.is_admin`.

| State | Description | Allowed Actions | Auto-Transitions |
|-------|-------------|-----------------|------------------|
| `pending` | Session created, waiting for metadata extraction | `GET session` | → `processing_metadata` (auto) |
| `processing_metadata` | AI extracting document metadata | `GET session` | → `metadata_extracted` (auto) |
| `metadata_extracted` | Metadata complete, waiting for entity extraction | `GET session` | → `processing_entities` (auto) |
| `processing_entities` | AI extracting and resolving entities | `GET session` | → `awaiting_review` (auto) |
| `awaiting_review` | Entities ready for human review | `GET session`<br>`POST entities/{index}/`<br>`POST conversations/{key}/`<br>`POST persist/` | → `processing_persistence` (user) |
| `processing_persistence` | Persisting approved changes to NES | `GET session` | → `completed` (auto) |
| `completed` | All processing finished successfully | `GET session` | None |
| `failed` | Processing failed at any stage | `GET session` | None |

#### State Transition Rules

**Automatic Transitions:**
- `pending` → `processing_metadata` (when metadata task starts)
- `processing_metadata` → `metadata_extracted` (when metadata task completes)
- `metadata_extracted` → `processing_entities` (when entity task starts)
- `processing_entities` → `awaiting_review` (when entity task completes)
- `processing_persistence` → `completed` (when persistence task completes)
- Any state → `failed` (on task failure)

**User-Triggered Transitions:**
- `awaiting_review` → `processing_persistence` (when user calls `POST persist/`)

#### Permission Requirements

All API endpoints require `is_admin` permission:

```python
from cases.rules.predicates import is_admin

@api_view(['POST'])
@permission_classes([IsAdminUser])  # Django's IsAdminUser maps to is_admin predicate
def create_session(request):
    # Only users with is_admin=True can access
    pass
```

The `is_admin` predicate returns `True` if:
- User is a superuser (`user.is_superuser`), OR
- User belongs to the 'Admin' group (`user.groups.filter(name='Admin').exists()`)

#### State Validation

Each endpoint validates the session state before allowing operations:

```python
# Entity resolution only allowed in awaiting_review state
if session.status != 'awaiting_review':
    return Response({
        "success": False, 
        "error": "invalid_state", 
        "message": "Session must be in awaiting_review status"
    }, status=400)
```

#### Error Handling

Failed states preserve error information:
- `error_message`: Human-readable error description
- `current_task_id`: ID of the failed task
- `task_status`: Set to 'failed'

Users can view failed sessions but cannot perform actions on them. Recovery requires creating a new session.

### Django REST Framework Views

```python
# agni/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django_q.tasks import async_task
from django.shortcuts import get_object_or_404
from django.db import transaction
import re
from .models import StoredExtractionSession
from .serializers import SessionSerializer, EntityActionSerializer
from .utils import serialize_session, deserialize_session

@api_view(['POST'])
@permission_classes([IsAdminUser])
@transaction.atomic
def create_session(request):
    """Upload document and create extraction session."""
    if 'document' not in request.FILES:
        return Response(
            {"success": False, "error": "validation_error", "message": "Document file required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    document = request.FILES['document']
    guidance = request.data.get('guidance', '')
    
    # Validate file type
    allowed_extensions = ['.txt', '.md', '.doc', '.docx', '.pdf']
    if not any(document.name.lower().endswith(ext) for ext in allowed_extensions):
        return Response(
            {"success": False, "error": "validation_error", 
             "message": f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create session
    session = StoredExtractionSession.objects.create(
        document=document,
        session_data={'guidance': guidance},
        created_by=request.user,
        status='pending'
    )
    
    # Auto-trigger metadata extraction
    task_id = async_task('agni.tasks.extract_metadata_task', session_id=str(session.id))
    session.current_task_id = task_id
    session.task_status = 'queued'
    session.save()
    
    return Response({
        "id": str(session.id),
        "status": session.status,
        "document_url": session.document.url,
        "created_at": session.created_at.isoformat()
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_session(request, session_id):
    """Get session status and details."""
    session = get_object_or_404(StoredExtractionSession, id=session_id)
    
    # Deserialize session data
    agni_session = deserialize_session(session.session_data)
    
    # Build response
    response_data = {
        "id": str(session.id),
        "status": session.status,
        "task_status": session.task_status,
        "error_message": session.error_message,
        "progress": session.progress_info,
        "metadata": None,
        "entities": [],
        "updated_at": session.updated_at.isoformat()
    }
    
    # Add metadata if available
    if agni_session.metadata:
        response_data["metadata"] = {
            "title": agni_session.metadata.title,
            "summary": agni_session.metadata.summary,
            "author": agni_session.metadata.author,
            "publication_date": agni_session.metadata.publication_date.isoformat() if agni_session.metadata.publication_date else None,
            "document_type": agni_session.metadata.document_type,
            "source": agni_session.metadata.source
        }
    
    # Add entities if available
    if agni_session.entities:
        response_data["entities"] = [
            {
                "entity_type": entity.entity_type.value,
                "entity_sub_type": entity.entity_sub_type.value if entity.entity_sub_type else None,
                "names": entity.names,
                "entity_data": entity.entity_data,
                "confidence": entity.confidence,
                "status": entity.status,
                "candidates": [
                    {
                        "nes_id": candidate.nes_id,
                        "confidence": candidate.confidence,
                        "reason": candidate.reason
                    }
                    for candidate in entity.candidates
                ],
                "matched_id": entity.matched_id,
                "needs_creation": entity.needs_creation
            }
            for entity in agni_session.entities
        ]
    
    return Response(response_data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
@transaction.atomic
def resolve_entity(request, session_id, entity_index):
    """Resolve entity (match, create, or skip)."""
    session = get_object_or_404(StoredExtractionSession, id=session_id)
    
    # Validate session status
    if session.status != 'awaiting_review':
        return Response(
            {"success": False, "error": "invalid_state", 
             "message": "Session must be in awaiting_review status"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Deserialize session data
    agni_session = deserialize_session(session.session_data)
    
    # Validate entity index
    if entity_index < 0 or entity_index >= len(agni_session.entities):
        return Response(
            {"success": False, "error": "validation_error", "message": "Invalid entity index"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    entity = agni_session.entities[entity_index]
    action = request.data.get('action')
    
    if action == 'match':
        nes_id = request.data.get('nes_id')
        if not nes_id:
            return Response(
                {"success": False, "error": "validation_error", "message": "nes_id required for match action"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate NES ID format
        if not validate_nes_id(nes_id, entity.entity_type):
            return Response(
                {"success": False, "error": "validation_error", "message": "Invalid NES ID format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        entity.matched_id = nes_id
        entity.needs_creation = False
        entity_status = "matched"
        
    elif action == 'create':
        confirmed = request.data.get('confirmed', False)
        if not confirmed:
            return Response(
                {"success": False, "error": "validation_error", "message": "confirmed=true required for create action"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        entity.needs_creation = True
        entity.matched_id = None
        entity_status = "create_new"
        
    elif action == 'skip':
        reason = request.data.get('reason', '')
        entity.is_skipped = True
        entity.skip_reason = reason
        entity.matched_id = None
        entity.needs_creation = False
        entity_status = "skipped"
        
    else:
        return Response(
            {"success": False, "error": "validation_error", 
             "message": "action must be 'match', 'create', or 'skip'"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Save updated session atomically
    session.session_data = serialize_session(agni_session)
    session.save()
    
    return Response({
        "success": True,
        "entity_status": entity_status
    })

@api_view(['POST'])
@permission_classes([IsAdminUser])
@transaction.atomic
def post_conversation_message(request, session_id, conversation_key):
    """Post message to conversation thread."""
    session = get_object_or_404(StoredExtractionSession, id=session_id)
    
    message = request.data.get('message')
    if not message:
        return Response(
            {"success": False, "error": "validation_error", "message": "message required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate conversation key
    valid_keys = ['metadata_extraction', 'entity_extraction']
    if conversation_key.startswith('entity:'):
        try:
            entity_index = int(conversation_key.split(':')[1])
            agni_session = deserialize_session(session.session_data)
            if entity_index < 0 or entity_index >= len(agni_session.entities):
                raise ValueError("Invalid entity index")
        except (ValueError, IndexError):
            return Response(
                {"success": False, "error": "validation_error", "message": "Invalid conversation key"},
                status=status.HTTP_400_BAD_REQUEST
            )
    elif conversation_key not in valid_keys:
        return Response(
            {"success": False, "error": "validation_error", "message": "Invalid conversation key"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Add message to conversation (implementation depends on AgniService integration)
    # For now, just acknowledge the message
    message_id = f"msg_{session_id}_{conversation_key}_{len(session.session_data.get('conversations', {}).get(conversation_key, []))}"
    
    return Response({
        "success": True,
        "message_id": message_id
    })

@api_view(['POST'])
@permission_classes([IsAdminUser])
@transaction.atomic
def persist_changes(request, session_id):
    """Persist approved entity changes."""
    session = get_object_or_404(StoredExtractionSession, id=session_id)
    
    # Validate session status
    if session.status != 'awaiting_review':
        return Response(
            {"success": False, "error": "invalid_state", 
             "message": "Session must be in awaiting_review status"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    description = request.data.get('description', '')
    confirm = request.data.get('confirm', False)
    
    if not confirm:
        return Response(
            {"success": False, "error": "validation_error", "message": "confirm=true required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Deserialize session data
    agni_session = deserialize_session(session.session_data)
    
    # Validate all entities are resolved
    for i, entity in enumerate(agni_session.entities):
        if entity.status not in ('matched', 'create_new', 'skipped'):
            return Response(
                {"success": False, "error": "validation_error", 
                 "message": f"Entity {i} not resolved: {entity.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Queue persistence task
    task_id = async_task(
        'agni.tasks.persist_changes_task',
        session_id=str(session.id),
        description=description,
        author_id=str(request.user.id)
    )
    
    # Update session status atomically
    session.status = 'processing_persistence'
    session.current_task_id = task_id
    session.task_status = 'queued'
    session.save()
    
    # Count changes (skip skipped entities)
    change_count = sum(1 for entity in agni_session.entities if entity.status in ('matched', 'create_new'))
    
    return Response({
        "success": True,
        "change_ids": [f"pending_{task_id}"],  # Actual IDs will be generated by persistence task
        "message": f"{change_count} changes queued for persistence"
    })

def validate_nes_id(nes_id: str, entity_type) -> bool:
    """Validate NES entity ID format."""
    patterns = {
        'PERSON': r'^person_\d+$',
        'ORGANIZATION': r'^org_\d+$',
        'LOCATION': r'^location_\d+$',
    }
    pattern = patterns.get(entity_type.value if hasattr(entity_type, 'value') else str(entity_type))
    return bool(re.match(pattern, nes_id)) if pattern else False
```

### URL Configuration

```python
# agni/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('sessions/', views.create_session, name='create_session'),
    path('sessions/<uuid:session_id>/', views.get_session, name='get_session'),
    path('sessions/<uuid:session_id>/entities/<int:entity_index>/', views.resolve_entity, name='resolve_entity'),
    path('sessions/<uuid:session_id>/conversations/<str:conversation_key>/', views.post_conversation_message, name='post_conversation_message'),
    path('sessions/<uuid:session_id>/persist/', views.persist_changes, name='persist_changes'),
]
```

### Main URLs Integration

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/agni/', include('agni.urls')),
    # ... other URL patterns
]
```

### Utility Functions

```python
# agni/utils.py
import json
from pathlib import Path
from datetime import datetime, date
from nes.services.agni.models import AgniExtractionSession, DocumentMetadata, ExtractedEntity
from nes.core.models.entity import EntityType, EntitySubType

def serialize_session(agni_session: AgniExtractionSession) -> dict:
    """Serialize AgniExtractionSession to JSON-compatible dict."""
    data = {
        'document': str(agni_session.document) if agni_session.document else None,
        'guidance': agni_session.guidance,
        'metadata': None,
        'conversations': {},
        'entities': []
    }
    
    # Serialize metadata
    if agni_session.metadata:
        data['metadata'] = {
            'title': agni_session.metadata.title,
            'summary': agni_session.metadata.summary,
            'author': agni_session.metadata.author,
            'publication_date': agni_session.metadata.publication_date.isoformat() if agni_session.metadata.publication_date else None,
            'document_type': agni_session.metadata.document_type,
            'source': agni_session.metadata.source
        }
    
    # Serialize conversations
    for key, conversation in agni_session.conversations.items():
        data['conversations'][key] = [
            {
                'author': message.author.value,
                'text': message.text,
                'timestamp': message.timestamp.isoformat()
            }
            for message in conversation.thread
        ]
    
    # Serialize entities
    for entity in agni_session.entities:
        entity_data = {
            'entity_type': entity.entity_type.value,
            'entity_sub_type': entity.entity_sub_type.value if entity.entity_sub_type else None,
            'names': entity.names,
            'entity_data': entity.entity_data,
            'confidence': entity.confidence,
            'candidates': [
                {
                    'nes_id': candidate.nes_id,
                    'confidence': candidate.confidence,
                    'reason': candidate.reason
                }
                for candidate in entity.candidates
            ],
            'matched_id': entity.matched_id,
            'needs_creation': entity.needs_creation,
            'proposed_changes': entity.proposed_changes
        }
        
        # Add skip fields if present
        if hasattr(entity, 'is_skipped'):
            entity_data['is_skipped'] = entity.is_skipped
        if hasattr(entity, 'skip_reason'):
            entity_data['skip_reason'] = entity.skip_reason
            
        data['entities'].append(entity_data)
    
    return data

def deserialize_session(data: dict) -> AgniExtractionSession:
    """Deserialize dict to AgniExtractionSession."""
    from nes.services.agni.models import (
        AgniExtractionSession, DocumentMetadata, ExtractedEntity, 
        Conversation, Message, Author, MatchEntityCandidate
    )
    
    session = AgniExtractionSession(
        document=Path(data['document']) if data.get('document') else None,
        guidance=data.get('guidance')
    )
    
    # Deserialize metadata
    if data.get('metadata'):
        metadata_data = data['metadata']
        session.metadata = DocumentMetadata(
            title=metadata_data.get('title'),
            summary=metadata_data.get('summary'),
            author=metadata_data.get('author'),
            publication_date=datetime.fromisoformat(metadata_data['publication_date']).date() if metadata_data.get('publication_date') else None,
            document_type=metadata_data.get('document_type'),
            source=metadata_data.get('source')
        )
    
    # Deserialize conversations
    for key, messages in data.get('conversations', {}).items():
        conversation = Conversation()
        for msg_data in messages:
            message = Message(
                author=Author(msg_data['author']),
                text=msg_data['text'],
                timestamp=datetime.fromisoformat(msg_data['timestamp'])
            )
            conversation.thread.append(message)
        session.conversations[key] = conversation
    
    # Deserialize entities
    for entity_data in data.get('entities', []):
        entity = ExtractedEntity(
            entity_type=EntityType(entity_data['entity_type']),
            entity_sub_type=EntitySubType(entity_data['entity_sub_type']) if entity_data.get('entity_sub_type') else None,
            names=entity_data.get('names', []),
            entity_data=entity_data.get('entity_data', {}),
            confidence=entity_data.get('confidence', 0.0),
            matched_id=entity_data.get('matched_id'),
            needs_creation=entity_data.get('needs_creation', False),
            proposed_changes=entity_data.get('proposed_changes', {})
        )
        
        # Deserialize candidates
        for candidate_data in entity_data.get('candidates', []):
            candidate = MatchEntityCandidate(
                nes_id=candidate_data['nes_id'],
                confidence=candidate_data['confidence'],
                reason=candidate_data['reason']
            )
            entity.candidates.append(candidate)
        
        # Add skip fields if present
        if 'is_skipped' in entity_data:
            entity.is_skipped = entity_data['is_skipped']
        if 'skip_reason' in entity_data:
            entity.skip_reason = entity_data['skip_reason']
            
        session.entities.append(entity)
    
    return session
```

## Contract 2: API Layer ↔ Worker Layer

### Task Queue Interface (Django Q)

#### Metadata Extraction Task
```python
# API Layer queues task
from django_q.tasks import async_task

task_id = async_task(
    'agni.tasks.extract_metadata_task',
    session_id=str(session.id)
)

# Worker executes
async def extract_metadata_task(session_id: str) -> None:
    """Extract document metadata using AI."""
    session = StoredExtractionSession.objects.get(id=session_id)
    session.status = 'processing_metadata'
    session.save()
    
    try:
        # Load session data
        agni_session = deserialize_session(session.session_data)
        
        # Process with AgniService
        agni_session = await agni_service.extract_metadata(agni_session)
        
        # Save results
        session.session_data = serialize_session(agni_session)
        session.status = 'metadata_extracted'
        session.task_status = 'completed'
        session.save()
        
        # Auto-trigger entity extraction
        async_task('agni.tasks.extract_entities_task', session_id=session_id)
        
    except Exception as e:
        session.status = 'failed'
        session.task_status = 'failed'
        session.error_message = str(e)
        session.save()
        raise
```

#### Entity Extraction Task
```python
# API Layer queues task
task_id = async_task(
    'agni.tasks.extract_entities_task',
    session_id=str(session.id)
)

# Worker executes
async def extract_entities_task(session_id: str) -> None:
    """Extract and resolve entities from document."""
    session = StoredExtractionSession.objects.get(id=session_id)
    session.status = 'processing_entities'
    session.save()
    
    try:
        agni_session = deserialize_session(session.session_data)
        
        # Extract entities with AI
        agni_session = await agni_service.extract_entities(agni_session)
        
        # Resolve candidates for each entity
        for entity in agni_session.entities:
            entity = await search_service.resolve(entity)
        
        # Save results
        session.session_data = serialize_session(agni_session)
        session.status = 'awaiting_review'
        session.task_status = 'completed'
        session.progress_info = {
            'total_entities': len(agni_session.entities),
            'needs_disambiguation': sum(1 for e in agni_session.entities if e.status == 'needs_disambiguation')
        }
        session.save()
        
    except Exception as e:
        session.status = 'failed'
        session.task_status = 'failed'
        session.error_message = str(e)
        session.save()
        raise
```

#### Persistence Task
```python
# API Layer queues task
task_id = async_task(
    'agni.tasks.persist_changes_task',
    session_id=str(session.id),
    description=description,
    author_id=str(request.user.id)
)

# Worker executes
async def persist_changes_task(session_id: str, description: str, author_id: str) -> None:
    """Persist approved entity changes to NES."""
    session = StoredExtractionSession.objects.get(id=session_id)
    session.status = 'processing_persistence'
    session.save()
    
    try:
        agni_session = deserialize_session(session.session_data)
        
        # Validate all entities are resolved
        for entity in agni_session.entities:
            if entity.status not in ('matched', 'create_new', 'skipped'):
                raise ValueError(f"Entity not resolved: {entity.status}")
        
        # Persist via AgniService
        agni_session = await agni_service.persist(agni_session, description, author_id)
        
        # Update session
        session.status = 'completed'
        session.task_status = 'completed'
        session.save()
        
    except Exception as e:
        session.status = 'failed'
        session.task_status = 'failed'
        session.error_message = str(e)
        session.save()
        raise
```

## Contract 3: Worker Layer ↔ AgniService

### AgniService Interface
```python
class AgniService:
    """Core entity extraction and resolution service."""
    
    async def extract_metadata(
        self, session: AgniExtractionSession
    ) -> AgniExtractionSession:
        """Extract document metadata using AI.
        
        Input: Session with document path
        Output: Session with metadata populated
        Side Effects: Updates metadata conversation
        """
        
    async def extract_entities(
        self, session: AgniExtractionSession
    ) -> AgniExtractionSession:
        """Extract entities from document using AI.
        
        Input: Session with document and metadata
        Output: Session with entities list populated
        Side Effects: Updates entity_extraction conversation
        Requires: metadata must be extracted first
        """
        
    async def set_nes_id_for_extracted_entity(
        self, session: AgniExtractionSession, entity_index: int, nes_id: str
    ) -> AgniExtractionSession:
        """Set matched NES ID for an entity.
        
        Input: Session, entity index, NES ID
        Output: Session with entity.matched_id set
        Side Effects: Updates entity status to 'matched'
        """
        
    async def post_message_to_metadata(
        self, session: AgniExtractionSession, text: str
    ) -> AgniExtractionSession:
        """Post user feedback to metadata conversation.
        
        Input: Session, user message
        Output: Session with updated conversation
        Side Effects: Adds message to metadata_extraction conversation
        """
        
    async def post_message_to_entity_extraction(
        self, session: AgniExtractionSession, text: str
    ) -> AgniExtractionSession:
        """Post user feedback to entity extraction conversation.
        
        Input: Session, user message
        Output: Session with updated conversation
        Side Effects: Adds message to entity_extraction conversation
        """
        
    async def post_message_to_entity(
        self, session: AgniExtractionSession, entity_id: int, text: str
    ) -> AgniExtractionSession:
        """Post user feedback to specific entity conversation.
        
        Input: Session, entity index, user message
        Output: Session with updated conversation
        Side Effects: Adds message to entity:{id} conversation
        """
        
    async def persist(
        self, session: AgniExtractionSession, description: str, author_id: str
    ) -> AgniExtractionSession:
        """Persist all resolved entities to change queue.
        
        Input: Session with all entities resolved, description, author
        Output: Session (unchanged)
        Side Effects: Creates ApprovedEntityChange records (skipped entities ignored)
        Validation: All entities must have status 'matched', 'create_new', or 'skipped'
        """
```

### Protocol Dependencies
```python
class GenAIService(Protocol):
    """AI extraction service."""
    
    async def extract_metadata(
        self, document: Path, conversation: Conversation
    ) -> DocumentMetadata:
        """Extract metadata considering conversation history."""
        
    async def extract_entities(
        self, document: Path, metadata: DocumentMetadata, conversation: Conversation
    ) -> List[ExtractedEntity]:
        """Extract entities considering conversation history."""

class SearchService(Protocol):
    """NES entity resolution service."""
    
    async def find_candidates(
        self, entity: ExtractedEntity
    ) -> List[MatchEntityCandidate]:
        """Find potential NES matches for extracted entity."""
        
    async def resolve(
        self, entity: ExtractedEntity
    ) -> ExtractedEntity:
        """Resolve entity to NES matches or mark for creation."""
        
    def validate_nes_id(
        self, nes_id: str, entity_type: EntityType
    ) -> bool:
        """Validate NES ID format (person_\d+, org_\d+, etc)."""

class Persistence(Protocol):
    """Entity change persistence service."""
    
    async def queue_entity_change(
        self, change: EntityChange, description: str, author_id: str
    ) -> str:
        """Queue entity change to ApprovedEntityChange table."""
        
    async def get_pending_changes(self) -> List[EntityChange]:
        """Retrieve pending entity changes."""
        
    async def apply_change(self, change_id: str) -> None:
        """Apply pending change to NES."""
```

## Data Models

### StoredExtractionSession (Django Model)
```python
class StoredExtractionSession(models.Model):
    id = models.UUIDField(primary_key=True)
    document = models.FileField(upload_to='agni/documents/')
    session_data = models.JSONField()  # Serialized AgniExtractionSession
    
    # Status tracking
    status = models.CharField(choices=[
        ('pending', 'Pending'),
        ('processing_metadata', 'Processing Metadata'),
        ('metadata_extracted', 'Metadata Extracted'),
        ('processing_entities', 'Processing Entities'),
        ('awaiting_review', 'Awaiting Review'),
        ('processing_persistence', 'Processing Persistence'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    
    # Task tracking
    current_task_id = models.CharField(max_length=100, blank=True)
    task_status = models.CharField(choices=[
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    
    error_message = models.TextField(blank=True)
    progress_info = models.JSONField(default=dict)
    
    # Audit
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### AgniExtractionSession (Dataclass)
```python
@dataclass
class AgniExtractionSession:
    document: Optional[Path] = None
    metadata: Optional[DocumentMetadata] = None
    conversations: Dict[str, Conversation] = field(default_factory=dict)
    entities: List[ExtractedEntity] = field(default_factory=list)
    guidance: Optional[str] = None
```

### ExtractedEntity (Dataclass)
```python
@dataclass
class ExtractedEntity:
    entity_type: EntityType
    entity_sub_type: Optional[EntitySubType] = None
    names: List[Dict[str, Any]] = field(default_factory=list)
    entity_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    
    # Matching state
    candidates: List[MatchEntityCandidate] = field(default_factory=list)
    matched_id: Optional[str] = None
    needs_creation: bool = False
    proposed_changes: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def status(self) -> str:
        """Returns: 'create_new', 'matched', 'skipped', or 'needs_disambiguation'"""
        if self.needs_creation:
            return "create_new"
        if self.matched_id:
            return "matched"
        if hasattr(self, 'is_skipped') and self.is_skipped:
            return "skipped"
        if self.candidates:
            return "needs_disambiguation"
        raise ValueError("Entity not resolved")
```

### ApprovedEntityChange (Django Model)
```python
class ApprovedEntityChange(models.Model):
    id = models.UUIDField(primary_key=True)
    change_type = models.CharField(choices=['create', 'update'])
    entity_type = models.CharField(max_length=20)
    entity_sub_type = models.CharField(max_length=50, blank=True)
    nes_entity_id = models.CharField(max_length=300, blank=True)
    entity_data = models.JSONField()
    description = models.TextField(blank=True)
    approved_by = models.ForeignKey(User)
    approved_at = models.DateTimeField(auto_now_add=True)
```

## Status Flow

```
pending
  ↓ (upload complete, task queued)
processing_metadata
  ↓ (metadata extracted)
metadata_extracted
  ↓ (auto-trigger entity extraction)
processing_entities
  ↓ (entities extracted and resolved)
awaiting_review
  ↓ (user approves, persist task queued)
processing_persistence
  ↓ (changes persisted)
completed

# Error path from any processing state
* → failed (with error_message)
```

## Error Handling

### API Layer Errors
```python
# Standard error response
{
  "success": false,
  "error": "validation_error",
  "message": "All entities must be resolved before persistence"
}

# Error codes:
# - validation_error: Invalid input
# - not_found: Session/entity not found
# - invalid_state: Operation not allowed in current state
# - server_error: Internal error
```

### Worker Layer Errors
```python
# Task failure handling
try:
    result = await agni_service.extract_metadata(session)
except Exception as e:
    session.status = 'failed'
    session.task_status = 'failed'
    session.error_message = str(e)
    session.save()
    # Log error with context
    logger.error(f"Task failed: {session_id}", exc_info=True)
    raise
```

## Configuration

```python
# settings.py
NES_API_BASE_URL = env('NES_API_BASE_URL', default='https://nes-api.jawafdehi.org')
NES_API_TIMEOUT = 10

# Django Q configuration
Q_CLUSTER = {
    'name': 'agni',
    'workers': 4,
    'timeout': 600,  # 10 minutes
    'retry': 3600,   # Retry after 1 hour
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
}
```
