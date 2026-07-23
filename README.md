# Codex AgentMemory Marketplace (Windows)

Community packaging of [agentmemory](https://github.com/rohitg00/agentmemory) for **Codex / ChatGPT Desktop on Windows**.

This is a **Git marketplace** plugin package, not an OpenAI official Plugins Directory listing. Others can add this repository as a plugin marketplace and install the `agentmemory` plugin from it.

## Prerequisites

agentmemory depends on native modules (`onnxruntime-node`, `sharp`, `protobufjs`) that require postinstall scripts to compile. **You must allow these scripts before installing.**

### Option A: Allow on install (recommended)

```powershell
npm install -g --allow-scripts=onnxruntime-node,sharp,protobufjs @agentmemory/agentmemory
```

### Option B: Permanent allow-scripts config

```powershell
npm config set allow-scripts=onnxruntime-node,sharp,protobufjs,protobufjs --location=user
npm install -g @agentmemory/agentmemory
```

After this, subsequent installs/upgrades won't need the `--allow-scripts` flag.

### Verify installation

```powershell
agentmemory
```

First run launches an interactive setup (select agents, configure LLM provider). After setup, the backend runs at `http://localhost:3111`.

> **Full installation docs:**  
> [github.com/rohitg00/agentmemory → Installation](https://github.com/rohitg00/agentmemory)

## Target environment

| Item | Value |
|---|---|
| Upstream | [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) |
| Client | **Codex / ChatGPT Desktop** |
| OS focus | **Windows** (PowerShell / Node.js) |
| Distribution | Public GitHub marketplace |
| Official public directory | No |

## What you get

- Portable MCP config via `npx -y @agentmemory/mcp`
- Codex hooks for session start / prompt submit / tool use / compact / stop
- **SessionStart auto-start**: plugin launches `agentmemory` backend (`localhost:3111`) on Codex startup if not already running
- Windows-native auto-start via `shell: true` (uses `cmd.exe` to resolve `agentmemory.cmd` from PATH)
- Optimized skills:
  - `recall`, `remember`, `forget`
  - `handoff`, `recap`, `session-history`
  - `commit-context`, `commit-history`
  - `agentmemory-troubleshooting`

## Requirements

- ChatGPT desktop app with Codex / Work mode plugins
- **Windows** recommended
- Node.js 18+ on PATH
- `agentmemory` CLI installed globally (see [Prerequisites](#prerequisites) above)

## Add this marketplace in ChatGPT desktop

1. Open **Plugins** → **Add plugin marketplace**
2. Fill:

| Field | Value |
|---|---|
| Source | `GoldenLoaf24h/codex-agentmemory-marketplace` |
| Git ref | `main` |
| Sparse path | *(leave empty)* |

3. Click **Add marketplace**
4. Install **AgentMemory (Codex / Windows)** from the marketplace
5. Start a **new chat / new task** after install

CLI equivalent:

```bash
codex plugin marketplace add GoldenLoaf24h/codex-agentmemory-marketplace --ref main
codex plugin add agentmemory@codex-agentmemory
```

Marketplace file: `.agents/plugins/marketplace.json`

## First-run behavior (Windows / Codex)

On SessionStart the plugin:

1. Probes `http://127.0.0.1:3111/agentmemory/livez`
2. If backend is not running, spawns `agentmemory` in background via `cmd.exe` shell (equivalent to typing `agentmemory` in PowerShell)
3. Waits up to ~30s for readiness
4. Registers session context

If auto-start fails, run manually in PowerShell, then restart Codex:

```powershell
agentmemory
```

## Modes

| Mode | When | Tools |
|---|---|---|
| Local / InMemoryKV | backend not reachable | reduced tools, standalone storage |
| **Proxy** | backend live on `:3111` | **full tool surface (50+)** |

Probe livez. Do not treat "recall returned something" as proof that Proxy mode is active.

## Multi-agent note

This package sets `AGENT_ID=codex` for the Codex MCP server. If you also run Hermes or another client against the same local agentmemory instance, give each client a distinct `AGENT_ID` to avoid data collision.

## Windows notes

- Validated for **Windows + Codex Desktop**
- Prefer one-command start: `agentmemory` in PowerShell
- Ensure `node` is on PATH (`node --version` works in PowerShell)
- Do not manually split engine processes or run `iii` separately
- If npm postinstall blocks (`onnxruntime-node`, `sharp`, `protobufjs`), see [Prerequisites](#prerequisites) above

## Attribution

- Upstream project: [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory)
- Upstream author: Rohit Ghumare
- License: Apache-2.0 (see `LICENSE`)
- This repository packages Codex-oriented install metadata, hooks, skills, and Windows-friendly startup for local use

## Privacy

Memory is stored locally under `~/.agentmemory/data/`. This marketplace package does not provide a hosted multi-tenant cloud service.

## Disclaimer

This is an unofficial community packaging of [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) for Windows Codex Desktop local use and Git marketplace distribution. It is not an OpenAI-reviewed public Plugins Directory submission, and it is not the official upstream repository.
