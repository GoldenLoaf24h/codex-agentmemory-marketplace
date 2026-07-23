# Importing Memories from `standalone.json` via API

> Hit: 2026-07-21
> AgentMemory v0.9.27, Windows

## When This Applies

After a server restart, the search index shows `{entries: 0}` even though `standalone.json` (at `~/.agentmemory/standalone.json`) contains memories. The `state_store.db` format may be incompatible between engine versions, or the new server instance created a fresh empty database.

## Root Cause

When `agentmemory` starts:

1. `iii-engine` reads/writes `state_store.db` (KV store, binary `.bin` files)
2. AgentMemory worker loads data from the KV store and rebuilds the search index
3. If the new engine version can't read the old `.bin` format, the search index is rebuilt with `0 entries`

The `standalone.json` is a **backup/export** file — it's NOT the primary data store. The server doesn't auto-import it.

## Recovery: Import via API

The `POST /agentmemory/remember` API creates new memories. Use it to re-import all entries from `standalone.json`.

### Prerequisites

- Server running on `localhost:3111`
- Python with `requests` library

### Script

```python
import json, requests, time

with open('C:/Users/Lenovo/.agentmemory/standalone.json') as f:
    data = json.load(f)

memories = data.get('mem:memories', {})
print(f'Found {len(memories)} memories to import')

success = 0
fail = 0
for k, v in memories.items():
    payload = {
        'title': v.get('title', ''),
        'content': v.get('content', v.get('narrative', '')),
        'type': v.get('type', 'fact'),
    }
    try:
        resp = requests.post(
            'http://localhost:3111/agentmemory/remember',
            json=payload,
            timeout=10
        )
        if resp.json().get('success'):
            success += 1
        else:
            fail += 1
    except Exception as e:
        fail += 1
    
    if success % 10 == 0 and success > 0:
        print(f'  ... {success} imported')
    time.sleep(0.05)

print(f'Import complete: {success} success, {fail} failed')
```

### Note: Status Code

The `remember` API returns **201** (not 200) on success. Check `resp.json().get('success')` — not `resp.status_code == 200`.

### Verification

```bash
curl -s http://localhost:3111/agentmemory/memories | python -c "import json,sys; print(f'Total: {json.load(sys.stdin).get(\"total\")}')"
curl -s -X POST http://localhost:3111/agentmemory/smart-search -H 'Content-Type: application/json' -d '{"query":"<known title>","limit":3}'
```

## Data Persistence After Import

Imported memories are persisted to `state_store.db` automatically. After restart, the server should load them and rebuild the search index with the correct entry count.

## Pitfalls

- **Use `POST /agentmemory/remember`** — NOT `POST /agentmemory/memories` (that's a GET endpoint).
- **`standalone.json` schema**: `{ "mem:memories": { "mem_xxx": { ... } } }`
- **Lossy import**: only `title`, `content`, `type` are imported. `concepts`, `files`, `strength`, `sessionIds` are lost.
- **No dedup**: running twice creates 2x the memories.
- **Wait for index rebuild**: first search may trigger rebuild — wait a few seconds.