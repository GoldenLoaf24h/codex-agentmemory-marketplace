---
name: forget
description: Delete specific observations or sessions from agentmemory. Use when user says "forget this", "delete memory", or wants to remove specific data for privacy.
argument-hint: "[what to forget - session ID, file path, or search term]"
user-invocable: true
---

The user wants to remove data from agentmemory: $ARGUMENTS

**IMPORTANT**: This is a destructive operation. Always confirm with the user before deleting.

## Mode note

agentmemory has two modes with different deletion paths:

- **Proxy mode (REST API online)** - 50+ tools, supports full deletion (obs_* and mem_*)
- **Local mode (standalone.json)** - 7 tools, only supports `mem_*` deletion

Check the troubleshooting skill for current mode. When unsure, verify if `memory_governance_delete` is available.

**CRITICAL — pick the right tool by ID type:**
- `mem_*` = long-term memory → delete with `memory_governance_delete`
- **Proxy mode (REST API online)** - 50+ tools, supports full deletion (obs_* and mem_*)

Steps:

1. Find the target IDs.
   - Use `memory_smart_search` (query = user input, `limit:20`) to surface candidate memory/observation IDs and titles.
- **Proxy mode (REST API online)** - 50+ tools, supports full deletion (obs_* and mem_*)
2. Show the user what was found — session IDs, observation IDs, titles — and ask for explicit confirmation before deleting.
3. Delete:
   - **Long-term memory (`mem_*`)**: call `memory_governance_delete` with `memoryIds` + `reason`. Works in both modes.
- **Proxy mode (REST API online)** - 50+ tools, supports full deletion (obs_* and mem_*)
     ```json
     {"sessionId":"<sessionId>","observationIds":["obs_..."],"reason":"<short reason>"}
     ```
     Returns `{"deleted":N,"success":true}`.
- **Proxy mode (REST API online)** - 50+ tools, supports full deletion (obs_* and mem_*)
4. In Local mode, obs_* cannot be deleted — inform the user.
5. Confirm the deletion count back to the user. Verify with `memory_smart_search` that the IDs no longer appear.

**Never delete without explicit user confirmation.**
