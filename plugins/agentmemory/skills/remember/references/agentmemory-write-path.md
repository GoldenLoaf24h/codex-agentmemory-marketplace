# AgentMemory Write Path (verified 2026-07-18)

The AgentMemory Viewer (localhost:3113) is read-only for creation — there is no
"new" form. Durable memories, actions, and crystals are written through the
`iii` engine's `trigger` functions, NOT the REST API.

## Engine location
- Binary: `C:\Users\Lenovo\.agentmemory\bin\iii.exe`
- Source of truth for function signatures:
  `D:\npm-global\node_modules\@agentmemory\agentmemory\dist\index.mjs`
  (283 functions; prefixes `mem::` and `api::`). Grep this file to confirm
  a function's exact payload shape before calling it.
- Liveness: `GET http://127.0.0.1:3111/agentmemory/livez` -> 200.
  NEVER use `memory_recall` to judge liveness (false-alive).

## Remember (durable memory)
```
iii trigger --function-id mem::remember --payload '{"content":"...","type":"fact","project":"D:/workspace/Hermes","concepts":["kw"]}'
```
- `content` (string, required) is the only mandatory field.
- `type` in `pattern|preference|architecture|bug|workflow|fact` (defaults to `fact`).
- The engine auto-dedupes/supersedes by semantic overlap — re-saving a refined
  version creates a new `isLatest` entry chained via `supersedes`.

## Actions (task tracker) + Crystals (3-line digests)
Actions are the input to crystallization. Note the two-step dance:
```
# 1. create (status is ALWAYS forced to "pending", input ignored)
iii trigger --function-id mem::action-create --payload '{"title":"...","description":"...","priority":6,"project":"D:/workspace/Hermes","tags":["x"],"status":"done"}'
# 2. flip to done (crystallize requires done/cancelled)
iii trigger --function-id mem::action-update --payload '{"actionId":"<id>","status":"done"}'
# 3. crystallize those actions into a 3-line digest (calls LLM ~60s+)
iii trigger --function-id mem::crystallize --timeout-ms 180000 --payload '{"actionIds":["<id1>","<id2>"],"sessionId":"<optional-label>","project":"D:/workspace/Hermes"}'
```
- `mem::crystallize` returns `actionIds is required` if you pass `sessionId`
  alone — it consumes **actionIds**, not a bare session.
- The `iii trigger` client defaults to a 30s timeout and will report
  "Timed out waiting for the engine" even though the engine finished in the
  background. Always pass `--timeout-ms 180000` and verify with
  `GET http://127.0.0.1:3111/agentmemory/crystals` rather than trusting the
  client's exit.

## Forget (cleanup)
```
iii trigger --function-id mem::forget --payload '{"memoryId":"<id>"}'
# or batch:
iii trigger --function-id mem::governance-delete --payload '{"memoryIds":["<id1>","<id2>"],"reason":"consolidation"}'
```
- `mem::forget` with `memoryId` deletes one; `mem::governance-delete` takes an
  array. Both strip the item from the search index and vector store.

## REST API (read-only / diagnostic — NOT for writes)
| Endpoint | Use |
|----------|-----|
| `GET /agentmemory/livez` | liveness (200 = alive) |
| `GET /agentmemory/memories` | list all memories (paginate via the raw JSON) |
| `GET /agentmemory/actions` | list actions |
| `GET /agentmemory/crystals` | list crystals (poll after crystallize) |

`POST /agentmemory/actions` etc. exist but are effectively read-gated and will
return `400 title is required` for writes — do NOT use them; use `iii trigger`.
