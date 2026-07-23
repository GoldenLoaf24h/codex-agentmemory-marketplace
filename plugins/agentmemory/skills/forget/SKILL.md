---
name: forget
description: Delete specific observations or sessions from agentmemory. Use when user says "forget this", "delete memory", or wants to remove specific data for privacy.
argument-hint: "[what to forget - session ID, file path, or search term]"
user-invocable: true
---

The user wants to remove data from agentmemory: $ARGUMENTS

**IMPORTANT**: This is a destructive operation. Always confirm with the user before deleting.

## Mode note

agentmemory 有两种模式，删除路径不同：

- **Proxy 模式（REST API 在线）** — 50+ 工具，支持完整删除（obs_* 和 mem_*）
- **Local 模式（standalone.json）** — 7 个工具，仅支持 `mem_*` 删除

当前状态见 troubleshooting skill。不确定模式时先验证 `memory_governance_delete` 是否存在。

**CRITICAL — pick the right tool by ID type:**
- `mem_*` = long-term memory → delete with `memory_governance_delete`
- `obs_*` = session observation → `memory_governance_delete` SILENTLY NO-OPS on these (`deleted:0`). Delete with `POST /agentmemory/forget` using `{sessionId, observationIds}` (PROXY mode only).

Steps:

1. Find the target IDs.
   - Use `memory_smart_search` (query = user input, `limit:20`) to surface candidate memory/observation IDs and titles.
   - In Proxy mode, open the viewer at `http://127.0.0.1:3113` (SESSIONS page) or call `GET /agentmemory/observations?sessionId=<id>` to list obs IDs in a session.
2. Show the user what was found — session IDs, observation IDs, titles — and ask for explicit confirmation before deleting.
3. Delete:
   - **Long-term memory (`mem_*`)**: call `memory_governance_delete` with `memoryIds` + `reason`. Works in both modes.
   - **Session observations (`obs_*`, Proxy mode only)**: `POST /agentmemory/forget` with body:
     ```json
     {"sessionId":"<sessionId>","observationIds":["obs_..."],"reason":"<short reason>"}
     ```
     Returns `{"deleted":N,"success":true}`.
   - **Entire session (Proxy mode only)**: `POST /agentmemory/forget` with `{"sessionId":"<id>"}` only — deletes all obs + session record.
4. In Local mode, obs_* cannot be deleted — inform the user.
5. Confirm the deletion count back to the user. Verify with `memory_smart_search` that the IDs no longer appear.

**Never delete without explicit user confirmation.**
