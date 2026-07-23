# iii-http Port 3111 Conflict (2026-07-12, revised)

## Architecture (still accurate)

`iii-config.yaml` configures `iii-http` worker on `port: 3111`. The engine starts iii-http which grabs 3111. The CLI's inline REST layer (`src-MOg2zKJs.mjs`) also wants 3111 (`III_REST_PORT` default).

**Official CLI handles this**: it starts the engine, waits for WS readiness, then imports the REST layer which binds 3111. The timing works because the CLI controls the sequence.

## What we did wrong (deprecated — do NOT follow)

> ⚠️ The manual split recipe below is **deprecated**. It was the approach we used
> before understanding the CLI's inline architecture. It works but is fragile,
> breaks on gateway restart, and kills iii.exe when you taskkill the 3111 holder
> (because iii-http is a child of iii.exe).

The old recipe was:
1. Start `iii.exe` separately
2. Kill whoever holds 3111 (iii-http)
3. Start `node index.mjs` separately

**Problem**: iii-http is a child of iii.exe. Killing the 3111 PID kills the
entire engine (49134 goes down too). You end up in a loop of restart-kill-restart.

## Correct fix (current)

```bash
cd C:/Users/Lenovo/.agentmemory && npx -y @agentmemory/agentmemory
```

One command. The CLI spawns the engine, waits for it, then inline-imports the
REST layer. If port 3111 is already in use:

1. `netstat -ano | findstr :3111` → find PID
2. `taskkill /PID <pid> /F` (single slash, not `//PID`)
3. `rm -f ~/.agentmemory/iii.pid ~/.agentmemory/worker.pid ~/.agentmemory/engine-state.json`
4. Re-run `npx -y @agentmemory/agentmemory`

If the conflict recurs on every gateway restart, the durable fix is to edit
`iii-config.yaml` and change the `iii-http` worker's `port` to something other
than 3111 (e.g. 3115). But this is a config change requiring engine restart.

## Why hermes doctor doesn't catch this

`hermes doctor` only checks config-level state. It never probes whether 3111
serves `/agentmemory/*` routes. A clean doctor run is NOT proof the backend works.

## Why git-bash `ps` lies

`ps -p <windows_pid>` inside MSYS reports the Windows process as "DEAD" because
MSYS can't see native PIDs. Use PowerShell `Get-NetTCPConnection -LocalPort 3111
| Select OwningProcess` for truth.
