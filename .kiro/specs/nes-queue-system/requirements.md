# Requirements Document: NES Queue System (NESQ)

## Overview

The NES Queue System (NESQ) is a queue-based API feature that enables authenticated contributors to submit requests to add names (including misspellings) to existing entities in the Nepal Entity Service (NES) database through a REST API, with admin/moderator approval workflows and automated daily processing.

**Initial Scope**: This MVP focuses exclusively on the ADD_NAME action. CREATE_ENTITY and UPDATE_ENTITY actions are planned for future releases.

## Problem Statement

Currently, updating the NES database requires creating Django migrations in the Jawafdehi API codebase, which is:
- **Developer-centric**: Requires technical knowledge of Django and Python
- **Slow**: Requires code review, deployment, and migration execution
- **Not scalable**: Cannot handle community contributions efficiently
- **Lacks audit trail**: No built-in tracking of who requested changes and why

## Goals

### Primary Goals
1. Enable authenticated users to submit requests to add names to existing NES entities via REST API
2. Provide admin/moderator approval workflow for quality control
3. Automate processing of approved requests through daily cron job
4. Maintain complete audit trail of all submissions and approvals
5. Integrate seamlessly with existing NES PublicationService

### Secondary Goals
1. Support misspelling flag to distinguish between valid names and common misspellings
2. Provide clear error messages for validation failures
3. Enable bulk approval/rejection in Django admin interface
4. Ensure chronological processing order for consistency

## User Stories

### US-1: Submit Add Name Request (Contributor)
**As a** contributor  
**I want to** submit a request to add a name or misspelling to an entity  
**So that** entities can be found by alternative names

**Acceptance Criteria**:
- AC-1.1: API endpoint accepts entity_id, name object, and is_misspelling flag
- AC-1.2: System validates entity_id using NES validator
- AC-1.3: System validates name has at least one of 'en' or 'ne' field
- AC-1.4: System validates name.kind is valid (PRIMARY, ALIAS, ALTERNATE, BIRTH_NAME)
- AC-1.5: System creates queue item with status=PENDING
- AC-1.6: System defaults is_misspelling to false if not provided
- AC-1.7: System uses authenticated user's username as author (no author_id field required)
- AC-1.8: API returns queue item ID and status in response

### US-2: Auto-Approve Own Submissions (Admin/Moderator)
**As an** admin or moderator  
**I want to** auto-approve my submissions by setting auto_approve flag  
**So that** I can bypass manual review for trusted changes

**Acceptance Criteria**:
- AC-2.1: API accepts optional auto_approve boolean flag
- AC-2.2: System allows auto_approve=true only for Admin/Moderator roles
- AC-2.3: System creates queue item with status=APPROVED when auto_approve=true
- AC-2.4: System sets reviewed_by and reviewed_at fields to submitter and current time
- AC-2.5: System returns 403 Forbidden if contributor tries to set auto_approve=true
- AC-2.6: System defaults auto_approve to false if not provided

### US-3: Review Pending Submissions (Admin/Moderator)
**As an** admin or moderator  
**I want to** review and approve/reject pending queue items in Django admin  
**So that** I can ensure quality control before processing

**Acceptance Criteria**:
- AC-3.1: Django admin displays list of queue items with filters (status, action, date)
- AC-3.2: Admin can search by change description or submitter username
- AC-3.3: Admin can view full payload and change description for each item
- AC-3.4: Admin can bulk approve multiple PENDING items
- AC-3.5: Admin can bulk reject multiple PENDING items
- AC-3.6: System records reviewer username and timestamp on approval/rejection
- AC-3.7: System prevents modification of COMPLETED or FAILED items

### US-4: Process Approved Queue Items (System)
**As the** system  
**I want to** automatically process approved queue items daily  
**So that** changes are applied to NES database without manual intervention

**Acceptance Criteria**:
- AC-4.1: GitHub Actions cron job runs daily at midnight UTC
- AC-4.2: System queries all items with status=APPROVED in chronological order
- AC-4.3: System processes ADD_NAME items by calling NES PublicationService
- AC-4.4: System augments change description with submitter username
- AC-4.5: System uses "jawafdehi:{username}" format as author_id for NES
- AC-4.6: System updates item status to COMPLETED on success
- AC-4.7: System updates item status to FAILED on error with error message
- AC-4.8: GitHub Actions workflow commits and pushes all changes to nes-db repository in single commit (git operations are workflow steps, not Python code)
- AC-4.9: Workflow skips commit/push if no changes exist in nes-db

### US-5: Handle Processing Errors (System)
**As the** system  
**I want to** gracefully handle errors during queue processing  
**So that** failures are logged and don't block other items

**Acceptance Criteria**:
- AC-5.1: System catches exceptions during item processing
- AC-5.2: System stores error message in item.error_message field
- AC-5.3: System sets item status to FAILED
- AC-5.4: System continues processing remaining items after failure
- AC-5.5: System logs processing summary (processed, completed, failed counts)
- AC-5.6: System handles entity not found errors for ADD_NAME
- AC-5.7: System handles NES validation errors with detailed messages

### US-6: View Submission History (Contributor)
**As a** contributor  
**I want to** view the status of my submitted requests  
**So that** I can track whether they've been approved and processed

**Acceptance Criteria**:
- AC-6.1: API endpoint returns list of queue items submitted by authenticated user
- AC-6.2: Response includes id, action, status, change_description, created_at
- AC-6.3: Response includes reviewed_by and reviewed_at for approved/rejected items
- AC-6.4: Response includes processed_at for completed/failed items
- AC-6.5: Response includes error_message for failed items
- AC-6.6: System orders results by created_at descending (newest first)

### US-7: Validate Payload Structure (System)
**As the** system  
**I want to** validate payload structure using action-specific Pydantic models  
**So that** invalid data is rejected before creating queue items

**Acceptance Criteria**:
- AC-7.1: System uses AddNamePayload Pydantic model for ADD_NAME action
- AC-7.2: System validates entity_id format using NES validate_entity_id() function
- AC-7.3: System returns detailed Pydantic validation errors in API response
- AC-7.4: System validates name has at least one of 'en' or 'ne' field
- AC-7.5: System validates name.kind is valid (PRIMARY, ALIAS, ALTERNATE, BIRTH_NAME)
- AC-7.6: System rejects unsupported actions (CREATE_ENTITY, UPDATE_ENTITY) with clear error message

## Functional Requirements

### FR-1: API Authentication
- FR-1.1: System MUST use Django REST Framework TokenAuthentication
- FR-1.2: System MUST require valid authentication token for all API requests
- FR-1.3: System MUST return 401 Unauthorized for missing or invalid tokens
- FR-1.4: System MUST identify user role (Admin, Moderator, Contributor) from token

### FR-2: Queue Item Creation
- FR-2.1: System MUST create NESQueueItem with all required fields
- FR-2.2: System MUST set status=PENDING for contributor submissions
- FR-2.3: System MUST set status=APPROVED for admin/moderator auto-approved submissions
- FR-2.4: System MUST store submitted_by as authenticated user
- FR-2.5: System MUST set created_at to current timestamp
- FR-2.6: System MUST validate payload using action-specific Pydantic model

### FR-3: Payload Validation
- FR-3.1: System MUST validate payload structure using Pydantic v2 models
- FR-3.2: System MUST use @field_validator decorator for custom validation
- FR-3.3: System MUST call validate_entity_id() for entity_id fields
- FR-3.4: System MUST reject unsupported actions with clear error message
- FR-3.5: System MUST validate name objects have 'en' or 'ne' field
- FR-3.6: System MUST validate name.kind is valid (PRIMARY, ALIAS, ALTERNATE, BIRTH_NAME)
- FR-3.7: System MUST use authenticated user's username as author (format: "jawafdehi:{username}")

### FR-4: Admin Approval Workflow
- FR-4.1: System MUST provide Django admin interface for queue management
- FR-4.2: System MUST support bulk approve action for PENDING items
- FR-4.3: System MUST support bulk reject action for PENDING items
- FR-4.4: System MUST record reviewed_by and reviewed_at on status change
- FR-4.5: System MUST prevent modification of COMPLETED/FAILED items
- FR-4.6: System MUST display filters for status, action, and created_at

### FR-5: Queue Processing
- FR-5.1: System MUST process items in chronological order (created_at ASC)
- FR-5.2: System MUST call PublicationService.update_entity() for ADD_NAME
- FR-5.3: System MUST augment change_description with " (submitted by {username})"
- FR-5.4: System MUST use "jawafdehi:{username}" format as author_id for NES
- FR-5.5: System MUST update status to COMPLETED on success
- FR-5.6: System MUST update status to FAILED on error
- FR-5.7: System MUST set processed_at timestamp after processing
- FR-5.8: System MUST skip unsupported actions (CREATE_ENTITY, UPDATE_ENTITY)

### FR-6: Git Operations (GitHub Actions Workflow Steps)
- FR-6.1: GitHub Actions workflow MUST commit all changes in single commit after processing
- FR-6.2: GitHub Actions workflow MUST use commit message format: "Process NESQ items: X completed, Y failed"
- FR-6.3: GitHub Actions workflow MUST push commit to nes-db repository remote
- FR-6.4: GitHub Actions workflow MUST skip commit/push if no changes exist
- FR-6.5: GitHub Actions workflow MUST surface git push failures visibly in workflow logs

**Note**: Git operations are handled as shell steps in the GitHub Actions workflow, not as Python code in the QueueProcessor.

### FR-7: Error Handling
- FR-7.1: System MUST catch and log all processing exceptions
- FR-7.2: System MUST store error message in item.error_message field
- FR-7.3: System MUST continue processing after individual item failures
- FR-7.4: System MUST return detailed validation errors in API responses
- FR-7.5: System MUST handle EntityNotFoundError for ADD_NAME
- FR-7.6: System MUST reject unsupported actions with HTTP 400 error

## Non-Functional Requirements

### NFR-1: Performance
- NFR-1.1: API response time MUST be < 200ms for queue submission
- NFR-1.2: Queue processing MUST handle 100+ items per batch
- NFR-1.3: Database queries MUST use indexes for status and created_at
- NFR-1.4: System MUST use select_related() to avoid N+1 queries

### NFR-2: Security
- NFR-2.1: System MUST validate all user input using Pydantic models
- NFR-2.2: System MUST use parameterized SQL queries (Django ORM)
- NFR-2.3: System MUST prevent SQL injection attacks
- NFR-2.4: System MUST prevent XSS attacks in admin interface
- NFR-2.5: System MUST use role-based access control for auto_approve
- NFR-2.6: System MUST store GitHub token securely in environment variables

### NFR-3: Reliability
- NFR-3.1: System MUST use database transactions for atomic operations
- NFR-3.2: System MUST maintain data integrity during failures
- NFR-3.3: System MUST not create partial updates in NES database
- NFR-3.4: GitHub Actions workflow MUST surface git operation failures visibly for manual intervention
- NFR-3.5: System MUST log all errors for debugging

### NFR-4: Maintainability
- NFR-4.1: Code MUST follow Django and DRF best practices
- NFR-4.2: Code MUST use Poetry for dependency management
- NFR-4.3: Code MUST have minimum 90% test coverage
- NFR-4.4: Code MUST use black and isort for formatting
- NFR-4.5: Code MUST include docstrings for all public functions

### NFR-5: Scalability
- NFR-5.1: System MUST support 1000+ queue items in database
- NFR-5.2: System MUST handle 100+ submissions per day
- NFR-5.3: System MUST process items efficiently in single cron run
- NFR-5.4: System MUST use database indexes for query optimization

### NFR-6: Auditability
- NFR-6.1: System MUST record submitted_by for all queue items
- NFR-6.2: System MUST record reviewed_by for approved/rejected items
- NFR-6.3: System MUST record timestamps for created_at, reviewed_at, processed_at
- NFR-6.4: System MUST store complete payload for audit trail
- NFR-6.5: System MUST store processing results and error messages

## Data Requirements

### DR-1: NESQueueItem Model
- DR-1.1: Model MUST have id (AutoField, primary key)
- DR-1.2: Model MUST have action (CharField, QueueAction choices)
- DR-1.3: Model MUST have payload (JSONField, not null)
- DR-1.4: Model MUST have status (CharField, QueueStatus choices, default=PENDING)
- DR-1.5: Model MUST have submitted_by (ForeignKey to User, PROTECT)
- DR-1.6: Model MUST have reviewed_by (ForeignKey to User, SET_NULL, nullable)
- DR-1.7: Model MUST have reviewed_at (DateTimeField, nullable)
- DR-1.8: Model MUST have processed_at (DateTimeField, nullable)
- DR-1.9: Model MUST have change_description (TextField, not null)
- DR-1.10: Model MUST have error_message (TextField, blank)
- DR-1.11: Model MUST have result (JSONField, nullable)
- DR-1.12: Model MUST have created_at (DateTimeField, auto_now_add)
- DR-1.13: Model MUST have updated_at (DateTimeField, auto_now)

### DR-2: Database Indexes
- DR-2.1: System MUST create index on status field
- DR-2.2: System MUST handle FIFO ordering via created_at in application code

### DR-3: Enums
- DR-3.1: QueueAction MUST have value: ADD_NAME (MVP - only supported action)
- DR-3.2: QueueStatus MUST have values: PENDING, APPROVED, REJECTED, COMPLETED, FAILED

**Note**: CREATE_ENTITY and UPDATE_ENTITY actions are planned for future releases.

## Integration Requirements

### IR-1: NES PublicationService Integration
- IR-1.1: System MUST import PublicationService from nes.services.publication.service
- IR-1.2: System MUST import FileDatabase from nes.database.file_database
- IR-1.3: System MUST call PublicationService methods asynchronously
- IR-1.4: System MUST pass author_id in format "jawafdehi:{username}" to PublicationService
- IR-1.5: System MUST pass augmented change_description to PublicationService

### IR-2: NES Validator Integration
- IR-2.1: System MUST import validate_entity_id from nes.core.identifiers.validators
- IR-2.2: System MUST call validator in Pydantic @field_validator methods
- IR-2.3: System MUST propagate validation errors to API response

### IR-3: nes-db Repository Integration
- IR-3.1: System MUST read NES_DB_PATH from environment variable (GitHub Actions only, REQUIRED)
- IR-3.2: System MUST verify nes-db repository is cloned and accessible
- IR-3.3: GitHub Actions workflow MUST perform git add, commit, push as shell steps (not Python code)
- IR-3.4: GitHub Actions workflow MUST use GitHub token for push authentication

### IR-4: GitHub Actions Integration
- IR-4.1: System MUST provide management command for queue processing
- IR-4.2: System MUST support execution via poetry run python manage.py process_queue
- IR-4.3: System MUST exit with non-zero status on critical errors
- IR-4.4: System MUST log processing summary to stdout

## Constraints

### Technical Constraints
- TC-1: System MUST use Django 5.2+ framework
- TC-2: System MUST use Django REST Framework 3.14+
- TC-3: System MUST use Pydantic 2.0+ for validation
- TC-4: System MUST use PostgreSQL 14+ database
- TC-5: System MUST use Python 3.12+
- TC-6: System MUST use Poetry for dependency management

### Business Constraints
- BC-1: System MUST maintain backward compatibility with existing NES API
- BC-2: System MUST not modify NES database structure
- BC-3: System MUST use existing NES PublicationService without modifications
- BC-4: System MUST process queue items daily (not real-time)
- BC-5: System MUST support bilingual content (English/Nepali)

### Operational Constraints
- OC-1: System MUST run on Google Cloud Platform
- OC-2: System MUST use GitHub Actions for cron scheduling
- OC-3: System MUST store secrets in environment variables
- OC-4: System MUST log to stdout for Cloud Run compatibility
- OC-5: System MUST handle network failures gracefully

## Acceptance Criteria Summary

The NES Queue System will be considered complete when:

1. ✅ All 7 user stories are implemented with acceptance criteria met
2. ✅ All functional requirements (FR-1 through FR-7) are satisfied
3. ✅ All non-functional requirements (NFR-1 through NFR-6) are met
4. ✅ Test coverage is minimum 90% for nesq app
5. ✅ Property-based tests validate critical invariants
6. ✅ Integration tests verify end-to-end workflows for ADD_NAME
7. ✅ Django admin interface is functional and user-friendly
8. ✅ API documentation is complete and accurate
9. ✅ GitHub Actions workflow is configured and tested
10. ✅ System successfully processes ADD_NAME queue items in production

## Out of Scope

The following items are explicitly out of scope for this feature:

1. CREATE_ENTITY action (planned for future release)
2. UPDATE_ENTITY action (planned for future release)
3. Real-time queue processing (daily batch processing only)
4. Email notifications for queue status changes
5. Web UI for queue submission (API only)
6. Queue item editing after submission
7. Rollback functionality for completed items
8. Rate limiting (future enhancement)
9. Queue item archival/cleanup (future enhancement)
10. Multi-language support beyond English/Nepali
11. Advanced search and filtering in API
12. Webhook notifications for status changes

## Dependencies

### External Dependencies
- Django REST Framework for API implementation
- Pydantic for payload validation
- NES PublicationService for entity operations
- nes-db repository for entity storage
- GitHub Actions for cron scheduling
- PostgreSQL for queue storage

### Internal Dependencies
- User authentication system (existing)
- Django admin interface (existing)
- NES entity validators (existing)
- Git (used by GitHub Actions workflow steps, not Python code)

## Risks and Mitigations

### Risk 1: NES PublicationService API Changes
**Impact**: High  
**Probability**: Low  
**Mitigation**: Use stable NES API, add integration tests, coordinate with NES team

### Risk 2: Git Push Failures
**Impact**: Medium  
**Probability**: Medium  
**Mitigation**: Implement retry logic, log errors, alert on persistent failures

### Risk 3: Queue Flooding
**Impact**: Medium  
**Probability**: Low  
**Mitigation**: Add rate limiting (future), require authentication, monitor queue depth

### Risk 4: Processing Performance Degradation
**Impact**: Low  
**Probability**: Low  
**Mitigation**: Use database indexes, batch processing, monitor performance metrics

### Risk 5: Validation Logic Drift
**Impact**: Medium  
**Probability**: Medium  
**Mitigation**: Use existing NES validators, add comprehensive tests, document validation rules

## Success Metrics

### Quantitative Metrics
- API response time < 200ms (95th percentile)
- Queue processing completes in < 5 minutes for 100 items
- Test coverage ≥ 90%
- Zero data integrity violations
- < 1% processing failure rate

### Qualitative Metrics
- Contributors can submit requests without developer assistance
- Admins can review and approve requests efficiently
- Error messages are clear and actionable
- System is reliable and requires minimal maintenance
- Audit trail is complete and accessible

## Glossary

- **Queue Item**: A single entity update request stored in NESQueueItem model
- **Action**: Type of entity operation (CREATE_ENTITY, UPDATE_ENTITY, ADD_NAME)
- **Status**: Current state of queue item (PENDING, APPROVED, REJECTED, COMPLETED, FAILED)
- **Payload**: Action-specific data structure containing entity information
- **Auto-Approve**: Feature allowing Admin/Moderator to bypass manual review
- **Augmented Description**: Change description with submitter username appended
- **PublicationService**: NES service for creating and updating entities
- **FileDatabase**: NES database implementation using file-based storage
- **nes-db**: Git repository containing NES entity data files
