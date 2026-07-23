# AgentMemory Windows 404 — Root-Cause Research (condensed)

Repo: https://github.com/rohitg00/agentmemory — issues found via `api.github.com/search/issues?q=repo:rohitg00/agentmemory+<kw>`.

## #634 — fix(windows): make agentmemory actually start on Windows (open)
Symptom matches ours exactly: `agentmemory` (v0.9.21) prints "engine started but REST API never responded" and exits, leaving an orphaned `iii.exe` on :3111 with **zero agentmemory routes registered** → every REST/MCP call 404.
Two latent bugs + one defensive:
1. `iii-exec` watches `src/**/*.ts`. Published npm package ships only `dist/` → glob resolves to 0 files. On Windows an empty watch glob makes `iii-exec` **abort before spawning** `node dist/index.mjs` (the route-registering process).
   Fix: watch `dist/**/*.mjs`.
2. `src/config.ts:140` defaults `engineUrl` to `ws://localhost:49134`. On Windows `localhost` prefers IPv6 (`::1`) but iii-engine binds IPv4 only → node child enters `ECONNREFUSED` reconnect loop forever, never registers HTTP triggers.
   Fix: `ws://127.0.0.1:49134` (override via `III_ENGINE_URL`).
3. Hardcoded 15s readiness timeout too tight. Fix: `AGENTMEMORY_READY_TIMEOUT_MS` (default 60000).
Verified (author, Win11/Node22/iii0.11.2): after fix, engine healthy ~1.3s, all 124 REST endpoints registered, MCP shim connects end-to-end.

## #844 — iii-exec worker supervision uses unresolvable relative paths (open, macOS; same class on Windows)
`iii-config.yaml` supervises worker via relative `watch: [src/**/*.ts]` + `exec: [node dist/index.mjs]`. On global-npm install the engine runs with `cwd=$HOME`, so it looks for `$HOME/dist/index.mjs` / `$HOME/src/**/*.ts` → not found → **engine never supervises a worker**. Only the foreground worker the CLI starts (import of worker bundle) runs; kill the terminal → worker dies → nothing respawns it. MCP still connects but returns empty (data safe in KV; just no live handler).
Impact note: README advertises "iii engine worker supervision" replacing pm2/systemd, but on native global-npm nothing supervises the worker. Data layer is fine; only worker supervision is broken.

## #892 — fix(cli): anchor engine cwd and rewrite bundled config with absolute paths (open, closes #844/#700/#303)
Mechanism behind "data-loss-on-restart" reports: bundled config uses cwd-relative paths and engine spawned without a cwd → `./data` stores landed in the invocation dir, and `iii-exec` supervision never resolved → worker never supervised.
Fix in PR: `startIiiBin` writes `~/.agentmemory/iii-config.runtime.yaml` (absolute data + absolute worker exec) each boot, copies legacy `./data` stores, spawns engine with cwd anchored at `~/.agentmemory`. User overrides via `AGENTMEMORY_III_CONFIG` or `~/.agentmemory/iii-config.yaml` pass through verbatim.
NOTE: this is an open PR, NOT yet in 0.9.27 — so the bundled config still has the relative-path bug.

## #1013 — All HTTP REST endpoints return 404 after iii-engine WebSocket reconnection (open)
Affects agentmemory v0.9.27 + iii-sdk 0.11.2 + iii-engine 0.11.2. After the iii-engine WS (port 49134) drops and reconnects, all `/agentmemory/*` return 404 while the node process stays alive (OS KeepAlive doesn't fire). Root cause is iii-engine bug #1796 (trigger unregister not owner-aware), fixed upstream in iii-engine v0.19.2 (PR #1803). Workaround: health-check watchdog that force-restarts after N consecutive health failures.
Distinguish from #634/#844: #1013 happens on a daemon that worked then degraded after ~12–24h WS instability; #634/#844 fail at startup.

## Takeaways for repair
- At startup on Windows: empty `src/**/*.ts` watch + relative `node dist/index.mjs` exec + `localhost` WS → worker never registers routes → all `/agentmemory/*` 404.
- Fix three things: `watch: dist/**/*.mjs`, `exec: <abs node> <abs package>/dist/index.mjs`, and `III_ENGINE_URL=ws://127.0.0.1:49134`.
- Data is never the problem — it lives in `~/.agentmemory/data/state_store.db` and survives stop/start. Never `remove`/`--reset`.
