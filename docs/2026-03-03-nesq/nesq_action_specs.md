# NES Queue Action Specifications

This document defines the full specifications for each queue action supported by the `nesq` app. Each action has a specific payload schema, validation rules, and processing behavior.

## Common Fields

Every queue item has these fields:

| Field | Type | Description |
|-------|------|-------------|
| `action` | string (enum) | `CREATE_ENTITY`, `UPDATE_ENTITY`, or `ADD_NAME` |
| `payload` | object | Action-specific data (schemas below) |
| `change_description` | string (required) | Description of the change, stored on the queue item |

The processor uses the NES [PublicationService](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/services/publication/service.py#34-681) to execute these actions against the NES [FileDatabase](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/database/file_database.py#43-1271).

> [!NOTE]
> When the processor persists to NES DB, it appends the submitter's username to the change description:
> `"{change_description} (submitted by {username})"` — this provides clear provenance in NES version history.

---

## Action: `CREATE_ENTITY`

Creates a new entity in the NES database.

### Payload Schema

```json
{
  "entity_type": "person | organization | location | project",
  "entity_subtype": null | "political_party | government_body | hospital | ngo | ...",
  "entity_data": {
    "slug": "string (required, 2-100 chars, pattern: ^[a-z0-9-]+$)",
    "names": [
      {
        "kind": "PRIMARY | ALIAS | ALTERNATE | BIRTH_NAME",
        "en": { "full": "string", "given": "string?", "family": "string?", ... },
        "ne": { "full": "string", "given": "string?", "family": "string?", ... }
      }
    ],
    "tags": ["string"],
    "short_description": { "en": { "value": "string" }, "ne": { "value": "string" } },
    "description": { "en": { "value": "string" }, "ne": { "value": "string" } },
    "contacts": [{ "type": "EMAIL | PHONE | URL | ...", "value": "string" }],
    "identifiers": [{ "scheme": "wikipedia | wikidata | ...", "value": "string" }],
    "attributions": [{ "title": { "en": { "value": "string" } } }],
    "pictures": [{ "type": "thumb | full | wide", "url": "string" }],
    "attributes": {},

    // Person-specific (when entity_type = "person")
    "personal_details": {
      "birth_date": "string?",
      "gender": "male | female | other",
      "birth_place": { "location_id": "entity:location/..." },
      "father_name": { "en": { "value": "string" } },
      "education": [{ "institution": { "en": { "value": "string" } } }],
      "positions": [{ "title": { "en": { "value": "string" } } }]
    },
    "electoral_details": {
      "candidacies": [{ "election_year": 2079, "election_type": "federal", ... }]
    },

    // Organization-specific
    // PoliticalParty: "address", "party_chief", "registration_date", "symbol"
    // GovernmentBody: "government_type"
    // Hospital: "beds", "services", "ownership", "address"

    // Location-specific (when entity_type = "location")
    "parent": "entity:location/...",
    "area": 123.45,
    "lat": 27.7172,
    "lng": 85.3240
  },
  "author_id": "string (required, slug format for NES Author)"
}
```

### Validation Rules

1. `entity_type` — **required**, must be one of: `person`, `organization`, [location](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/location.py#49-54), `project`
2. `entity_data.slug` — **required**, 2-100 chars, lowercase alphanumeric with hyphens only
3. `entity_data.names` — **required**, at least one entry with `kind: "PRIMARY"`, each name must have [en](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/person.py#13-19) or [ne](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/organization.py#23-27) (or both)
4. `entity_subtype` — must be valid for the given `entity_type` per NES `ENTITY_TYPE_MAP`
5. `author_id` — **required**, slug format (used to create/get NES [Author](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/version.py#14-28))


### Example Payload

```json
{
  "action": "CREATE_ENTITY",
  "payload": {
    "entity_type": "person",
    "entity_data": {
      "slug": "sher-bahadur-deuba",
      "names": [
        {
          "kind": "PRIMARY",
          "en": { "full": "Sher Bahadur Deuba" },
          "ne": { "full": "शेरबहादुर देउवा" }
        }
      ],
      "tags": ["politician", "nepali-congress"],
      "short_description": {
        "en": { "value": "Former Prime Minister of Nepal" },
        "ne": { "value": "नेपालका पूर्व प्रधानमन्त्री" }
      },
      "personal_details": {
        "gender": "male",
        "birth_date": "1946-06-13",
        "birth_place": { "location_id": "entity:location/district/dadeldhura" }
      }
    },
    "author_id": "jawafdehi-queue"
  }
}
```

### Processing

1. Call `PublicationService.create_entity(entity_data=payload["entity_data"], author_id=payload["author_id"], change_description=augmented_description)`
2. Store the returned entity ID in `result`

### Error Cases

| Error | Cause |
|-------|-------|
| `Entity with slug already exists` | Duplicate slug + type combination |
| `Unknown entity type` | Invalid `entity_type` |
| `At least one name with kind="PRIMARY" is required` | Missing primary name |
| Pydantic `ValidationError` | Invalid data shape for the entity type |

---

## Action: `UPDATE_ENTITY`

Patches an existing entity's attributes. This is a **merge update** — only the provided fields are changed.

### Payload Schema

```json
{
  "entity_id": "string (required, e.g. 'entity:person/sher-bahadur-deuba')",
  "updates": {
    // Any top-level Entity fields to update:
    "tags": ["string"],
    "short_description": { "en": { "value": "string" } },
    "description": { "en": { "value": "string" } },
    "contacts": [{ "type": "EMAIL", "value": "user@example.com" }],
    "identifiers": [{ "scheme": "wikipedia", "value": "Sher_Bahadur_Deuba" }],
    "pictures": [{ "type": "thumb", "url": "https://..." }],
    "attributes": {},

    // Type-specific fields (only for matching entity type)
    "personal_details": { ... },
    "electoral_details": { ... },
    "address": { ... },
    "party_chief": { ... },
    "parent": "entity:location/...",
    "area": 123.45
  },
  "author_id": "string (required)"
}
```

### Validation Rules

1. [entity_id](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/person.py#139-150) — **required**, must be a valid NES entity ID format (`entity:<type>/<slug>` or `entity:<type>/<subtype>/<slug>`)
2. `updates` — **required**, non-empty object
3. `updates` must NOT contain immutable fields: `slug`, [type](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/location.py#49-54), `sub_type`, `created_at`, `version_summary`, [id](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/version.py#47-51)
4. `author_id` — **required**, slug format


### Processing

1. Fetch existing entity via `PublicationService.get_entity(entity_id)`
2. Deep-merge `updates` into the entity (replace provided fields, keep unmodified fields)
3. Call `PublicationService.update_entity(merged_entity, author_id, augmented_description)`
4. Store the updated entity ID and version number in `result`

### Example Payload

```json
{
  "action": "UPDATE_ENTITY",
  "payload": {
    "entity_id": "entity:person/sher-bahadur-deuba",
    "updates": {
      "tags": ["politician", "nepali-congress", "prime-minister"],
      "identifiers": [
        { "scheme": "wikipedia", "value": "Sher_Bahadur_Deuba", "url": "https://en.wikipedia.org/wiki/Sher_Bahadur_Deuba" }
      ]
    },
    "author_id": "jawafdehi-queue"
  }
}
```

### Error Cases

| Error | Cause |
|-------|-------|
| `Entity does not exist` | Invalid [entity_id](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/person.py#139-150) |
| `Cannot modify immutable field: slug` | Attempted to change slug/type/sub_type |
| Pydantic `ValidationError` | Updated data doesn't validate against entity model |

---

## Action: `ADD_NAME`

Adds a name (or misspelled name) to an existing entity. This is a convenience action that wraps an `UPDATE_ENTITY` specifically for the [names](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/entity.py#192-201) or `misspelled_names` list.

### Payload Schema

```json
{
  "entity_id": "string (required, e.g. 'entity:person/sher-bahadur-deuba')",
  "name": {
    "kind": "PRIMARY | ALIAS | ALTERNATE | BIRTH_NAME",
    "en": { "full": "string", "given": "string?", "family": "string?" },
    "ne": { "full": "string", "given": "string?", "family": "string?" }
  },
  "is_misspelling": false,
  "author_id": "string (required)"
}
```

### Validation Rules

1. [entity_id](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/person.py#139-150) — **required**, valid NES entity ID
2. [name](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/entity.py#192-201) — **required**, must have at least [en](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/person.py#13-19) or [ne](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/organization.py#23-27), with a non-empty `full` field
3. `name.kind` — **required**, valid [NameKind](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/base.py#34-42) value
4. `is_misspelling` — optional boolean, defaults to `false`. If `true`, appends to `misspelled_names` instead of [names](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/entity.py#192-201)
5. `author_id` — **required**, slug format


### Processing

1. Fetch existing entity via `PublicationService.get_entity(entity_id)`
2. If `is_misspelling` is `true`: append to `misspelled_names` list
3. If `is_misspelling` is `false`: append to [names](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/entity.py#192-201) list
4. Call `PublicationService.update_entity(entity, author_id, augmented_description)`
5. Store entity ID and new name count in `result`

### Example Payloads

**Adding an alias:**
```json
{
  "action": "ADD_NAME",
  "payload": {
    "entity_id": "entity:person/sher-bahadur-deuba",
    "name": {
      "kind": "ALIAS",
      "en": { "full": "S.B. Deuba" }
    },
    "is_misspelling": false,
    "author_id": "jawafdehi-queue"
  }
}
```

**Adding a misspelling:**
```json
{
  "action": "ADD_NAME",
  "payload": {
    "entity_id": "entity:person/sher-bahadur-deuba",
    "name": {
      "kind": "ALTERNATE",
      "en": { "full": "Sher Bahadur Devba" }
    },
    "is_misspelling": true,
    "author_id": "jawafdehi-queue"
  }
}
```

### Error Cases

| Error | Cause |
|-------|-------|
| `Entity does not exist` | Invalid [entity_id](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/person.py#139-150) |
| `Name must have at least one of en or ne` | Missing both language fields |
| Pydantic `ValidationError` | Invalid name structure |

---

## Test Plan

### `test_models.py` — Model Tests

| # | Test | Description |
|---|------|-------------|
| 1 | `test_create_queue_item_defaults` | QueueItem created with status=PENDING by default |
| 2 | `test_create_queue_item_all_fields` | QueueItem with all fields populated |
| 3 | `test_status_choices` | All status values (PENDING, APPROVED, REJECTED, COMPLETED, FAILED) are valid |
| 4 | `test_action_choices` | All action values (CREATE_ENTITY, UPDATE_ENTITY, ADD_NAME) are valid |
| 5 | `test_queue_item_ordering` | Items ordered by `-created_at` |
| 6 | `test_submitted_by_required` | ForeignKey to User is enforced |
| 7 | `test_reviewed_by_nullable` | reviewed_by starts as null |
| 8 | `test_payload_accepts_valid_json` | JSONField stores arbitrary valid JSON |

### `test_serializers.py` — Serializer Tests

**CREATE_ENTITY validation:**

| # | Test | Description |
|---|------|-------------|
| 1 | `test_create_entity_valid_person` | Full valid person payload passes |
| 2 | `test_create_entity_valid_organization` | Full valid organization payload passes |
| 3 | `test_create_entity_valid_location` | Full valid location payload passes |
| 4 | `test_create_entity_missing_slug` | Rejected: no slug |
| 5 | `test_create_entity_missing_names` | Rejected: no names |
| 6 | `test_create_entity_no_primary_name` | Rejected: names exist but none is PRIMARY |
| 7 | `test_create_entity_invalid_entity_type` | Rejected: invalid entity_type |
| 8 | `test_create_entity_invalid_subtype_for_type` | Rejected: subtype doesn't match type |
| 9 | `test_create_entity_missing_author_id` | Rejected: no author_id |
| 10 | `test_create_entity_missing_change_description` | Rejected: no change_description |
| 11 | `test_create_entity_bilingual_names` | Valid with both en and ne name parts |
| 12 | `test_create_entity_nepali_only_name` | Valid with only ne name |

**UPDATE_ENTITY validation:**

| # | Test | Description |
|---|------|-------------|
| 13 | `test_update_entity_valid` | Valid update payload passes |
| 14 | `test_update_entity_missing_entity_id` | Rejected: no entity_id |
| 15 | `test_update_entity_empty_updates` | Rejected: empty updates dict |
| 16 | `test_update_entity_immutable_slug` | Rejected: updates contains `slug` |
| 17 | `test_update_entity_immutable_type` | Rejected: updates contains [type](file:///Users/kwame/Documents/projects/newnepal/newnepal-meta/services/nes/nes/core/models/location.py#49-54) |
| 18 | `test_update_entity_immutable_version_summary` | Rejected: updates contains `version_summary` |
| 19 | `test_update_entity_valid_tags_only` | Valid: updating only tags |
| 20 | `test_update_entity_valid_description` | Valid: updating description |

**ADD_NAME validation:**

| # | Test | Description |
|---|------|-------------|
| 21 | `test_add_name_valid_english` | Valid name with English only |
| 22 | `test_add_name_valid_nepali` | Valid name with Nepali only |
| 23 | `test_add_name_valid_bilingual` | Valid name with both languages |
| 24 | `test_add_name_misspelling_flag` | Valid with is_misspelling=true |
| 25 | `test_add_name_missing_entity_id` | Rejected: no entity_id |
| 26 | `test_add_name_missing_name` | Rejected: no name object |
| 27 | `test_add_name_missing_both_languages` | Rejected: missing en and ne |
| 28 | `test_add_name_missing_kind` | Rejected: no name kind |
| 29 | `test_add_name_default_misspelling_false` | is_misspelling defaults to false |

### `test_api_views.py` — API Endpoint Tests

| # | Test | Description |
|---|------|-------------|
| 1 | `test_submit_unauthenticated_rejected` | 401 without token |
| 2 | `test_submit_invalid_token_rejected` | 401 with bad token |
| 3 | `test_submit_valid_create_entity` | 201 with valid CREATE_ENTITY payload |
| 4 | `test_submit_auto_approve_admin` | Admin caller → status=APPROVED |
| 5 | `test_submit_auto_approve_moderator` | Moderator caller → status=APPROVED |
| 6 | `test_submit_contributor_pending` | Contributor caller → status=PENDING |
| 7 | `test_submit_invalid_action` | 400 with unknown action |
| 8 | `test_submit_invalid_payload` | 400 with malformed payload |
| 9 | `test_submit_returns_queue_item` | Response contains item ID and status |
| 10 | `test_get_method_not_allowed` | GET /api/submit_nes_change returns 405 |

### `test_processor.py` — Queue Processor Tests

| # | Test | Description |
|---|------|-------------|
| 1 | `test_process_create_entity_success` | Approved CREATE_ENTITY → COMPLETED |
| 2 | `test_process_update_entity_success` | Approved UPDATE_ENTITY → COMPLETED |
| 3 | `test_process_add_name_success` | Approved ADD_NAME → COMPLETED |
| 4 | `test_process_add_misspelled_name` | ADD_NAME with is_misspelling=true appends to misspelled_names |
| 5 | `test_process_skips_pending` | PENDING items not processed |
| 6 | `test_process_skips_rejected` | REJECTED items not processed |
| 7 | `test_process_skips_completed` | Already COMPLETED items not re-processed |
| 8 | `test_process_skips_failed` | Already FAILED items not re-processed |
| 9 | `test_process_entity_not_found` | UPDATE_ENTITY for missing entity → FAILED with error |
| 10 | `test_process_duplicate_entity` | CREATE_ENTITY for existing slug → FAILED with error |
| 11 | `test_process_invalid_data` | Pydantic validation failure → FAILED with error |
| 12 | `test_process_stores_result` | Result field populated with entity ID on success |
| 13 | `test_process_sets_processed_at` | processed_at timestamp set on completion |
| 14 | `test_process_ordering` | Items processed in created_at order |
| 15 | `test_process_partial_failure` | One failure doesn't stop remaining items |

### `test_admin.py` — Admin Interface Tests

| # | Test | Description |
|---|------|-------------|
| 1 | `test_admin_list_view` | Queue items visible in admin |
| 2 | `test_admin_bulk_approve` | Bulk approve action sets status=APPROVED |
| 3 | `test_admin_bulk_reject` | Bulk reject action sets status=REJECTED |
| 4 | `test_admin_approve_sets_reviewer` | reviewed_by and reviewed_at populated |
| 5 | `test_admin_cannot_approve_non_pending` | Cannot approve COMPLETED/FAILED items |
