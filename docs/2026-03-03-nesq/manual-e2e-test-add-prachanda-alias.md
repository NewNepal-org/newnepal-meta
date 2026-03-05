# NESQ Manual E2E Test: Add "Prachanda" Alias

**Entity:** `entity:person/pushpa-kamal-dahal-prachanda`
**Action:** ADD_NAME — add "Prachanda" as an English alias
**Date:** 2026-03-04

---

## Prerequisites

- Jawafdehi API running locally (`poetry run python manage.py runserver`)
- PostgreSQL database accessible
- `NES_DB_PATH` set to local `nes-db` clone (e.g. `export NES_DB_PATH=~/nes-db/v2`)
- A user account with a DRF auth token
- The entity `entity:person/pushpa-kamal-dahal-prachanda` exists in the nes-db

### Get your auth token

```bash
# If you need to create a token for an existing user:
poetry run python manage.py drf_create_token <username>
```

Save the token:
```bash
export TOKEN="your-token-here"
export BASE_URL="http://localhost:8000"
```

---

## Step 1: Submit the ADD_NAME request

```bash
curl -s -X POST "${BASE_URL}/api/submit_nes_change" \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "ADD_NAME",
    "payload": {
      "entity_id": "entity:person/pushpa-kamal-dahal-prachanda",
      "name": {
        "kind": "ALIAS",
        "en": {
          "full": "Prachanda"
        }
      }
    },
    "change_description": "Adding commonly used alias Prachanda for Pushpa Kamal Dahal"
  }' | python3 -m json.tool
```

### Expected response (201 Created)

```json
{
    "id": 1,
    "action": "ADD_NAME",
    "status": "PENDING",
    "submitted_by": "<your-username>",
    "reviewed_by": null,
    "reviewed_at": null,
    "processed_at": null,
    "created_at": "2026-03-04T..."
}
```

**Save the item ID:** `export ITEM_ID=<id from response>`

### Verify: Check your submissions list

```bash
curl -s "${BASE_URL}/api/my_nes_submissions" \
  -H "Authorization: Token ${TOKEN}" | python3 -m json.tool
```

You should see the item with `"status": "PENDING"`.

---

## Step 2: Approve the item

### Option A: Via Django Admin UI

1. Go to `${BASE_URL}/admin/nesq/nesqueueitem/`
2. Log in with an Admin or Moderator account
3. Find the item (should show entity_id `entity:person/pushpa-kamal-dahal-prachanda`)
4. Check the checkbox next to it
5. Select **"Approve selected PENDING queue items"** from the action dropdown
6. Click **Go**
7. Confirm the success message: _"1 queue item(s) approved successfully."_

### Option B: Via Django shell

```bash
poetry run python manage.py shell -c "
from nesq.models import NESQueueItem, QueueStatus
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
admin = User.objects.get(username='<admin-username>')

item = NESQueueItem.objects.get(pk=${ITEM_ID})
print(f'Before: status={item.status}')

item.status = QueueStatus.APPROVED
item.reviewed_by = admin
item.reviewed_at = timezone.now()
item.save()

print(f'After: status={item.status}, reviewed_by={item.reviewed_by}')
"
```

### Verify: Item is now APPROVED

```bash
curl -s "${BASE_URL}/api/my_nes_submissions" \
  -H "Authorization: Token ${TOKEN}" | python3 -m json.tool
```

The item should now show `"status": "APPROVED"` and a `"reviewed_by"` value.

---

## Step 3: Process the queue

```bash
NES_DB_PATH=~/nes-db/v2 poetry run python manage.py process_queue --verbose
```

### Expected output

```
Using NES database at: /Users/<you>/nes-db/v2
Processed 1 item(s): 1 completed, 0 failed
```

---

## Step 4: Verify the result

### 4a. Verify item status in DB

```bash
curl -s "${BASE_URL}/api/my_nes_submissions" \
  -H "Authorization: Token ${TOKEN}" | python3 -m json.tool
```

The item should now show:
- `"status": "COMPLETED"`
- `"processed_at": "2026-03-04T..."`

### 4b. Verify entity file on disk

```bash
cat ~/nes-db/v2/entity/person/pushpa-kamal-dahal-prachanda.json | python3 -m json.tool
```

Look for the new name entry in the `names` array:

```json
{
    "kind": "ALIAS",
    "en": {
        "full": "Prachanda"
    }
}
```

The entity should now have its original PRIMARY name(s) plus the new ALIAS entry.

### 4c. Verify version was incremented

In the same JSON file, check `version_summary.version_number` — it should be incremented by 1 from the previous value, and `change_description` should read _"Adding commonly used alias Prachanda for Pushpa Kamal Dahal"_.

---

## Step 5 (optional): Verify git diff

If the nes-db is a git repo:

```bash
cd ~/nes-db
git diff v2/entity/person/pushpa-kamal-dahal-prachanda.json
```

You should see the added ALIAS name and updated version_summary in the diff.

> **Note:** In production, the GitHub Actions workflow handles `git add`, `git commit`, and `git push` automatically after `process_queue` runs. For this manual test, the file change is local only.

---

## Alternative: Admin auto-approve (single step)

If you have Admin/Moderator credentials, you can skip the manual approval step:

```bash
curl -s -X POST "${BASE_URL}/api/submit_nes_change" \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "ADD_NAME",
    "payload": {
      "entity_id": "entity:person/pushpa-kamal-dahal-prachanda",
      "name": {
        "kind": "ALIAS",
        "en": {
          "full": "Prachanda"
        }
      }
    },
    "change_description": "Adding commonly used alias Prachanda for Pushpa Kamal Dahal",
    "auto_approve": true
  }' | python3 -m json.tool
```

The response will show `"status": "APPROVED"` immediately. Then run Step 3 to process.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `401 Unauthorized` | Missing or invalid token | Re-generate with `drf_create_token` |
| `400 Bad Request` with payload errors | Invalid entity_id format or name structure | Check entity_id matches `entity:{type}/{slug}` pattern |
| `403 Forbidden` on auto_approve | User is a Contributor, not Admin/Moderator | Use manual approval flow instead |
| `process_queue` says "NES_DB_PATH is not configured" | Missing env var | `export NES_DB_PATH=~/nes-db/v2` |
| Item status is `FAILED` after processing | Entity not found in nes-db | Verify the entity file exists at the expected path |
| Author slug validation error | Username contains underscores | Usernames must match `^[a-z0-9-]+$` (use hyphens) |
