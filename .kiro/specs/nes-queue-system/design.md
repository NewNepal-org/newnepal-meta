# Design Document: NES Queue System (NESQ)

## Overview

The NES Queue System (NESQ) is a queue-based API feature for the Jawafdehi API that replaces the migration-based approach for updating the Nepal Entity Service (NES) database. The system enables authenticated contributors to submit requests to add names (including misspellings) to existing entities through a REST API endpoint, provides admin/moderator approval workflows via Django admin interface, and processes approved requests through a daily GitHub Actions cron job that integrates with the NES PublicationService to commit changes to the nes-db repository.

**Initial Scope**: This MVP focuses exclusively on the ADD_NAME action. CREATE_ENTITY and UPDATE_ENTITY actions are planned for future releases.

## Main Algorithm/Workflow

```mermaid
sequenceDiagram
    participant Contributor
    participant API as Jawafdehi API
    participant DB as PostgreSQL
    participant Admin as Django Admin
    participant Cron as GitHub Actions
    participant NES as NES PublicationService
    participant Repo as nes-db Repository
    
    Contributor->>API: POST /api/submit_nes_change (token auth)
    Note over API: ADD_NAME action only (MVP)
    API->>API: Validate payload
    API->>DB: Create NESQueueItem
    alt Admin/Moderator
        API->>DB: Set status=APPROVED
    else Contributor
        API->>DB: Set status=PENDING
    end
    API-->>Contributor: Return queue item
    
    opt Manual Review Required
        Admin->>DB: Query PENDING items
        Admin->>DB: Update status to APPROVED/REJECTED
    end
    
    Note over Cron: Daily at midnight UTC
    Cron->>DB: Query APPROVED items
    loop For each approved item
        Cron->>NES: Call PublicationService method
        alt Success
            NES->>Repo: Write to nes-db/v2
            Cron->>DB: Set status=COMPLETED
        else Failure
            Cron->>DB: Set status=FAILED, store error
        end
    end
    Note over Cron: Git operations as workflow steps
    Cron->>Repo: git add, commit & push (shell steps)
```

## Architecture

```mermaid
graph TB
    subgraph "Jawafdehi API Service"
        API[REST API Endpoint<br/>/api/submit_nes_change]
        Models[Django Models<br/>NESQueueItem]
        Admin[Django Admin<br/>Review Interface]
        Processor[Queue Processor<br/>Management Command]
        
        API --> Models
        Admin --> Models
        Processor --> Models
    end
    
    subgraph "Authentication"
        Token[DRF Token Auth]
        Perms[Role-Based Permissions]
        
        Token --> API
        Perms --> API
    end
    
    subgraph "NES Integration"
        PubService[PublicationService]
        FileDB[FileDatabase<br/>nes-db/v2]
        
        Processor --> PubService
        PubService --> FileDB
    end
    
    subgraph "Automation"
        GHA[GitHub Actions<br/>Daily Cron]
        Git[Git Operations<br/>Workflow Shell Steps]
        
        GHA --> Processor
        GHA --> Git
        Git --> FileDB
    end
    
    subgraph "External Systems"
        NESRepo[nes-db Repository]
        
        Git --> NESRepo
    end
```


## Components and Interfaces

### Component 1: NESQueueItem Model

**Purpose**: Core data model representing a single entity update request in the queue

**Interface**:
```python
class NESQueueItem(models.Model):
    action: CharField  # QueueAction enum
    payload: JSONField  # Action-specific data
    status: CharField  # QueueStatus enum
    submitted_by: ForeignKey(User)
    reviewed_by: ForeignKey(User, null=True)
    reviewed_at: DateTimeField(null=True)
    processed_at: DateTimeField(null=True)
    change_description: TextField
    error_message: TextField(blank=True)
    result: JSONField(null=True)
    created_at: DateTimeField(auto_now_add=True)
    updated_at: DateTimeField(auto_now=True)
```

**Responsibilities**:
- Store queue item data with full audit trail
- Track status transitions through workflow
- Maintain relationships to users (submitter and reviewer)
- Store processing results and error messages

### Component 2: Queue API Endpoint

**Purpose**: REST API endpoint for submitting entity update requests

**Interface**:
```python
class SubmitNESChangeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(request) -> Response:
        """
        Submit a new NES entity update request
        
        Request Body:
        {
            "action": "ADD_NAME",  # MVP: Only ADD_NAME supported
            "payload": {...},  # AddNamePayload structure
            "change_description": "string",
            "auto_approve": false  # Optional, only Admin/Moderator can set to true
        }
        
        Returns:
        {
            "id": int,
            "action": string,
            "status": string,
            "submitted_by": string,
            "created_at": datetime
        }
        """
```

**Responsibilities**:
- Authenticate requests using DRF token authentication
- Validate action and auto_approve flag using DRF serializers
- Validate payload structure using Pydantic models (action-specific schemas)
- Validate auto_approve flag (only Admin/Moderator can set to true)
- Create queue items with appropriate status based on auto_approve flag

### Component 2.5: Pydantic Payload Validators

**Purpose**: Action-specific payload validation using Pydantic models

**Interface**:
```python
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any
from nes.core.identifiers.validators import validate_entity_id

class AddNamePayload(BaseModel):
    """Payload for ADD_NAME action - adds name or misspelling to existing entity
    
    MVP: This is the only supported action in the initial release.
    Future: CREATE_ENTITY and UPDATE_ENTITY will be added later.
    """
    entity_id: str
    name: Dict[str, Any]
    is_misspelling: bool = False
    
    @field_validator('entity_id')
    @classmethod
    def validate_entity_id_format(cls, v: str) -> str:
        """Validate entity_id using NES validator"""
        validate_entity_id(v)
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if 'kind' not in v:
            raise ValueError('name.kind is required')
        if v['kind'] not in ['PRIMARY', 'ALIAS', 'ALTERNATE', 'BIRTH_NAME']:
            raise ValueError('invalid name.kind')
        if 'en' not in v and 'ne' not in v:
            raise ValueError('name must have at least one of en or ne')
        return v
```

**Responsibilities**:
- Define ADD_NAME payload schema using Pydantic
- Validate payload structure and field constraints using Pydantic v2 syntax
- Use existing NES validator (`validate_entity_id`) for ID validation
- Provide detailed validation error messages
- Ensure type safety for payload data

**Key Design Decisions**:
- MVP focuses exclusively on `AddNamePayload` - other actions deferred to future releases
- No `author_id` field - the authenticated user's username is used automatically
- Entity ID validation uses existing NES validator from `services/nes/nes/core/identifiers/validators.py`
- Pydantic v2 syntax with `@field_validator` decorator (not deprecated `@validator`)
- `is_misspelling` flag determines whether name goes to `names` or `misspelled_names` array

### Component 3: Django Admin Interface

**Purpose**: Administrative interface for reviewing and approving queue items

**Interface**:
```python
class NESQueueItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'action', 'status', 'submitted_by', 'reviewed_by', 'created_at']
    list_filter = ['status', 'action', 'created_at']
    search_fields = ['change_description', 'submitted_by__username']
    actions = ['bulk_approve', 'bulk_reject']
    
    def bulk_approve(modeladmin, request, queryset) -> None:
        """Bulk approve selected PENDING items"""
    
    def bulk_reject(modeladmin, request, queryset) -> None:
        """Bulk reject selected PENDING items"""
```

**Responsibilities**:
- Display queue items with filtering and search
- Provide bulk approval/rejection actions
- Track reviewer and review timestamp
- Prevent modification of completed/failed items

### Component 4: Queue Processor

**Purpose**: Process approved queue items by calling NES PublicationService

**Interface**:
```python
class QueueProcessor:
    def __init__(self, nes_db_path: str):
        """Initialize with path to nes-db repository"""
    
    async def process_approved_items(self) -> ProcessingResult:
        """
        Process all approved queue items in order
        
        Returns:
        {
            "processed": int,
            "completed": int,
            "failed": int,
            "errors": List[Dict]
        }
        """
    
    async def process_item(self, item: NESQueueItem) -> bool:
        """Process a single queue item"""
```

**Responsibilities**:
- Query approved items in chronological order
- Augment change descriptions with submitter username
- Call appropriate NES PublicationService methods
- Handle success/failure status updates

**Note**: Git operations (add, commit, push) are NOT part of the QueueProcessor. They are handled by GitHub Actions workflow shell steps after the processor completes.

### Component 5: NES PublicationService Integration

**Purpose**: Interface to NES entity management operations

**Interface**:
```python
class PublicationService:
    async def create_entity(
        self,
        entity_data: Dict[str, Any],
        author_id: str,
        change_description: str
    ) -> Entity:
        """Create a new entity in NES database"""
    
    async def update_entity(
        self,
        entity: Entity,
        author_id: str,
        change_description: str
    ) -> Entity:
        """Update an existing entity in NES database"""
    
    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieve an entity by ID"""
```

**Responsibilities**:
- Create new entities with validation
- Update existing entities with merge logic
- Maintain version history with change descriptions
- Write changes to FileDatabase (nes-db/v2)


## Data Models

### QueueAction Enum

```python
class QueueAction(models.TextChoices):
    ADD_NAME = "ADD_NAME", "Add Name"
    # Future actions (not in MVP):
    # CREATE_ENTITY = "CREATE_ENTITY", "Create Entity"
    # UPDATE_ENTITY = "UPDATE_ENTITY", "Update Entity"
```

**Values**:
- `ADD_NAME` — Add name or misspelled name to existing entity (MVP - only supported action)

**Future Actions** (deferred to later releases):
- `CREATE_ENTITY` — Create a new NES entity (person, organization, location, project)
- `UPDATE_ENTITY` — Patch existing entity attributes (merge update)

### QueueStatus Enum

```python
class QueueStatus(models.TextChoices):
    PENDING = "PENDING", "Pending Review"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
```

**Status Workflow**:
```mermaid
stateDiagram-v2
    [*] --> PENDING: Contributor submits
    [*] --> APPROVED: Admin/Moderator submits
    PENDING --> APPROVED: Admin approves
    PENDING --> REJECTED: Admin rejects
    APPROVED --> COMPLETED: Processing succeeds
    APPROVED --> FAILED: Processing fails
    COMPLETED --> [*]
    FAILED --> [*]
    REJECTED --> [*]
```

### NESQueueItem Model Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing ID |
| `action` | CharField(20) | Choices: QueueAction | Type of entity operation |
| `payload` | JSONField | Not null | Action-specific data structure |
| `status` | CharField(20) | Choices: QueueStatus, default=PENDING | Current workflow status |
| `submitted_by` | ForeignKey(User) | Not null, on_delete=PROTECT | User who submitted request |
| `reviewed_by` | ForeignKey(User) | Null, on_delete=SET_NULL | Admin who reviewed |
| `reviewed_at` | DateTimeField | Null | Timestamp of review |
| `processed_at` | DateTimeField | Null | Timestamp of processing |
| `change_description` | TextField | Not null | Human-readable change description |
| `error_message` | TextField | Blank | Error details if processing failed |
| `result` | JSONField | Null | Processing result data (e.g., entity ID) |
| `created_at` | DateTimeField | Auto-add | Submission timestamp |
| `updated_at` | DateTimeField | Auto-update | Last modification timestamp |

**Validation Rules**:
- `payload` structure must match the selected `action` type
- `status` transitions must follow the workflow diagram
- `reviewed_by` and `reviewed_at` must be set together when status changes to APPROVED/REJECTED
- `processed_at` must be set when status changes to COMPLETED/FAILED
- `error_message` required when status is FAILED
- `result` should be populated when status is COMPLETED

**Indexes**:
- `status` (for filtering approved items, then sort by created_at in application code for FIFO processing)


## Algorithmic Pseudocode

### API Request Processing Algorithm

```pascal
ALGORITHM processSubmitRequest(request)
INPUT: request containing action, payload, change_description, auto_approve (optional), authenticated user
OUTPUT: queue_item with appropriate status

BEGIN
  ASSERT request.user IS authenticated
  
  // Step 1: Validate request structure (DRF serializer)
  serializer ← NESQueueSubmitSerializer(data=request.data)
  IF NOT serializer.is_valid() THEN
    RETURN ValidationError(serializer.errors)
  END IF
  
  // Step 2: Validate payload using Pydantic (ADD_NAME only in MVP)
  action ← serializer.validated_data.action
  payload ← serializer.validated_data.payload
  
  // MVP: Only ADD_NAME is supported
  IF action ≠ ADD_NAME THEN
    RETURN ValidationError({"action": "Only ADD_NAME action is supported in this version"})
  END IF
  
  TRY
    validated_payload ← AddNamePayload(**payload)
  CATCH ValidationError AS e
    RETURN ValidationError({"payload": e.errors()})
  END TRY
  
  // Step 3: Validate auto_approve flag
  auto_approve ← serializer.validated_data.get('auto_approve', False)
  IF auto_approve = True THEN
    IF request.user.role NOT IN [ADMIN, MODERATOR] THEN
      RETURN PermissionDenied("Only Admin/Moderator can set auto_approve=true")
    END IF
  END IF
  
  // Step 4: Determine initial status based on auto_approve flag
  IF auto_approve = True THEN
    initial_status ← APPROVED
    reviewed_by ← request.user
    reviewed_at ← now()
  ELSE
    initial_status ← PENDING
    reviewed_by ← NULL
    reviewed_at ← NULL
  END IF
  
  // Step 5: Create queue item
  queue_item ← NESQueueItem.create(
    action=action,
    payload=payload,
    change_description=serializer.validated_data.change_description,
    submitted_by=request.user,
    status=initial_status,
    reviewed_by=reviewed_by,
    reviewed_at=reviewed_at
  )
  
  // Step 6: Return response
  response_data ← NESQueueItemSerializer(queue_item).data
  RETURN Response(response_data, status=201)
END
```

**Preconditions**:
- Request user is authenticated with valid token
- Request contains valid action, payload, and change_description
- Payload structure matches Pydantic schema for the specified action
- If auto_approve=true, user must be Admin or Moderator

**Postconditions**:
- Queue item created in database with appropriate status
- Response contains queue item ID and status
- Payload has been validated by both DRF serializer and Pydantic model
- If auto_approve=true: status=APPROVED, reviewed_by and reviewed_at are set
- If auto_approve=false or omitted: status=PENDING, reviewed_by and reviewed_at are NULL

### Queue Processing Algorithm

```pascal
ALGORITHM processApprovedQueue()
INPUT: None (queries database for approved items)
OUTPUT: processing_result with counts and errors

BEGIN
  // Step 1: Initialize NES PublicationService
  database ← FileDatabase(NES_DB_PATH)
  publication_service ← PublicationService(database)
  
  // Step 2: Query approved items in chronological order
  approved_items ← NESQueueItem.objects.filter(status=APPROVED).order_by('created_at')
  
  processed_count ← 0
  completed_count ← 0
  failed_count ← 0
  errors ← []
  
  // Step 3: Process each item with loop invariant
  FOR each item IN approved_items DO
    ASSERT item.status = APPROVED
    ASSERT all_previous_items_processed(processed_count)
    ASSERT item.action = ADD_NAME  // MVP: Only ADD_NAME supported
    
    TRY
      // Augment change description with submitter
      augmented_description ← item.change_description + " (submitted by " + item.submitted_by.username + ")"
      
      // Use authenticated user's username as author_id
      author_id ← "jawafdehi:" + item.submitted_by.username
      
      // Process ADD_NAME action
      existing_entity ← await publication_service.get_entity(item.payload.entity_id)
      IF existing_entity IS NULL THEN
        RAISE EntityNotFoundError
      END IF
      
      IF item.payload.is_misspelling = true THEN
        existing_entity.misspelled_names.append(item.payload.name)
      ELSE
        existing_entity.names.append(item.payload.name)
      END IF
      
      result ← await publication_service.update_entity(
        entity=existing_entity,
        author_id=author_id,
        change_description=augmented_description
      )
      
      // Update item to completed
      item.status ← COMPLETED
      item.result ← serialize(result)
      item.processed_at ← now()
      item.save()
      
      completed_count ← completed_count + 1
      
    CATCH error AS e
      // Update item to failed
      item.status ← FAILED
      item.error_message ← str(e)
      item.processed_at ← now()
      item.save()
      
      failed_count ← failed_count + 1
      errors.append({item_id: item.id, error: str(e)})
    END TRY
    
    processed_count ← processed_count + 1
  END FOR
  
  RETURN {
    processed: processed_count,
    completed: completed_count,
    failed: failed_count,
    errors: errors
  }
  
  // Note: Git add, commit, push are handled by GitHub Actions workflow steps
  // after this algorithm completes. See .github/workflows/process-nes-queue.yml
END
```

**Preconditions**:
- NES_DB_PATH environment variable is set and valid
- nes-db repository is cloned and accessible
- Git credentials are configured for pushing
- At least one item with status=APPROVED exists

**Postconditions**:
- All approved items have been processed
- Successful items have status=COMPLETED with result data
- Failed items have status=FAILED with error messages
- All items have processed_at timestamp set
- Changes written to nes-db filesystem (git add/commit/push handled separately by GitHub Actions)

**Loop Invariants**:
- All previously processed items have status ∈ {COMPLETED, FAILED}
- processed_count = completed_count + failed_count
- All items maintain data integrity (no partial updates)


### Payload Validation Algorithm

```pascal
ALGORITHM validatePayload(action, payload)
INPUT: action (QueueAction enum), payload (JSON object)
OUTPUT: validated_payload or ValidationError

BEGIN
  // MVP: Only ADD_NAME is supported
  IF action ≠ ADD_NAME THEN
    RAISE ValidationError("Only ADD_NAME action is supported in this version")
  END IF
  
  // Validate ADD_NAME payload
  ASSERT payload.entity_id MATCHES "^entity:(person|organization|location|project)/.+$"
  ASSERT payload.name IS NOT NULL
  ASSERT payload.name.en IS NOT NULL OR payload.name.ne IS NOT NULL
  ASSERT payload.name.kind IN ["PRIMARY", "ALIAS", "ALTERNATE", "BIRTH_NAME"]
  
  IF payload.is_misspelling IS NULL THEN
    payload.is_misspelling ← false
  END IF
  
  RETURN payload
END
```

**Preconditions**:
- action is a valid QueueAction enum value
- payload is a valid JSON object

**Postconditions**:
- Returns validated payload if all assertions pass
- Raises ValidationError with specific message if any assertion fails
- Payload structure matches expected schema for the action type


## Key Functions with Formal Specifications

### Function 1: create_queue_item()

```python
def create_queue_item(
    action: QueueAction,
    payload: Dict[str, Any],
    change_description: str,
    submitted_by: User
) -> NESQueueItem
```

**Preconditions:**
- `action` is a valid QueueAction enum value
- `payload` is validated against action-specific schema
- `change_description` is non-empty string
- `submitted_by` is authenticated User instance

**Postconditions:**
- Returns NESQueueItem instance with status=PENDING or APPROVED
- Item persisted to database with created_at timestamp
- If submitted_by is Admin/Moderator: status=APPROVED
- If submitted_by is Contributor: status=PENDING
- All required fields populated correctly

**Loop Invariants:** N/A (no loops)

### Function 2: process_queue_item()

```python
async def process_queue_item(
    item: NESQueueItem,
    publication_service: PublicationService
) -> bool
```

**Preconditions:**
- `item.status` equals APPROVED
- `publication_service` is initialized with valid FileDatabase
- `item.payload` is valid for `item.action`
- NES database is accessible and writable

**Postconditions:**
- Returns True if processing succeeds, False otherwise
- If successful: `item.status` = COMPLETED, `item.result` populated, `item.processed_at` set
- If failed: `item.status` = FAILED, `item.error_message` populated, `item.processed_at` set
- Item changes persisted to database
- NES database updated with entity changes (on success)

**Loop Invariants:** N/A (no loops)

### Function 3: validate_action_payload()

```python
def validate_action_payload(
    action: QueueAction,
    payload: Dict[str, Any]
) -> BaseModel
```

**Preconditions:**
- `action` is valid QueueAction enum value
- `payload` is dictionary (may be invalid structure)

**Postconditions:**
- Returns validated Pydantic model instance if all checks pass
- Raises Pydantic ValidationError with descriptive message if validation fails
- Returned model matches expected Pydantic schema for action type
- No side effects on input parameters

**Implementation:**
```python
def validate_action_payload(action: QueueAction, payload: Dict[str, Any]) -> BaseModel:
    """Validate payload using action-specific Pydantic model
    
    MVP: Only ADD_NAME is supported in this version.
    """
    if action == QueueAction.ADD_NAME:
        return AddNamePayload(**payload)
    else:
        raise ValueError(f"Action {action} is not supported in this version. Only ADD_NAME is available.")
```

**Loop Invariants:**
- For name validation loops: All previously checked names are valid
- For field validation loops: All previously checked fields pass constraints

### Function 4: augment_change_description()

```python
def augment_change_description(
    item: NESQueueItem
) -> str
```

**Preconditions:**
- `item` is valid NESQueueItem instance
- `item.change_description` is non-empty string
- `item.submitted_by` is valid User with username

**Postconditions:**
- Returns string in format: "{original_description} (submitted by {username})"
- Original item.change_description unchanged
- Result is non-empty string
- Username properly escaped for NES version history

**Loop Invariants:** N/A (no loops)

### Function 5: Git Operations (GitHub Actions)

**Note**: Git operations (add, commit, push) are handled as shell steps in the GitHub Actions workflow, not as Python functions. The workflow checks for changes after `process_queue` completes and performs:

```yaml
# In .github/workflows/process-nes-queue.yml
- name: Commit and push NES changes
  working-directory: nes-db
  run: |
    git add .
    if git diff --cached --quiet; then
      echo "No changes to commit"
    else
      git commit -m "Process NESQ items"
      git push
    fi
```

**Preconditions:**
- Process queue management command completed successfully
- Git credentials configured in workflow
- nes-db repository checked out with write access

**Postconditions:**
- If changes exist: committed and pushed to remote
- If no changes: skipped gracefully
- Workflow fails visibly if push fails


## Example Usage

### Example 1: Submit ADD_NAME Request (Contributor)

```python
# API Request
POST /api/submit_nes_change
Authorization: Token contributor_token
Content-Type: application/json

{
  "action": "ADD_NAME",
  "payload": {
    "entity_id": "entity:person/sher-bahadur-deuba",
    "name": {
      "kind": "ALIAS",
      "en": {"full": "S.B. Deuba"}
    },
    "is_misspelling": false
  },
  "change_description": "Adding common alias for Sher Bahadur Deuba"
}

# API Response (201 Created)
{
  "id": 42,
  "action": "ADD_NAME",
  "status": "PENDING",
  "submitted_by": "contributor_user",
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Example 2: Submit ADD_NAME Request with Misspelling (Admin with auto_approve)

```python
# API Request
POST /api/submit_nes_change
Authorization: Token admin_token_xyz
Content-Type: application/json

{
  "action": "ADD_NAME",
  "payload": {
    "entity_id": "entity:person/sher-bahadur-deuba",
    "name": {
      "kind": "ALIAS",
      "ne": {"full": "शेर बहादुर देउबा"}  # Common misspelling with space
    },
    "is_misspelling": true
  },
  "change_description": "Adding common misspelling with space",
  "auto_approve": true
}

# API Response (201 Created)
{
  "id": 43,
  "action": "ADD_NAME",
  "status": "APPROVED",  # Auto-approved via flag
  "submitted_by": "admin_user",
  "reviewed_by": "admin_user",
  "reviewed_at": "2025-01-15T11:00:00Z",
  "created_at": "2025-01-15T11:00:00Z"
}
```

### Example 3: Admin Approval in Django Admin

```python
# Admin selects pending items and uses bulk approve action
# Django Admin Action
def bulk_approve(modeladmin, request, queryset):
    pending_items = queryset.filter(status=QueueStatus.PENDING)
    for item in pending_items:
        item.status = QueueStatus.APPROVED
        item.reviewed_by = request.user
        item.reviewed_at = timezone.now()
        item.save()
    
    count = pending_items.count()
    modeladmin.message_user(
        request,
        f"{count} items approved successfully"
    )
```

### Example 4: Queue Processing (GitHub Actions Cron)

```python
# Management command execution
# Command: poetry run python manage.py process_queue

from nesq.processor import QueueProcessor

processor = QueueProcessor(nes_db_path=settings.NES_DB_PATH)
result = asyncio.run(processor.process_approved_items())

# Console Output
"""
Processing 2 approved queue items...
[1/2] Processing ADD_NAME for entity:person/sher-bahadur-deuba... ✓ COMPLETED
[2/2] Processing ADD_NAME for entity:person/sher-bahadur-deuba... ✓ COMPLETED

Summary:
- Processed: 2
- Completed: 2
- Failed: 0
"""

# Git operations happen as subsequent GitHub Actions workflow steps:
# - git add .
# - git diff --cached --quiet || git commit -m "Process NESQ items: 2 completed, 0 failed"
# - git push
```

### Example 5: Error Handling - Unsupported Action

```python
# API Request with unsupported action
POST /api/submit_nes_change
Authorization: Token token123
Content-Type: application/json

{
  "action": "CREATE_ENTITY",
  "payload": {...},
  "change_description": "Trying to create entity"
}

# API Response (400 Bad Request)
{
  "action": ["Only ADD_NAME action is supported in this version"]
}
```

### Example 6: Error Handling - Entity Not Found

```python
# API Request with invalid entity_id
POST /api/submit_nes_change
Authorization: Token token123
Content-Type: application/json

{
  "action": "UPDATE_ENTITY",
  "payload": {
    "entity_id": "entity:person/non-existent-person",
    "updates": {"tags": ["test"]},
    "author_id": "jawafdehi-queue"
  },
  "change_description": "Test update"
}

# Processing Result (during cron)
# Item status: FAILED
# Error message: "Entity does not exist: entity:person/non-existent-person"
```


## Correctness Properties

### Universal Quantification Properties

**Property 1: Status Transition Validity**
```
∀ item ∈ NESQueueItem:
  (item.status = PENDING ⟹ item.reviewed_by = NULL ∧ item.reviewed_at = NULL) ∧
  (item.status ∈ {APPROVED, REJECTED} ⟹ item.reviewed_by ≠ NULL ∧ item.reviewed_at ≠ NULL) ∧
  (item.status ∈ {COMPLETED, FAILED} ⟹ item.processed_at ≠ NULL)
```

**Property 2: Auto-Approval Correctness**
```
∀ item ∈ NESQueueItem:
  (item.status = APPROVED at creation ⟹ 
    auto_approve_flag = true ∧ 
    item.submitted_by.role ∈ {ADMIN, MODERATOR} ∧
    item.reviewed_by = item.submitted_by ∧
    item.reviewed_at ≠ NULL) ∧
  (auto_approve_flag = false ∨ auto_approve_flag = NULL ⟹ 
    item.status = PENDING at creation ∧
    item.reviewed_by = NULL ∧
    item.reviewed_at = NULL)
```

**Property 3: Payload Validity**
```
∀ item ∈ NESQueueItem:
  (item.action = ADD_NAME ⟹
    item.payload.entity_id ≠ NULL ∧
    item.payload.name ≠ NULL ∧
    (item.payload.name.en ≠ NULL ∨ item.payload.name.ne ≠ NULL))
```

**Note**: MVP only supports ADD_NAME action. CREATE_ENTITY and UPDATE_ENTITY properties will be added in future releases.

**Property 4: Processing Idempotency**
```
∀ item ∈ NESQueueItem:
  item.status ∈ {COMPLETED, FAILED, REJECTED} ⟹ 
    item will not be processed again by queue processor
```

**Property 5: Change Description Augmentation**
```
∀ item ∈ NESQueueItem processed by queue:
  NES_change_description = item.change_description + " (submitted by " + item.submitted_by.username + ")"
```

**Property 6: Atomic Processing**
```
∀ item ∈ NESQueueItem:
  (processing_started(item) ∧ ¬processing_completed(item)) ⟹
    item.status remains APPROVED ∧
    no partial changes written to NES database
```

**Property 7: Chronological Processing Order**
```
∀ item1, item2 ∈ NESQueueItem where item1.status = APPROVED ∧ item2.status = APPROVED:
  item1.created_at < item2.created_at ⟹ 
    item1 processed before item2
```

**Property 8: Result Storage Consistency**
```
∀ item ∈ NESQueueItem:
  (item.status = COMPLETED ⟹ item.result ≠ NULL ∧ item.error_message = "") ∧
  (item.status = FAILED ⟹ item.error_message ≠ "" ∧ item.result = NULL)
```


## Error Handling

### Error Scenario 1: Invalid Authentication

**Condition**: Request without valid token or with expired token
**Response**: HTTP 401 Unauthorized with error message
**Recovery**: User must obtain valid authentication token

```python
{
  "detail": "Authentication credentials were not provided."
}
# or
{
  "detail": "Invalid token."
}
```

### Error Scenario 2: Invalid Payload Structure

**Condition**: Payload doesn't match expected Pydantic schema for action type
**Response**: HTTP 400 Bad Request with Pydantic validation errors
**Recovery**: Client must correct payload structure and resubmit

```python
{
  "payload": [
    {
      "loc": ["entity_data", "slug"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["entity_data", "names"],
      "msg": "at least one name with kind='PRIMARY' is required",
      "type": "value_error"
    }
  ]
}
```

### Error Scenario 3: Entity Not Found (During Processing)

**Condition**: UPDATE_ENTITY or ADD_NAME references non-existent entity_id
**Response**: Item status set to FAILED with error message
**Recovery**: Admin reviews error, corrects entity_id, creates new queue item

```python
# Queue item after processing
{
  "status": "FAILED",
  "error_message": "Entity does not exist: entity:person/non-existent-slug",
  "processed_at": "2025-01-15T12:00:00Z"
}
```

### Error Scenario 4: Duplicate Entity (During Processing)

**Condition**: CREATE_ENTITY with slug that already exists
**Response**: Item status set to FAILED with error message
**Recovery**: Admin reviews error, uses UPDATE_ENTITY instead or chooses different slug

```python
# Queue item after processing
{
  "status": "FAILED",
  "error_message": "Entity with slug 'sher-bahadur-deuba' already exists",
  "processed_at": "2025-01-15T12:00:00Z"
}
```

### Error Scenario 5: NES Validation Error (During Processing)

**Condition**: Payload data doesn't pass NES Pydantic model validation
**Response**: Item status set to FAILED with detailed validation error
**Recovery**: Admin reviews error, corrects data structure, creates new queue item

```python
# Queue item after processing
{
  "status": "FAILED",
  "error_message": "ValidationError: 1 validation error for Person\npersonal_details.gender\n  Input should be 'male', 'female', or 'other' (type=value_error)",
  "processed_at": "2025-01-15T12:00:00Z"
}
```

### Error Scenario 6: Git Push Failure

**Condition**: Unable to push changes to nes-db repository (network, permissions, conflicts)
**Response**: GitHub Actions workflow step fails, error is visible in workflow logs
**Recovery**: GitHub Actions workflow retries on next scheduled run, manual intervention if persistent

**Note**: Git operations are handled as shell steps in the GitHub Actions workflow, not in Python code. Failures are surfaced through GitHub Actions workflow status.

```yaml
# GitHub Actions workflow step
- name: Push NES changes
  working-directory: nes-db
  run: |
    git push
    # Failure here causes the workflow step to fail visibly
```

### Error Scenario 7: Immutable Field Modification Attempt

**Condition**: UPDATE_ENTITY payload contains immutable fields (slug, type, sub_type, id)
**Response**: HTTP 400 Bad Request with validation error
**Recovery**: Client removes immutable fields from updates and resubmits

```python
{
  "payload": {
    "updates": {
      "slug": ["Cannot modify immutable field: slug"]
    }
  }
}
```

### Error Scenario 8: Unauthorized Auto-Approve Attempt

**Condition**: Contributor (non-Admin/Moderator) tries to set auto_approve=true
**Response**: HTTP 403 Forbidden with permission error
**Recovery**: Remove auto_approve flag or authenticate as Admin/Moderator

```python
{
  "detail": "Only Admin/Moderator can set auto_approve=true"
}
```

### Error Scenario 9: NES Database Access Failure

**Condition**: NES_DB_PATH invalid or nes-db repository not accessible
**Response**: Processing fails immediately, error logged
**Recovery**: Verify NES_DB_PATH configuration, ensure nes-db repository is cloned

```python
# Console output
"""
Error: Cannot access NES database
Details: FileNotFoundError: [Errno 2] No such file or directory: '/path/to/nes-db/v2'
Action: Verify NES_DB_PATH environment variable and repository clone
Status: Processing aborted, no items modified
"""
```


## Testing Strategy

### Unit Testing Approach

Comprehensive unit tests for all components with focus on:
- Model creation and validation
- Serializer payload validation for each action type
- API endpoint authentication and authorization
- Status transition logic
- Error handling and edge cases

**Test Coverage Goals**: Minimum 90% code coverage for nesq app

**Key Test Categories**:
1. Model tests (`test_models.py`) - 8 tests covering field validation, status choices, ordering
2. Serializer tests (`test_serializers.py`) - 29 tests covering all action types and validation rules
3. API view tests (`test_api_views.py`) - 10 tests covering authentication, authorization, auto-approval
4. Processor tests (`test_processor.py`) - 15 tests covering queue processing, error handling, ordering
5. Admin tests (`test_admin.py`) - 5 tests covering bulk actions and review workflow

**Test Execution**:
```bash
cd services/jawafdehi-api
poetry run pytest tests/nesq/ -v --cov=nesq --cov-report=html
```

### Property-Based Testing Approach

Use hypothesis for property-based testing of critical invariants:

**Property Test Library**: hypothesis (Python)

**Property Tests**:

1. **Status Transition Property**
```python
@given(st.sampled_from(QueueStatus))
def test_status_transitions_maintain_invariants(initial_status):
    """All status transitions maintain required field invariants"""
    # Property: Status transitions always set required fields correctly
```

2. **Payload Validation Property**
```python
@given(
    action=st.sampled_from(QueueAction),
    payload=st.dictionaries(st.text(), st.text())
)
def test_payload_validation_is_consistent(action, payload):
    """Payload validation is deterministic and consistent"""
    # Property: Same payload always produces same validation result
```

3. **Processing Order Property**
```python
@given(st.lists(st.datetimes(), min_size=2))
def test_processing_respects_chronological_order(timestamps):
    """Queue items always processed in chronological order"""
    # Property: created_at ordering is preserved during processing
```

4. **Change Description Augmentation Property**
```python
@given(
    description=st.text(min_size=1),
    username=st.text(min_size=1, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))
)
def test_change_description_augmentation_format(description, username):
    """Change descriptions always augmented with correct format"""
    # Property: Augmented description always ends with " (submitted by {username})"
```

### Integration Testing Approach

Integration tests for end-to-end workflows:

1. **API to Database Integration**
   - Submit request → verify database state
   - Test with different user roles
   - Verify auto-approval logic

2. **Queue Processor to NES Integration**
   - Mock NES PublicationService
   - Verify correct method calls with augmented descriptions
   - Test error handling and status updates

3. **Git Operations**
   - Git add/commit/push handled by GitHub Actions workflow steps, not Python code
   - Verify workflow step configuration
   - Test workflow with manual dispatch

4. **Complete Workflow Integration**
   - Submit → Approve → Process → Verify NES changes
   - Test with all three action types
   - Verify audit trail completeness

**Integration Test Execution**:
```bash
cd services/jawafdehi-api
poetry run pytest tests/nesq/test_integration.py -v
```


## Performance Considerations

### Database Query Optimization

**Indexes**: Create index on `status` for efficient queue processing queries
```python
class Meta:
    indexes = [
        models.Index(fields=['status'], name='queue_status_idx'),
    ]
    ordering = ['created_at']  # FIFO ordering handled in application code
```

**Query Optimization**: Use `select_related()` for foreign key relationships to avoid N+1 queries
```python
approved_items = NESQueueItem.objects.filter(
    status=QueueStatus.APPROVED
).select_related('submitted_by').order_by('created_at')
```

### Batch Processing Considerations

**Processing Batch Size**: Process all approved items in single cron run, but consider adding batch size limit if queue grows large
```python
# Future optimization if needed
MAX_BATCH_SIZE = 100
approved_items = NESQueueItem.objects.filter(
    status=QueueStatus.APPROVED
).order_by('created_at')[:MAX_BATCH_SIZE]
```

**Transaction Management**: Use database transactions for atomic status updates
```python
from django.db import transaction

with transaction.atomic():
    item.status = QueueStatus.COMPLETED
    item.result = result_data
    item.processed_at = timezone.now()
    item.save()
```

### NES Database Performance

**FileDatabase Access**: NES FileDatabase reads/writes are file-based, relatively fast for individual operations
- Average entity creation: ~50-100ms
- Average entity update: ~30-80ms
- Batch operations more efficient than individual calls

**Git Operations**: Commit and push operations are handled by GitHub Actions workflow shell steps
- Single commit for all processed items (not per-item)
- Push only if changes exist (checked via `git diff --cached --quiet`)
- Estimated time: 2-5 seconds for commit + push
- Not part of Python code — decoupled from processor performance

### API Response Time

**Target Response Time**: < 200ms for queue submission endpoint
- Database insert: ~10-20ms
- Serialization: ~5-10ms
- Authentication: ~10-20ms
- Total: ~50-100ms typical

**Optimization Strategies**:
- Defer payload validation to background processing for complex validations
- Use database connection pooling
- Cache user role lookups if needed

### Scalability Considerations

**Current Scale**: Expected load is low (< 100 submissions per day)
- Daily cron processing is sufficient
- No need for real-time processing
- PostgreSQL can handle thousands of queue items easily

**Future Scale**: If submission rate increases significantly:
- Consider moving to Celery for asynchronous processing
- Add rate limiting to API endpoint
- Implement queue item archival/cleanup for old completed items
- Add monitoring and alerting for queue depth


## Security Considerations

### Authentication and Authorization

**Token Authentication**: Use Django REST Framework's TokenAuthentication
- Tokens stored securely in database (hashed)
- Tokens transmitted via Authorization header only
- No token exposure in URLs or logs

**Role-Based Access Control**:
```python
# User roles hierarchy
ADMIN > MODERATOR > CONTRIBUTOR

# Permissions
- Submit queue items: All authenticated users
- Set auto_approve=true: Admin, Moderator only
- Manual approval: Admin, Moderator only (via Django admin)
- View all queue items: Admin, Moderator only
- View own submissions: All authenticated users
```

**Django Admin Security**:
- Admin interface protected by Django's built-in authentication
- Only staff users can access admin interface
- Audit trail maintained (reviewed_by, reviewed_at fields)

### Input Validation and Sanitization

**Payload Validation**: Strict validation at multiple levels using Pydantic
1. DRF serializer validation (action, change_description, auto_approve)
2. Pydantic model validation (payload structure and action-specific business rules)
3. NES Pydantic model validation (entity data integrity during processing)

**SQL Injection Prevention**: Django ORM provides automatic SQL injection protection
- All queries use parameterized statements
- No raw SQL queries in queue system

**XSS Prevention**: 
- All user input stored as-is in database
- Django templates auto-escape output
- API responses are JSON (no HTML rendering)

**Slug Validation**: Strict regex pattern prevents path traversal
```python
slug_pattern = r'^[a-z0-9-]{2,100}$'
# Only lowercase alphanumeric and hyphens allowed
```

### Data Integrity

**Immutable Fields Protection**: Prevent modification of critical fields
```python
IMMUTABLE_FIELDS = ['slug', 'type', 'sub_type', 'id', 'created_at', 'version_summary']
# Validation rejects any update containing these fields
```

**Atomic Operations**: Use database transactions for consistency
```python
with transaction.atomic():
    # All database operations succeed or all fail
    # No partial updates possible
```

**Audit Trail**: Complete history of all changes
- Who submitted (submitted_by)
- Who reviewed (reviewed_by)
- When submitted (created_at)
- When reviewed (reviewed_at)
- When processed (processed_at)
- What changed (change_description, payload)
- Processing outcome (status, result, error_message)

### Git Repository Security

**Push Authentication**: GitHub Actions uses secure token
```yaml
# GitHub Actions secret
NES_DB_PUSH_TOKEN: ${{ secrets.NES_DB_PUSH_TOKEN }}
# Token has write access to nes-db repository only
```

**Commit Signing**: Consider GPG signing for commits (future enhancement)

**Branch Protection**: nes-db repository should have branch protection rules
- Require pull request reviews (optional, depends on workflow)
- Prevent force pushes
- Require status checks to pass

### Secrets Management

**Environment Variables**: Sensitive configuration via environment variables
```python
# Required secrets
NES_DB_PATH: Path to nes-db repository (not sensitive, but configurable)
DATABASE_URL: PostgreSQL connection string (sensitive)
SECRET_KEY: Django secret key (sensitive)
NES_DB_PUSH_TOKEN: GitHub token for pushing (sensitive)
```

**Secret Storage**: 
- Local development: `.env` file (gitignored)
- Production: Environment variables or secret management service
- GitHub Actions: Repository secrets

### Rate Limiting

**API Rate Limiting**: Consider adding rate limiting to prevent abuse
```python
# Future enhancement using django-ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='100/h', method='POST')
def submit_nes_change(request):
    # Limit to 100 submissions per hour per user
```

### Threat Model

**Threat 1: Malicious Entity Data Injection**
- Mitigation: Multi-layer validation (serializer, NES models)
- Impact: Low (validation catches malformed data)

**Threat 2: Unauthorized Queue Item Approval**
- Mitigation: Django admin authentication, role-based permissions
- Impact: Medium (requires compromised admin account)

**Threat 3: Git Repository Compromise**
- Mitigation: Token-based authentication, branch protection
- Impact: High (could corrupt NES database)

**Threat 4: Denial of Service via Queue Flooding**
- Mitigation: Rate limiting, authentication required
- Impact: Medium (could slow processing, but queue persists)

**Threat 5: Information Disclosure**
- Mitigation: Authentication required, role-based access
- Impact: Low (all NES data is public anyway)


## Dependencies

### Python Dependencies (Jawafdehi API)

**Core Framework**:
- `django>=5.2` - Web framework
- `djangorestframework>=3.14` - REST API framework
- `psycopg2-binary>=2.9` - PostgreSQL adapter

**Validation**:
- `pydantic>=2.0` - Payload validation with type safety

**Authentication**:
- `djangorestframework.authtoken` - Token authentication (included in DRF)

**Testing**:
- `pytest>=8.0` - Test framework
- `pytest-django>=4.5` - Django integration for pytest
- `pytest-cov>=4.1` - Coverage reporting
- `hypothesis>=6.92` - Property-based testing
- `factory-boy>=3.3` - Test fixture factories

**Utilities**:
- `python-dotenv>=1.0` - Environment variable management

### External Service Dependencies

**NES (Nepal Entity Service)**:
- Location: `services/nes/`
- Required modules:
  - `nes.services.publication.service.PublicationService`
  - `nes.database.file_database.FileDatabase`
  - `nes.core.models.*` (Entity, Person, Organization, Location, etc.)
- Integration: Async calls via `asyncio.run()`

**nes-db Repository**:
- Repository: `https://github.com/NewNepal-org/NepalEntityService.git`
- Branch: `main`
- Path: `nes-db/v2/` (FileDatabase storage)
- Access: Read/write via NES PublicationService, git operations for commit/push

### Infrastructure Dependencies

**PostgreSQL Database**:
- Version: 14+
- Purpose: Store queue items, user data, Django metadata
- Configuration: Via `DATABASE_URL` environment variable

**GitHub Actions**:
- Purpose: Daily cron job for queue processing
- Required secrets:
  - `NES_DB_PUSH_TOKEN` - GitHub token with write access to nes-db repository
- Workflow file: `.github/workflows/process-nes-queue.yml`

**Git**:
- Version: 2.30+
- Purpose: Commit and push changes to nes-db repository
- Configuration: Git user.name and user.email must be set

### Development Dependencies

**Code Quality**:
- `black>=24.0` - Code formatter
- `isort>=5.13` - Import sorter
- `flake8>=7.0` - Linter

**Type Checking** (optional):
- `mypy>=1.8` - Static type checker
- `django-stubs>=4.2` - Django type stubs

### Environment Variables

**Required**:
```bash
# Django settings
SECRET_KEY=<django-secret-key>
DEBUG=False
ALLOWED_HOSTS=jawafdehi.org,localhost

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# NES integration (GitHub Actions only - REQUIRED, no default)
NES_DB_PATH=/path/to/nes-db/v2

# GitHub Actions only
NES_DB_PUSH_TOKEN=<github-token>
```

**Optional**:
```bash
# Logging
LOG_LEVEL=INFO

# Rate limiting (future)
RATELIMIT_ENABLE=True
```

### Service Integration Points

**Jawafdehi API → NES**:
- Direction: Jawafdehi calls NES
- Protocol: Direct Python module import
- Data flow: Queue processor → PublicationService → FileDatabase
- Error handling: Exceptions caught and stored in queue item

**Jawafdehi API → nes-db Repository**:
- Direction: Jawafdehi writes to nes-db filesystem via NES PublicationService
- Protocol: NES FileDatabase writes files to disk
- Data flow: PublicationService writes files → GitHub Actions git steps commit & push
- Error handling: File write errors caught in processor; git errors handled by workflow

**GitHub Actions → Jawafdehi API**:
- Direction: GitHub Actions runs management command
- Protocol: Django management command
- Data flow: Cron trigger → process_queue command → Queue processor
- Error handling: Workflow fails if command exits with non-zero status

### Deployment Dependencies

**Docker** (for containerized deployment):
- Base image: `python:3.12-slim`
- Exposed port: 8000
- Volume mounts: nes-db repository

**Cloud Run** (GCP deployment):
- Runtime: Python 3.12
- Memory: 512MB minimum
- CPU: 1 vCPU
- Concurrency: 80 requests

