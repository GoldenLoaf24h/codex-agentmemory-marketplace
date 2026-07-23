---
name: agentmemory-troubleshooting
description: "Diagnose and repair agentmemory MCP connectivity in the Codex plugin -- MCP tools not loading, memory_save/recall fails unexpectedly, or the MCP server falls back to local InMemoryKV mode. Focuses on the plugin layer: .mcp.json config, npm resolution, node module hygiene, and MCP server health."
---

# AgentMemory Troubleshooting -- Codex Plugin Edition

This skill handles **Codex plugin-side agentmemory MCP connectivity issues only**.
Hermes-specific issues belong in the Hermes troubleshooting skill.

## Architecture Overview

Codex plugin agentmemory MCP server workflow:

```
.mcp.json -> npx -y @agentmemory/mcp
  -> probe localhost:3111 /agentmemory/livez
     -> 200 OK -> Proxy mode (forward MCP calls to REST API, 53 tools)
     -> fail  -> Local / InMemoryKV mode (standalone storage, ~7 tools)
```

When the backend is running at `localhost:3111`, the MCP operates in **Proxy mode** with full tool surface.
When the backend is unreachable, it falls back to local InMemoryKV with a reduced tool set.


## Prerequisites

Before troubleshooting, ensure agentmemory is installed globally with native module support:

```powershell
npm install -g --allow-scripts=onnxruntime-node,sharp,protobufjs @agentmemory/agentmemory
```

Or set permanent config:
```powershell
npm config set allow-scripts=onnxruntime-node,sharp,protobufjs,protobufjs --location=user
npm install -g @agentmemory/agentmemory
```

Verify: `agentmemory` command must be available in PowerShell.

## Diagnostic Flow (in order)

### 1. Check if MCP tools are loaded
Are `mcp__agentmemory__*` tools visible in the tool list?
No -> MCP server failed to start or Codex hasn't connected it yet.

### 2. Test MCP server manually
Run in terminal:

```
npx -y @agentmemory/mcp
```

Expected: `[@agentmemory/mcp] Standalone MCP server vX.Y.Z starting...`
If `ERR_MODULE_NOT_FOUND` -> nested package resolution issue (see Common Issues).

### 3. Verify plugin .mcp.json
Path: `<plugin-root>/.mcp.json`

- `command`: `npx` (or `node` with direct path)
- `args`: `["-y", "@agentmemory/mcp"]`
- `env.AGENT_ID`: `codex`

### 4. Round-trip test
Call `memory_save` with a test payload, then `memory_recall` the same content.

## Common Issues

### 0. `spawn('npx', ...)` fails on Windows -- auto-start hook broken (hit 2026-07-23)
**Symptom:** SessionStart auto-start hook silently fails. Backend never starts. `agentmemory` command may disappear from PATH after the failed spawn pollutes npm state.
**Root cause:** `npx` on Windows is `npx.cmd` (a batch wrapper). Node.js `child_process.spawn('npx', ...)` without `shell: true` cannot reliably find `.cmd` files. Additionally, `npx -y` uses its own cache separate from the global install, causing version mismatch.
**Fix:** The auto-start script must use `spawn('agentmemory', [], { shell: true })` instead of `spawn('npx', ['-y', '@agentmemory/agentmemory'])`. The `shell: true` flag lets `cmd.exe` resolve `agentmemory.cmd` from PATH -- identical to typing `agentmemory` in PowerShell.
**Recovery if command disappeared:** Re-run `npm install -g @agentmemory/agentmemory` to restore the PATH shims.

### 1. `ERR_MODULE_NOT_FOUND` -- incomplete nested @agentmemory package
**Symptom:** MCP fails because `@agentmemory/mcp\node_modules\@agentmemory\` has only `viewer/`, missing `standalone.mjs`.
**Fix:** Remove the nested incomplete package so Node resolves to the global install:

```
Remove-Item %APPDATA%\npm\node_modules\@agentmemory\mcp\node_modules\@agentmemory -Recurse -Force
```

Or locate the correct path via:

```
npm root -g
```

Then restart Codex.

### 2. MCP tools missing after install -- plugin not activated
Check `~/.codex/config.toml` for the plugin in the `[plugins]` list.
If the `agentmemory` command itself is missing from PowerShell, the npm global state may have been corrupted by a failed auto-start hook. Reinstall:
```powershell
npm install -g @agentmemory/agentmemory
```
Try: restart the app or start a new task.

### 3. FALSE-ALIVE trap (important)

**Symptom:** `memory_recall` returns data but the backend (`localhost:3111`) is actually down.
**Cause:** When the MCP detects the backend is unreachable, it falls back to **InMemoryKV cache**, which may still contain stale data from a previous session. New writes will **not persist**.

**Never use `memory_recall` alone to determine backend health.**

Decision matrix:

| livez/health | memory_recall | Meaning |
|---|---|---|
| 200 | returns data | ✅ Healthy |
| fails | empty | Backend down, InMemoryKV empty |
| fails | returns data | ⚠️ **FALSE-ALIVE** -- backend actually down, new writes lost |

### 4. Auto-start timeout
If the SessionStart auto-start hook fails to start the backend within ~30s, it gives up.
Run manually:

```
agentmemory
```

Wait for the status box (REST API at `http://localhost:3111`), then restart Codex.

**Important:** The auto-start hook probes `localhost:3111/agentmemory/livez` first. If the backend is already running (e.g. started manually), it skips startup entirely -- no conflict.

## Verification Checklist

All must pass:

- [ ] `mcp__agentmemory__*` tools visible in the tool list
- [ ] `memory_save` returns `"saved": "mem_xxx"`
- [ ] `memory_recall` finds the saved content
- [ ] Data persists after Codex restart (proxy mode confirmed)


## Key lessons (2026-07-23)

- **`spawn('npx', ...)` is unreliable on Windows** -- always use `shell: true` or call the binary directly
- **`npx -y` cache is separate from `npm install -g`** -- version mismatch can occur
- **Official repo has no Windows auto-start solution** (Issue #524 still open) -- our `shell: true` approach is the community workaround
- **`agentmemory connect` is unsupported on native Windows** (Issue #557) -- manual config only
- **Failed auto-start can corrupt npm global state** -- reinstall if `agentmemory` command disappears
- **Multiple npm global paths in PATH can cause confusion** -- verify with `npm config get prefix` and `npm root -g`

## Reference Files

The following references document past issues and recovery procedures:

- `references/windows-404-rootcause.md` -- Historical root-cause research on Windows 404 issue (iii-exec watch bug, fixed in later releases)
- `references/iii-http-port-conflict.md` -- Port conflict details (deprecated -- use official CLI single command)
- `references/delete-observations.md` -- How to delete observations via `POST /agentmemory/forget`
- `references/memory-cleanup-hygiene.md` -- Memory cleanup best practices
- `references/merge-offline-data.md` -- Merging orphaned data copies
- `references/standalone-json-import.md` -- Importing from `standalone.json` backup
- `scripts/probe_agentmemory.py` -- Health probe script
- `scripts/verify_roundtrip.py` -- Round-trip verification script (contains Hermes-specific paths; adapt for Codex use)
