# Deleting AgentMemory Observations (`obs_*`) — the real path

**Myth (pre-2026-07-13):** "Observations are immutable / no API to delete them."
**Truth:** `POST /agentmemory/forget` deletes observations by ID within a session.

## Why `memory_governance_delete` fails on obs
`mem::governance-delete` only handles the `mem_*` long-term-memory layer.
Passing `obs_*` IDs returns `{"success":true,"deleted":0}` — silent no-op.
The function that deletes obs is `mem::forget` (src-MOg2zKJs.mjs ~L5659).

## The endpoint
```
POST http://127.0.0.1:3111/agentmemory/forget
Content-Type: application/json
{ "sessionId": "20260713_224912_7c8db3",
  "observationIds": ["obs_mrjca06b_845b40c8bc4d","obs_mrjcf9bs_02a8169b9ef4","obs_mrjcv7m9_dae774d5fae9"],
  "reason": "user requested cleanup of empty-shell observations" }
```
Response: `{"deleted":3,"success":true}`

- `sessionId` is REQUIRED (obs are namespaced per session).
- Omit `observationIds` → wipes ALL obs in that session + session/summary records.

## Finding sessionId + obs IDs
- Viewer: `http://127.0.0.1:3113` → SESSIONS → click a session row → OBSERVATIONS list.
  (Driven headlessly via kimi-webbridge at `:10086` during discovery 2026-07-13.)
- REST: `GET /agentmemory/observations?sessionId=<id>`
- `memory_smart_search` returns `obsId` fields.

## Discovery path that worked (2026-07-13)
1. Opened viewer via kimi-webbridge → confirmed session list + obs counts.
2. END SESSION button → `POST /agentmemory/session/end` (marks completed, does NOT delete obs).
3. Read package source `@agentmemory/agentmemory/dist/src-MOg2zKJs.mjs`:
   - L5659 `sdk.registerFunction("mem::forget", ...)` shows obs deletion needs `{sessionId, observationIds}`.
   - L15748 `api_path: "/agentmemory/forget"` is the HTTP trigger for `mem::forget`.
4. Called the endpoint → `deleted:3` per session. Verified gone via `smart-search` (0 obs hits).

## Safety
- `state_store.db` is locked by `iii.exe`; never edit it by hand. Use the REST endpoint only.
- Always confirm with the user before deleting (destructive op).
- Verify post-delete with `memory_smart_search` / `GET /agentmemory/observations?sessionId=`.
