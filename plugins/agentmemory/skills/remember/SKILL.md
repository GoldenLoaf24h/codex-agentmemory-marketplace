---
name: remember
description: Explicitly save an insight, decision, or learning to agentmemory's long-term storage. Use when the user says "remember this", "save this", or wants to preserve knowledge for future sessions.
argument-hint: "[what to remember]"
user-invocable: true
---

The user wants to save this to long-term memory: $ARGUMENTS

Use the `memory_save` MCP tool (provided by the agentmemory server that this plugin wires up automatically via `.mcp.json`) to persist it. Works in both Local and Proxy mode.

Steps:
1. Analyze what the user wants to remember — pull out the core insight, decision, or fact.
2. Extract 2-5 searchable `concepts` (lowercased keyword phrases) that capture what the memory is about. Prefer specific terms over generic ones (`"jwt-refresh-rotation"` beats `"auth"`).
3. Extract any relevant `files` — absolute or repo-relative paths the memory references.
4. Call `memory_save` with the fields:
   - `content` — the full text to remember (preserve the user's phrasing as much as possible)
   - `concepts` — the extracted concept list
   - `files` — the extracted file list (empty array if none apply)
5. Confirm to the user that the memory was saved and show the concepts you tagged so they know what terms will retrieve it later.

## CRITICAL — where durable memory lives

**Durable memory belongs in the agentmemory storage (MCP server), NOT in the agent's local MEMORY.md / memory tool.** Local context is hot-injected for the current session only; it is NOT the cross-session store.

- In **Local mode**, `memory_save` persists to `~/.agentmemory/standalone.json` via the standalone MCP server. Data survives Codex restarts.
- In **Proxy mode** (REST API), `memory_save` writes to the engine's `state_store.db` and also saves via the MCP tool. Both paths converge.

If `memory_save` isn't available, the MCP server didn't start:
- Check plugin is enabled in config.toml
- Restart Codex
- Use `tool_search` with "agentmemory memory_save" to see if tools are available

See `references/agentmemory-write-path.md` for the full function map and worked examples.
