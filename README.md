# Codex AgentMemory Marketplace (Windows)

> 本仓库基于上游开源项目 [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) 做 **Codex / ChatGPT Desktop** 侧打包与 Windows 适配。不是 OpenAI 官方插件，也不是上游仓库本体。

Community packaging of [agentmemory](https://github.com/rohitg00/agentmemory) for **Codex / ChatGPT Desktop on Windows**.

**Git marketplace** 插件包，其他人可以通过添加此仓库为插件市场来安装。

---

## 安装前准备 / Prerequisites

agentmemory 的 npm 包依赖 `onnxruntime-node`、`sharp`、`protobufjs` 等原生模块，这些模块需要执行 postinstall 脚本编译。在安装之前，**必须先允许这些脚本运行**。

### 方式一：安装时临时允许（推荐）

```powershell
npm install -g --allow-scripts=onnxruntime-node,sharp,protobufjs @agentmemory/agentmemory
```

### 方式二：永久配置 allow-scripts

```powershell
npm config set allow-scripts=onnxruntime-node,sharp,protobufjs,protobufjs --location=user
npm install -g @agentmemory/agentmemory
```

配置后，后续安装/升级 npm 包时不再需要重复添加 `--allow-scripts`。

### 验证安装

```powershell
agentmemory
```

首次运行会进入引导配置（选择使用的 agent、配置 LLM provider 等）。配置完成后 agentmemory 后端会启动在 `http://localhost:3111`。

> **完整安装方案请参阅上游官方文档：**  
> [github.com/rohitg00/agentmemory → Installation](https://github.com/rohitg00/agentmemory)

---

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
- **SessionStart auto-start**: plugin automatically launches `agentmemory` backend (`localhost:3111`) on Codex startup if not already running
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
- `agentmemory` CLI installed globally（见上方安装前准备）

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
2. If backend is not running, starts `agentmemory` in background via `cmd.exe` shell (equivalent to typing `agentmemory` in PowerShell)
3. Waits up to ~30s for readiness
4. Loads session context

If auto-start fails, run manually in PowerShell, then restart Codex:

```powershell
agentmemory
```

## Modes

| Mode | When | Tools |
|---|---|---|
| Local / InMemoryKV | backend not reachable | fewer MCP tools, standalone storage |
| **Proxy** | backend live on `:3111` | **full tool surface (50+)** |

Probe livez. Do not treat "recall returned something" as proof that Proxy mode is active.

## Multi-agent note

This package sets `AGENT_ID=codex` for the Codex MCP server. If you also run Hermes or another client against the same local agentmemory instance, give each client a distinct `AGENT_ID` to avoid data collision.

## Windows notes

- This packaging was validated for **Windows + Codex Desktop**
- Prefer one-command start: `agentmemory` in PowerShell
- Ensure `node` is on PATH (`node --version` works in PowerShell)
- Avoid manually splitting engine processes or running `iii` separately
- If npm postinstall blocks (`onnxruntime-node`, `sharp`, `protobufjs`), see [安装前准备](#安装前准备--prerequisites) above

## Attribution

- Upstream project: [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory)
- Upstream author: Rohit Ghumare
- License: Apache-2.0 (see `LICENSE`)
- This repository packages Codex-oriented install metadata, hooks, skills, and Windows-friendly startup for local use

## Privacy

Memory is stored on the user's machine under `~/.agentmemory/data/`. This marketplace package does not provide a hosted multi-tenant cloud service.

## Disclaimer

This is an unofficial community packaging of [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) for Windows Codex Desktop local use and Git marketplace distribution. It is not an OpenAI-reviewed public Plugins Directory submission, and it is not the official upstream repository.
