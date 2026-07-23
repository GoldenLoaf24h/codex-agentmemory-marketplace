# Codex AgentMemory Marketplace (Windows)

> **来源说明 / Attribution**
>
> 本仓库基于上游开源项目 [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) 做 **Codex / ChatGPT Desktop** 侧打包与 Windows 适配。
>
> - 上游：`rohitg00/agentmemory`（Apache-2.0）
> - 本仓库：面向 **Windows + Codex Desktop** 的 Git marketplace 插件包
> - 不是 OpenAI 官方 Plugins Directory 上架版本
> - 不是官方 agentmemory 仓库本体，而是社区二次打包

Community packaging of [agentmemory](https://github.com/rohitg00/agentmemory) for **Codex / ChatGPT Desktop on Windows**.

This is a **Git marketplace**, not an official OpenAI Plugins Directory listing. Other people can add this repository as a plugin marketplace and install the `agentmemory` plugin from it.

## Target environment

| Item | Value |
|---|---|
| Upstream | [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) |
| Client | **Codex / ChatGPT Desktop** |
| OS focus | **Windows** (PowerShell / Node / `npx`) |
| Distribution | Public GitHub marketplace |
| Official public directory | No |

## What you get

- Portable MCP config via `npx -y @agentmemory/mcp`
- Codex hooks for session start / prompt submit / tool use / compact / stop
- SessionStart auto-start helper for local agentmemory REST backend (`localhost:3111`)
- Windows-oriented startup and troubleshooting notes
- Optimized skills:
  - `recall`, `remember`, `forget`
  - `handoff`, `recap`, `session-history`
  - `commit-context`, `commit-history`
  - `agentmemory-troubleshooting`

## Requirements

- ChatGPT desktop app with Codex / Work mode plugins
- **Windows** recommended for the auto-start path validated here
- Node.js 18+ and `npx` available on PATH
- Network access for first-time `npx` package download

## Add this marketplace in ChatGPT desktop

1. Open **Plugins**
2. Choose **Add plugin marketplace**
3. Fill:

| Field | Value |
|---|---|
| Source | `PyEL666/codex-agentmemory-marketplace` |
| Git ref | `main` |
| Sparse path | *(leave empty)* |

4. Click **Add marketplace**
5. Install **AgentMemory (Codex)** from the marketplace
6. Start a **new chat / new task** after install

CLI equivalent:

```bash
codex plugin marketplace add PyEL666/codex-agentmemory-marketplace --ref main
codex plugin add agentmemory@codex-agentmemory
```

If your Codex UI asks for a sparse path, leave it empty for this repo. Marketplace file lives at:

```text
.agents/plugins/marketplace.json
```

## First-run behavior (Windows / Codex)

On SessionStart the plugin:

1. Probes `http://127.0.0.1:3111/agentmemory/livez`
2. If down, starts `npx -y @agentmemory/agentmemory` in background
3. Waits up to ~30s for readiness
4. Loads session context

If auto-start fails, run manually in PowerShell:

```powershell
npx -y @agentmemory/agentmemory
```

Keep that process running, then restart Codex / open a new task.

## Modes

| Mode | When | Tools |
|---|---|---|
| Local | backend not reachable | fewer MCP tools, local standalone storage |
| Proxy | backend live on `:3111` | full tool surface (50+) |

Probe livez. Do not treat “recall returned something” as proof that Proxy mode is active.

## Multi-agent note

This package sets `AGENT_ID=codex` for the Codex MCP server. If you also run Hermes or another client against the same local agentmemory instance, give each client a distinct `AGENT_ID`.

## Windows notes

- This packaging was validated for **Windows + Codex Desktop**
- Prefer official one-command start: `npx -y @agentmemory/agentmemory`
- Avoid manually splitting engine processes
- Ensure `node` and `npx` work in a normal PowerShell window

## Attribution

- Upstream project: [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory)
- Upstream author: Rohit Ghumare
- License: Apache-2.0 (see `LICENSE`)
- This repository packages **Codex-oriented** install metadata, hooks, skills, and **Windows-friendly** startup for local use

## Privacy

Memory is stored on the user's machine under the local agentmemory data directory (typically `~/.agentmemory`). This marketplace package does not provide a hosted multi-tenant cloud service.

## Disclaimer

This is an unofficial community packaging of [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) for **Windows Codex Desktop** local use and Git marketplace distribution. It is not an OpenAI-reviewed public Plugins Directory submission, and it is not the official upstream repository.
