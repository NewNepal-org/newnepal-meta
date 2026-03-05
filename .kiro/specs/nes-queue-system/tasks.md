# Implementation Tasks: NES Queue System (NESQ)

## Task Overview

This document outlines the implementation tasks for the NES Queue System feature. Tasks are organized by component and should be completed in the order listed to maintain dependencies.

---

## 1. Project Setup and Configuration

### 1.1 Create Django App Structure
- [x] Create `nesq` Django app in jawafdehi-api
- [x] Add `nesq` to INSTALLED_APPS in settings.py
- [x] Create app directory structure (models, views, serializers, admin, etc.)
- [x] Create `__init__.py` files for all modules

### 1.2 Configure Dependencies
- [x] Add `pydantic>=2.0` to pyproject.toml
- [x] Add `rest_framework.authtoken` to INSTALLED_APPS

### 1.3 Configure Environment Variables
- [x] Configure NES_DB_PATH to be required in GitHub Actions workflow (no default value)
- [x] Document that NES_DB_PATH is only needed for GitHub Actions in deployment docs

---

## 2. Data Models and Database

### 2.1 Create Enums
- [x] Create `QueueAction` TextChoices enum with ADD_NAME only (MVP)
- [x] Add comments indicating CREATE_ENTITY and UPDATE_ENTITY are future enhancements
- [x] Create `QueueStatus` TextChoices enum (PENDING, APPROVED, REJECTED, COMPLETED, FAILED)
- [x] Add docstrings explaining each enum value

### 2.2 Create NESQueueItem Model
- [x] Define model with all required fields (id, action, payload, status, etc.)
- [x] Add ForeignKey relationships (submitted_by, reviewed_by)
- [x] Add timestamp fields (created_at, updated_at, reviewed_at, processed_at)
- [x] Add JSONField for payload and result
- [x] Add TextField for change_description and error_message
- [x] Set default status to PENDING
- [x] Add model Meta class with ordering and indexes

### 2.3 Create Database Indexes
- [x] Add index on status field only
- [x] Add ordering = ['created_at'] in Meta class for FIFO processing

### 2.4 Create and Run Migrations
- [x] Generate initial migration: `poetry run python manage.py makemigrations nesq`
- [x] Review migration file for correctness
- [x] Run migration: `poetry run python manage.py migrate`

---

## 3. Pydantic Payload Validators

### 3.1 Create Base Validator Module
- [x] Create `nesq/validators.py` file
- [x] Import NES validator (validate_entity_id only)
- [x] Import Pydantic v2 classes (BaseModel, Field, field_validator)

### 3.2 Create AddNamePayload Model (MVP - Only Supported Action)
- [x] Define entity_id field
- [x] Define name dict field
- [x] Define is_misspelling boolean field with default=False
- [x] Add @field_validator for entity_id using validate_entity_id()
- [x] Add @field_validator for name (kind, en/ne validation)
- [x] Add docstring explaining this is MVP-only action
- [x] Add comment that CREATE_ENTITY and UPDATE_ENTITY are future enhancements

---

## 4. Django REST Framework Serializers

### 4.1 Create Request Serializer
- [x] Create `nesq/serializers.py` file
- [x] Create NESQueueSubmitSerializer with fields: action, payload, change_description, auto_approve
- [x] Add validation for action field (must be valid QueueAction)
- [x] Add validation for payload field (must be dict)
- [x] Add validation for change_description (non-empty)
- [x] Add validation for auto_approve (boolean, optional)

### 4.2 Create Response Serializer
- [x] Create NESQueueItemSerializer for API responses
- [x] Include fields: id, action, status, submitted_by, reviewed_by, reviewed_at, processed_at, created_at
- [x] Use SerializerMethodField for submitted_by username
- [x] Use SerializerMethodField for reviewed_by username
- [x] Add docstring explaining serializer usage

---

## 5. API Views and Endpoints

### 5.1 Create Submit Endpoint
- [x] Create `nesq/api_views.py` file
- [x] Create SubmitNESChangeView (APIView)
- [x] Add TokenAuthentication to authentication_classes
- [x] Add IsAuthenticated to permission_classes
- [x] Verify compatibility with existing auth system in services/jawafdehi-api/cases/rules/predicates.py
- [x] Implement POST method handler

### 5.2 Implement POST Handler Logic
- [x] Validate request data using NESQueueSubmitSerializer
- [x] Extract action and payload from validated data
- [x] Reject if action is not ADD_NAME with HTTP 400 error
- [x] Validate payload using AddNamePayload Pydantic model
- [x] Check auto_approve flag and user role
- [x] Return 403 if contributor tries auto_approve=true
- [x] Determine initial status (PENDING or APPROVED)
- [x] Create NESQueueItem with appropriate fields
- [x] Return serialized queue item with 201 status

### 5.3 Create URL Configuration
- [x] Create `nesq/urls.py` file
- [x] Add route for POST /api/submit_nes_change
- [x] Include nesq URLs in main config/urls.py

### 5.4 Create List Endpoint (Optional)
- [x] Create ListMySubmissionsView for viewing user's submissions
- [x] Filter by submitted_by = request.user
- [x] Order by created_at descending
- [x] Add pagination support
- [x] Add route for GET /api/my_nes_submissions

---

## 6. Django Admin Interface

### 6.1 Create Admin Configuration
- [x] Create `nesq/admin.py` file
- [x] Register NESQueueItem model
- [x] Configure list_display (id, action, status, submitted_by, reviewed_by, created_at)
- [x] Configure list_filter (status, action, created_at)
- [x] Configure search_fields (change_description, submitted_by__username)
- [x] Configure readonly_fields for completed/failed items

### 6.2 Create Bulk Actions
- [x] Create bulk_approve admin action
- [x] Filter queryset to only PENDING items
- [x] Set status=APPROVED, reviewed_by=request.user, reviewed_at=now()
- [x] Display success message with count
- [x] Create bulk_reject admin action
- [x] Filter queryset to only PENDING items
- [x] Set status=REJECTED, reviewed_by=request.user, reviewed_at=now()
- [x] Display success message with count

### 6.3 Customize Admin Display
- [x] Add custom display methods for formatted fields
- [x] Add color coding for status field (green=COMPLETED, red=FAILED, etc.)
- [x] Add inline display of payload (formatted JSON)
- [x] Add inline display of error_message for failed items

---

## 7. Queue Processor

### 7.1 Create Processor Module
- [x] Create `nesq/processor.py` file
- [x] Create QueueProcessor class
- [x] Add __init__ method accepting nes_db_path parameter
- [x] Import NES PublicationService and FileDatabase
- [x] Import asyncio for async/await support

### 7.2 Implement Process Approved Items Method
- [x] Create async process_approved_items() method
- [x] Initialize FileDatabase with nes_db_path
- [x] Initialize PublicationService with database
- [x] Query NESQueueItem.objects.filter(status=APPROVED).order_by('created_at')
- [x] Use select_related('submitted_by') to avoid N+1 queries
- [x] Initialize counters (processed, completed, failed)
- [x] Return processing result dict

### 7.3 Implement Process Single Item Method
- [x] Create async process_item() method
- [x] Augment change_description with " (submitted by {username})"
- [x] Generate author_id in format "jawafdehi:{username}"
- [x] Assert item.action is ADD_NAME (skip unsupported actions)
- [x] Fetch existing entity using publication_service.get_entity()
- [x] Raise EntityNotFoundError if entity doesn't exist
- [x] Append name to entity.names or entity.misspelled_names based on is_misspelling flag
- [x] Call publication_service.update_entity() with augmented description and author_id
- [x] Wrap in try/except to catch processing errors
- [x] Update item status to COMPLETED on success
- [x] Update item status to FAILED on error with error_message
- [x] Set processed_at timestamp
- [x] Save item to database

**Note**: Git operations (add, commit, push) are handled by GitHub Actions workflow steps, NOT by the Python processor. See Task 9.

---

## 8. Management Command

### 8.1 Create Management Command Structure
- [x] Create `nesq/management/` directory
- [x] Create `nesq/management/__init__.py`
- [x] Create `nesq/management/commands/` directory
- [x] Create `nesq/management/commands/__init__.py`

### 8.2 Implement Process Queue Command
- [x] Create `nesq/management/commands/process_queue.py`
- [x] Create Command class inheriting from BaseCommand
- [x] Add help text describing command purpose
- [x] Implement handle() method
- [x] Read NES_DB_PATH from settings
- [x] Verify nes-db repository exists and is accessible
- [x] Create QueueProcessor instance
- [x] Call asyncio.run(processor.process_approved_items())
- [x] Log processing summary to stdout
- [x] Exit with status 0 on success, non-zero on critical error

### 8.3 Add Command Options
- [x] Add --verbose option for detailed logging
- [x] Document options in help text

---

## 9. GitHub Actions Workflow

### 9.1 Create Workflow File
- [x] Create `.github/workflows/process-nes-queue.yml` in jawafdehi-api repo
- [x] Configure cron schedule: '0 0 * * *' (midnight UTC daily)
- [x] Add manual workflow_dispatch trigger for testing

### 9.2 Configure Workflow Steps
- [x] Add checkout action for jawafdehi-api repo
- [x] Add checkout action for nes-db repo to specific path
- [x] Set up Python 3.12 environment
- [x] Install Poetry
- [x] Run poetry install to install dependencies
- [x] Configure git user.name and user.email for nes-db repo
- [x] Run process_queue management command
- [x] Handle command failures with appropriate exit codes

### 9.3 Add Git Operations Steps (post-processing)
- [x] Run `git add .` in nes-db directory after process_queue completes
- [x] Check for changes using `git diff --cached --quiet` (skip commit if none)
- [x] Create commit with message "Process NESQ items: X completed, Y failed"
- [x] Run `git push` to push changes to nes-db remote
- [x] Handle git push failures with appropriate error logging

### 9.4 Configure Secrets
- [x] Add NES_DB_PUSH_TOKEN to repository secrets
- [x] Add DATABASE_URL to repository secrets
- [x] Add SECRET_KEY to repository secrets
- [x] Document required secrets in README

---

## 10. Unit Tests

### 10.1 Test Models
- [x] Create `tests/nesq/test_models.py`
- [x] Test NESQueueItem creation with defaults
- [x] Test NESQueueItem creation with all fields
- [x] Test status choices are valid
- [x] Test action choices are valid
- [x] Test ordering by created_at
- [x] Test submitted_by foreign key constraint
- [x] Test reviewed_by nullable foreign key
- [x] Test payload JSONField accepts valid JSON

### 10.2 Test Pydantic Validators
- [x] Create `tests/nesq/test_validators.py`
- [x] Test AddNamePayload with valid English name
- [x] Test AddNamePayload with valid Nepali name
- [x] Test AddNamePayload with bilingual name
- [x] Test AddNamePayload with missing both languages (should fail)
- [x] Test AddNamePayload with invalid entity_id (should fail)
- [x] Test AddNamePayload with invalid name.kind (should fail)
- [x] Test AddNamePayload with is_misspelling=true
- [x] Test AddNamePayload with is_misspelling=false (default)

### 10.3 Test Serializers
- [x] Create `tests/nesq/test_serializers.py`
- [x] Test NESQueueSubmitSerializer with valid data
- [x] Test NESQueueSubmitSerializer with missing action (should fail)
- [x] Test NESQueueSubmitSerializer with invalid action (should fail)
- [x] Test NESQueueSubmitSerializer with missing payload (should fail)
- [x] Test NESQueueItemSerializer serialization
- [x] Test username extraction in serializers

### 10.4 Test API Views
- [x] Create `tests/nesq/test_api_views.py`
- [x] Test submit endpoint without authentication (401)
- [x] Test submit endpoint with invalid token (401)
- [x] Test submit endpoint with valid ADD_NAME payload (201)
- [x] Test submit endpoint with CREATE_ENTITY action (400 - unsupported)
- [x] Test submit endpoint with UPDATE_ENTITY action (400 - unsupported)
- [x] Test auto_approve=true as admin (status=APPROVED)
- [x] Test auto_approve=true as moderator (status=APPROVED)
- [x] Test auto_approve=true as contributor (403)
- [x] Test auto_approve=false creates PENDING item
- [x] Test invalid payload returns 400 with Pydantic errors
- [x] Test that no author_id field is required in payload

### 10.5 Test Queue Processor
- [x] Create `tests/nesq/test_processor.py`
- [x] Mock NES PublicationService for testing
- [x] Test process_approved_items with ADD_NAME (success)
- [x] Test process_approved_items with ADD_NAME is_misspelling=true
- [x] Test processor generates correct author_id format "jawafdehi:{username}"
- [x] Test processor augments change_description correctly
- [x] Test processor skips PENDING items
- [x] Test processor skips REJECTED items
- [x] Test processor skips COMPLETED items
- [x] Test processor skips FAILED items
- [x] Test processor handles entity not found error
- [x] Test processor handles NES validation error
- [x] Test processor stores result on success
- [x] Test processor sets processed_at timestamp
- [x] Test processor maintains chronological order (FIFO)
- [x] Test processor continues after individual failure

### 10.6 Test Admin Interface
- [x] Create `tests/nesq/test_admin.py`
- [x] Test admin list view displays queue items
- [x] Test bulk_approve action on PENDING items
- [x] Test bulk_reject action on PENDING items
- [x] Test bulk_approve sets reviewed_by and reviewed_at
- [x] Test bulk actions skip non-PENDING items

---

## 11. Integration Tests

### 11.1 Test End-to-End Workflow
- [x] Create `tests/nesq/test_integration.py`
- [x] Test complete ADD_NAME workflow: submit → approve → process → verify
- [x] Test ADD_NAME workflow with real NES integration
- [x] Test ADD_NAME with is_misspelling=true workflow
- [x] Test auto_approve workflow for admin
- [x] Test manual approval workflow in admin
- [x] Test error handling in complete workflow
- [x] Test that unsupported actions are rejected

**Note**: Git operations (add, commit, push) are tested as part of the GitHub Actions workflow (Task 9), not as Python unit/integration tests.

---

## 12. Property-Based Tests

### 12.1 Create Property Tests
- [ ] Create `tests/nesq/test_properties.py`
- [ ] Test status transition invariants using hypothesis
- [ ] Test payload validation consistency using hypothesis
- [ ] Test processing order preservation using hypothesis
- [ ] Test change description augmentation format using hypothesis

---

## 13. Documentation

### 13.1 API Documentation (services/jawafdehi-api/docs/features/nesq/)
- [ ] Create services/jawafdehi-api/docs/features/nesq/ directory
- [ ] Document POST /api/submit_nes_change endpoint
- [ ] Document ADD_NAME request/response schemas
- [ ] Document authentication requirements
- [ ] Document error responses
- [ ] Add example ADD_NAME requests (regular name and misspelling)
- [ ] Document that CREATE_ENTITY and UPDATE_ENTITY are not yet supported
- [ ] Document that author_id is automatically derived from authenticated user

### 13.2 Admin Documentation (services/jawafdehi-api/docs/features/nesq/)
- [ ] Document admin interface usage
- [ ] Document bulk approval workflow
- [ ] Document queue item lifecycle
- [ ] Add screenshots of admin interface

### 13.3 Deployment Documentation (services/jawafdehi-api/docs/features/nesq/)
- [ ] Document environment variables
- [ ] Document GitHub Actions setup
- [ ] Document nes-db repository requirements
- [ ] Document monitoring and alerting

### 13.4 Developer Documentation (services/jawafdehi-api/docs/features/nesq/)
- [ ] Document code structure and organization
- [ ] Document testing strategy
- [ ] Document contribution guidelines
- [ ] Add inline code comments and docstrings

### 13.5 NES Contributor Documentation (services/nes/docs/contributors/)
- [ ] Create contributor guide for adding names via NESQ API
- [ ] Document requirement for Jawafdehi user account
- [ ] Provide step-by-step instructions for submitting ADD_NAME requests
- [ ] Include authentication setup instructions
- [ ] Add examples with curl/httpie commands
- [ ] Update documentation.html in services/nes/docs/templates to replace data migration guide with NESQ guide

---

## 14. Deployment and Verification

### 14.1 Staging Deployment
- [ ] Deploy to staging environment
- [ ] Verify database migrations applied
- [ ] Verify API endpoints accessible
- [ ] Verify admin interface accessible
- [ ] Test queue submission in staging
- [ ] Test queue processing in staging

### 14.2 Production Deployment
- [ ] Deploy to production environment
- [ ] Run database migrations
- [ ] Verify environment variables configured
- [ ] Verify GitHub Actions workflow configured
- [ ] Monitor first production queue processing run
- [ ] Verify nes-db commits appear correctly

### 14.3 Post-Deployment Verification
- [ ] Submit test queue items via API
- [ ] Approve test items in admin
- [ ] Wait for cron job to process items
- [ ] Verify items marked as COMPLETED
- [ ] Verify changes appear in nes-db repository
- [ ] Verify audit trail is complete

---

## Task Dependencies

### Critical Path
1. Project Setup (1.x) → Data Models (2.x)
2. Data Models (2.x) → Pydantic Validators (3.x)
3. Pydantic Validators (3.x) → API Views (5.x)
4. Data Models (2.x) → Queue Processor (7.x)
5. Queue Processor (7.x) → Management Command (8.x)
6. Management Command (8.x) → GitHub Actions (9.x) (includes git add/commit/push)

### Parallel Work Streams
- DRF Serializers (4.x) can be done in parallel with Pydantic Validators (3.x)
- Django Admin (6.x) can be done in parallel with API Views (5.x)
- Unit Tests (10.x) can be written alongside implementation
- Documentation (13.x) can be written throughout development

---

## Estimated Effort

| Task Category | Estimated Hours |
|---------------|-----------------|
| 1. Project Setup | 2 hours |
| 2. Data Models | 3 hours |
| 3. Pydantic Validators | 3 hours |
| 4. DRF Serializers | 3 hours |
| 5. API Views | 5 hours |
| 6. Django Admin | 4 hours |
| 7. Queue Processor | 4 hours |
| 8. Management Command | 3 hours |
| 9. GitHub Actions | 5 hours |
| 10. Unit Tests | 10 hours |
| 11. Integration Tests | 4 hours |
| 12. Property Tests | 3 hours |
| 13. Documentation | 5 hours |
| 14. Deployment | 4 hours |
| **Total** | **58 hours** |

**Note**: Reduced from 78 hours due to MVP scope focusing on ADD_NAME only. CREATE_ENTITY and UPDATE_ENTITY will be added in future iterations.

---

## Success Criteria

Implementation is complete when:
- ✅ All tasks marked as complete
- ✅ All tests passing with ≥90% coverage
- ✅ ADD_NAME API endpoint functional and documented
- ✅ Django admin interface functional
- ✅ Queue processing runs successfully via cron for ADD_NAME actions
- ✅ Changes committed to nes-db repository via GitHub Actions git steps
- ✅ System deployed to production
- ✅ Post-deployment verification complete
- ✅ Unsupported actions (CREATE_ENTITY, UPDATE_ENTITY) properly rejected with clear error messages

**Future Enhancements** (not in MVP):
- CREATE_ENTITY action support
- UPDATE_ENTITY action support
