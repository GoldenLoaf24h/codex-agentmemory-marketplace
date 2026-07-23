# Windows Startup Patterns

> Verified on Windows 10 + Git Bash + Hermes Agent.

## Startup sequence

1. Check whether the service is already up:
   - `netstat -ano | grep ":3111.*LISTEN"` → if present, do not start another instance.
   - If unsure, verify with `memory_search("test")` via MCP instead of relying on `/health`.
2. If not running, start with:
   - Preferred: `agentmemory`
   - Windows fallback: `cd ~/.agentmemory && ./bin/iii.exe --use-default-config`
3. Wait a few seconds, then verify with `memory_search("test")`.

## Pitfalls

- `curl http://localhost:3111/agentmemory/health` may return 404 even when the server is healthy.
- `iii.pid` and `worker.pid` in `~/.agentmemory/` can contain stale PIDs; do not trust them blindly.
- Do not kill processes by PID from those files without checking `netstat` first.
- If using `terminal(background=true)` to start the server, prefer `pty=true`; otherwise the CLI may exit immediately.
