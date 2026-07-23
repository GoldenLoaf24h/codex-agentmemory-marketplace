# AgentMemory Memory Cleanup & Hygiene

## When to clean up
- After a session that saved many probe/test memories
- When `memory_recall` returns duplicate entries
- When stale project snapshots or one-time research clutter the store
- Periodically (monthly) to keep recall signal-to-noise high

## How to list all memories with IDs

```python
import urllib.request, json

base = 'http://127.0.0.1:3111'
req = urllib.request.Request(f'{base}/agentmemory/memories?limit=100')
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read().decode())
memories = data if isinstance(data, list) else data.get('memories', data.get('data', []))
for m in memories:
    print(f'{m["id"]} | {m.get("type","?")} | {m.get("createdAt","?")[:19]} | {(m.get("title") or m.get("content","")[:80])[:80]}')
```

Paginate with `&offset=100` if total > 100.

## Deletion rules

### Delete (safe to remove)
- **Exact duplicates**: same content saved twice (common after import/dedup runs)
- **Test/probe markers**: "test memory", "cleanup verification", "probe_agentmemory"
- **Stale project code details**: paused-project architecture (WQN Rust patterns, SQLite migrations) — belongs in repo, not cross-session memory
- **One-time research**: GitHub project surveys, framework comparisons, article topic lists — session-specific, not reusable
- **Superseded by skill**: if a fact is now fully captured in a skill SKILL.md, the AgentMemory copy is redundant
- **Superseded by corrected fact**: if a later memory corrects an earlier one, delete the wrong one
- **Old pipeline versions**: "v2.1 deployed", "v3.1 deployed" when current is v4+
- **Stale version numbers**: "Hermes v0.17.0" when current is v0.18.2

### Keep (durable, non-redundant)
- Active project roles and methodology (MyStudy analyst role, firecrawl search method)
- Current tool configurations not in any skill (Kimi WebBridge daemon)
- Architecture truths that contradict common misconceptions (CLI inline mode)
- Bug patterns that recur (disabled_toolsets browser → web_search killed)
- Active content strategy (public account positioning)

## Deletion API

### A. Memories (`mem_*`) — `governance_delete`
```python
# Via MCP tool (preferred — goes through the shim):
# mcp__agentmemory_mcp__memory_governance_delete(memoryIds="id1,id2,id3", reason="...")
#   NOTE: comma-separated STRING, not array. Arrays return deleted:0.

# Via REST (if MCP shim is down):
import urllib.request, json
ids = ["mem_xxx", "mem_yyy"]
data = json.dumps({"memoryIds": ",".join(ids), "reason": "stale/superseded"}).encode()
req = urllib.request.Request(
    'http://127.0.0.1:3111/agentmemory/governance-delete',  # <- dash, NOT /governance/memories
    data=data, headers={'Content-Type': 'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=15) as r:
    print(json.loads(r.read().decode()))
```

### B. Observations (`obs_*`) — `POST /agentmemory/forget`  (hit 2026-07-13, REVISES old "immutable" claim)
Observations ARE deletable — the old belief "append-only, no API" is WRONG. Source-verified:
`mem::forget` (src-MOg2zKJs.mjs:5659-5717) is registered as `POST /agentmemory/forget` (line 15748).
It physically deletes obs when given `sessionId` + `observationIds[]`. Deleted obs vanish from `smart-search` immediately.
```python
import urllib.request, json
# Delete specific obs in one session:
payload = {"sessionId": "20260713_224912_7c8db3",
           "observationIds": ["obs_mrjca06b_845b40c8bc4d", "obs_mrjcf9bs_02a8169b9ef4"],
           "reason": "user requested cleanup"}
# Delete ALL obs in a session (also drops session record + summaries):
# payload = {"sessionId": "20260713_224912_7c8db3"}
data = json.dumps(payload).encode()
req = urllib.request.Request(
    'http://127.0.0.1:3111/agentmemory/forget',
    data=data, headers={'Content-Type': 'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=15) as r:
    print(json.loads(r.read().decode()))   # -> {"deleted":N,"success":true}
```
- obs are partitioned per session key `KV.observations(sessionId)` — you MUST know `sessionId`.
  Get it from viewer SESSIONS page (`http://127.0.0.1:3113/#sessions`) or `GET /agentmemory/sessions`.
- `memory_recall` does NOT return obs IDs — use `smart-search` or the viewer to find `obs_xxx` ids + parent session.
- END SESSION first (viewer button) to mark COMPLETED, then forget to purge.

## Key facts
- `memory_governance_delete` / `/agentmemory/governance-delete` → deletes **memories** (`mem_*`) only. Pass obs IDs → `{"success":true,"deleted":0}` silent no-op.
- **Observations ARE deletable** via `POST /agentmemory/forget` with `{sessionId, observationIds[]}`. Old "append-only, no API" claim is FALSE — corrected 2026-07-13.
- `memory_recall` does NOT return IDs (mem or obs) — use `GET /agentmemory/memories` for mem IDs, `smart-search`/viewer for obs IDs.
- Batch delete: comma-separated IDs in one `governance_delete` call (mem), or multiple obs IDs in one `forget` call.
- Deletion is permanent (no undo).

## Redundancy check (MEMORY.md vs AgentMemory)

Before saving to AgentMemory, check:
1. Is this fact already in **MEMORY.md**? → Don't duplicate; MEMORY.md is injected every turn
2. Is this fact already in a **skill SKILL.md**? → Don't duplicate; skill loads on demand
3. Is this fact already in **USER.md**? → Don't duplicate; USER.md is injected every turn

If yes to any → skip the AgentMemory save. The three-layer architecture means each fact lives in exactly ONE place.
