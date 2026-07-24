# Codex AgentMemory Marketplace (Windows)

Community packaging of [agentmemory](https://github.com/rohitg00/agentmemory) for **Codex / ChatGPT Desktop on Windows**.

This is a **Git marketplace** plugin package, not an OpenAI official Plugins Directory listing.

## Quick start

```powershell
# 1. Install agentmemory globally (allow native module postinstall scripts)
npm install -g --allow-scripts=onnxruntime-node,sharp,protobufjs @agentmemory/agentmemory

# 2. Start the backend
agentmemory

# 3. Open ChatGPT Desktop → Plugins → Add plugin marketplace
#    Source: https://github.com/GoldenLoaf24h/codex-agentmemory-marketplace
#    Install "AgentMemory (Codex / Windows)" and start a new task
```

> **Full upstream installation docs:**  
> [github.com/rohitg00/agentmemory → Installation](https://github.com/rohitg00/agentmemory)

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

First run launches an interactive setup (select agents, configure LLM provider). After setup, the backend starts on `http://localhost:3111`.

## Target environment

| Item | Value |
|---|---|
| Upstream | [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) |
| Client | **Codex / ChatGPT Desktop** |
| OS focus | **Windows** (PowerShell / Node.js) |
| Distribution | Public GitHub marketplace |
| Official public directory | No |

## What you get

- **MCP config** — Plugin ships `.mcp.json` pointing to `@agentmemory/mcp`, no manual setup needed
- **Lifecycle hooks** — SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / PreCompact / Stop
- **Auto-start** — SessionStart hook spawns `agentmemory` backend on `:3111` if not already running (via `cmd.exe` shell, same as typing in PowerShell)
- **Optimized skills**:
  - `recall`, `remember`, `forget`
  - `handoff`, `recap`, `session-history`
  - `commit-context`, `commit-history`
  - `agentmemory-troubleshooting`

## Requirements

- ChatGPT desktop app with Codex / Work mode plugins
- **Windows** recommended
- Node.js 18+ on PATH
- `agentmemory` CLI installed globally (see [Prerequisites](#prerequisites))

## Add this marketplace in ChatGPT Desktop

1. Open **Plugins** → **Add plugin marketplace**
2. Fill:

| Field | Value |
|---|---|
| Source | `https://github.com/GoldenLoaf24h/codex-agentmemory-marketplace` |
| Git ref | `main` |
| Sparse path | *(leave empty)* |

3. Click **Add marketplace**
4. Install **AgentMemory (Codex / Windows)** from the marketplace
5. **Approve all hooks** — go to **Settings → Hooks**, review each hook, and click **Allow / Approve** for every hook entry belonging to this plugin. **Hooks will not run until you explicitly approve them.**
6. **Restart** the app or start a **new task** after install

Marketplace file: `.agents/plugins/marketplace.json`

> **Important:** Codex Desktop requires explicit user approval for every hook a plugin registers. After installing this plugin, navigate to **Settings → Hooks** and approve all hooks (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, Stop). Until approved, the plugin's auto-start, memory recall, and observation capture will be completely silent — no errors, just nothing happens.

## First-run behavior

On SessionStart the plugin:

1. Probes `http://127.0.0.1:3111/agentmemory/livez`
2. If backend is down, spawns `agentmemory` in background via `cmd.exe` (identical to typing `agentmemory` in PowerShell)
3. Waits up to ~30s for readiness
4. Registers session context

If auto-start fails, start the backend manually, then restart Codex:

```powershell
agentmemory
```

Keep that terminal open. The backend must be reachable at port **3111**.

## Modes

| Mode | When | Tools |
|---|---|---|
| Local / InMemoryKV | backend not reachable at `:3111` | reduced tools, standalone storage |
| **Proxy** | backend live on `:3111` | **full tool surface (50+)** |

> Probe `http://127.0.0.1:3111/agentmemory/livez` to check status. A tool returning data is **not** proof that Proxy mode is active.

## Multi-agent note

This package sets `AGENT_ID=codex` for the Codex MCP server. If you also run Hermes or another client against the same agentmemory instance, give each client a distinct `AGENT_ID` to avoid data collision.

## Windows notes

- Validated for **Windows + Codex Desktop**
- Prefer one-command start: `agentmemory` in PowerShell
- Ensure `node` is on PATH (`node --version` works in PowerShell)
- Do not manually split engine processes or run `iii` separately
- Persistent allow-scripts config: `npm config set allow-scripts=... --location=user` (see [Prerequisites](#prerequisites))

## Attribution

- Upstream project: [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory)
- Upstream author: Rohit Ghumare
- License: Apache-2.0 (see `LICENSE`)

## Privacy

Memory is stored locally under `%USERPROFILE%\.agentmemory\data\` (`~/.agentmemory/data/` on Windows). This package does not provide a hosted cloud service.

## Disclaimer

This is an unofficial community packaging of [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) for Windows Codex Desktop local use and Git marketplace distribution. It is not an OpenAI-reviewed public Plugins Directory submission, and it is not the official upstream repository.
