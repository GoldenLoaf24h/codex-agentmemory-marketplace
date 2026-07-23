# Session History Archiving Workflow

When AgentMemory has no sessions yet (common after fresh setup), or when the user wants to extract long-term value from session history.

## Full Archive Pipeline (Export → Audit → Cleanup → Extract → Save → Verify)

When the user asks to "整理记忆", "归档会话", "清理记忆", or "extract value from sessions":

### Phase 1: Export & Audit
```python
# 1. Get current memory state (PREFERRED: read standalone.json directly)
import json, os
with open(os.path.expanduser('~/.agentmemory/standalone.json'), 'r', encoding='utf-8') as f:
    memories = json.load(f).get('mem:memories', {})

# Fallback: REST API (unstable format — returns dict or list inconsistently)
# memory_export()  # ⚠️ may return different formats, prefer standalone.json

# 2. Get session history overview
session_search(limit=10)  # browse mode
```

**⚠️ REST API `/agentmemory/memories` pitfall**: Returns inconsistent formats (sometimes dict, sometimes list). Always prefer reading `~/.agentmemory/standalone.json` directly — it's the authoritative data source.

### Phase 2: Cleanup (delete stale/test/merged memories)
Identify for deletion:
- **Test artifacts**: content = "测试xxx" or "test xxx" with no real substance
- **Superseded entries**: old memories that are strict subsets of newer, more detailed ones
- **Stale facts**: information that has changed (e.g., old config values)

```python
# Delete test artifacts
memory_governance_delete(memoryIds="id1,id2", reason="测试产物，无实际价值")

# Delete superseded entries (AFTER creating the replacement)
memory_governance_delete(memoryIds="old_id", reason="已被更详细的记忆 xxx 覆盖")
```

**Critical**: Always create the replacement memory BEFORE deleting the old one. Never delete without a backup.

### Phase 3: Deep Extraction
Run 4-6 parallel `session_search(query=...)` with topic-specific queries covering:
- Projects (hardware, software, configs)
- Workflows (multi-step procedures)
- Preferences (style, decisions)
- Architecture (system design, tool choices)
- Tools (MCP, plugins, integrations)

For each valuable finding, `memory_save` with proper type/concepts/files.

### Phase 4: Verify
```python
memory_export()  # confirm final count, no stale entries
```

Present summary table: deleted count, new count, final count, type distribution.

---

## Source Priority

1. **AgentMemory** (`memory_sessions`) — preferred, has observations + knowledge graph
2. **Hermes session DB** (`session_search` browse/discover) — fallback, has raw messages + FTS5

## Extraction Query Template (proven effective)

Run 4-6 parallel `session_search(query=...)` covering these dimensions:

```
session_search(query="<hardware> <api> <config>", limit=5)        # Projects & configs
session_search(query="<tool-name> <install> <setup>", limit=5)    # Tooling & setup
session_search(query="<workflow> <process> <step>", limit=5)      # Reusable workflows
session_search(query="<preference> <style> <review>", limit=5)    # User preferences
session_search(query="<architecture> <design> <pattern>", limit=5) # Architecture decisions
```

Each returns: `session_id`, `title`, `match_message_id`, `snippet`, `bookend_start/end`, `messages` (±5 around match).

**Key**: Read the `bookend_start` (first 3 messages = user's goal) and `bookend_end` (last 3 messages = resolution) to understand what was accomplished without reading the full transcript.

## Merge-then-Delete Pattern

When consolidating old memories with new, more detailed ones:

1. **Create** the new, more detailed memory first
2. **Verify** it saved successfully (check returned ID)
3. **Delete** the old memory, referencing the new one in the reason:
   ```
   memory_governance_delete(memoryIds="old_id", reason="已被更详细的记忆 new_id 覆盖")
   ```
4. **Never** delete without creating the replacement first

## Two-Pass Archival Pattern

Effective for large session histories (10+ sessions, 1000+ messages):

- **Pass 1**: Extract obvious high-value items — projects, workflows, preferences, architecture decisions. Quick wins.
- **Pass 2**: Deep dive into specific topics that surfaced in pass 1 — tool configs, MCP setup, debugging patterns, user-provided research findings.

This is more efficient than trying to extract everything in one pass.

## Final Report Format

After archival, present a summary table:

| 操作 | 数量 | 详情 |
|------|:---:|------|
| 🗑️ 删除测试记忆 | N | reason list |
| 🔄 合并旧记忆 | N | old → new mappings |
| ➕ 新增记忆 | N | type distribution |

**Final memory library**: N total, type breakdown (fact×N, workflow×N, preference×N, architecture×N)

## Pitfalls

- **REST API `/agentmemory/memories` returns inconsistent formats** — sometimes dict, sometimes list. When user says "整理记忆" or "精炼总结", always read `~/.agentmemory/standalone.json` directly (it's the authoritative data source), then use REST API only for health/graph verification.
- `session_search(around_message_id=0)` → always errors. Use discovery mode (query=) first, then use returned `match_message_id` for scroll mode.
- AgentMemory sessions empty → use Hermes `session_search()` as data source instead.
- Don't archive transient errors, one-off tasks, or stale data. Focus on: reusable workflows, user preferences, project facts, debugging patterns.
- Don't delete memories without creating replacements first — you lose context permanently.
- When merging old+new memories, delete the old AFTER confirming the new one saved successfully.
- `session_search` with `window=3` on bookend_start is useful for quick triage; use `window=5` for detailed extraction.
- User may share their own research findings (tool comparisons, etc.) — treat as first-class input, don't redo the search. Build on what they provided.
- Two-pass archival is effective: first pass extracts obvious high-value items (projects, workflows, preferences), second pass digs deeper into specific topics (architecture, tool configs, MCP setup).
- Test artifacts commonly look like: "测试xxx", "test memory system connection", "测试深度集成" — these have empty concepts arrays and no real substance. Delete them.
- When the user asks to "清理过时记忆", combine cleanup with deep extraction in one session — it's more efficient than doing them separately.
