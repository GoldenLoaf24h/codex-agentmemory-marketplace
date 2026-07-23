---
name: agentmemory-troubleshooting
description: "Diagnose and repair agentmemory MCP connectivity in the Codex plugin — MCP tools not loading, memory_save/recall fails unexpectedly, or the MCP server falls back to local InMemoryKV mode. Focuses on the plugin layer: .mcp.json config, npm resolution, node module hygiene, and the standalone MCP server health. NOT for Hermes-specific issues."
---

# AgentMemory Troubleshooting — Codex Plugin Edition

> 本 skill 只处理 **Codex 插件侧的 agentmemory MCP 连接问题**。Hermes 专属问题（hermes doctor、background_process_notifications、gateway restart 等）见 Hermes 版的 troubleshooting skill。

## 架构概要

Codex 插件的 agentmemory MCP server 工作流程：

```
.mcp.json → @agentmemory/mcp/bin.mjs
  → import("@agentmemory/agentmemory/dist/standalone.mjs")  // MCP stdio server
     → probe localhost:3111 /agentmemory/livez
        → 200 → Proxy 模式（转发 MCP 调用到 REST API）
        → fail → Local 模式（InMemoryKV → standalone.json）
```

当前状态：**Local 模式**（REST API 端口 3111 的 business routes 返回 404，MCP 自动降级）。
Local 模式提供 7 个核心 MCP 工具，数据存于 `~/.agentmemory/standalone.json`，功能完整可用。

## 诊断流程（按顺序）

### 1. MCP 工具是否已加载
工具搜索里有没有 `mcp__agentmemory__memory_save` 等？没有 → MCP server 未启动或 Codex 未连接。

### 2. MCP server 是否能正常启动
在终端手动运行验证：

```
node D:\npm-global\node_modules\@agentmemory\mcp\bin.mjs
```

预期输出：`[@agentmemory/mcp] Standalone MCP server v0.9.27 starting...`
若报 `ERR_MODULE_NOT_FOUND` → 包解析问题（见常见问题 #1）。

### 3. 插件配置检查
验证 `.mcp.json`：

- `command`: `node`
- `args`: `["D:\\npm-global\\node_modules\\@agentmemory\\mcp\\bin.mjs"]`
- `env.AGENT_ID`: `codex`
- 路径必须是绝对路径，Windows 用双反斜杠或正斜杠均可

### 4. 操作验证
直接调用 `memory_save`：
✅ 返回 `{"saved":"mem_xxx"}` → 正常
❌ 返回 `{"success":false}` → Local 模式异常或数据存储有问题

## 常见问题与修复

### 1. `ERR_MODULE_NOT_FOUND` — 嵌套的 @agentmemory 包不完整
**现象：** 启动 MCP 时报模块找不到，因为 `@agentmemory/mcp\node_modules\@agentmemory\agentmemory\dist\` 目录不完整（只有 `viewer/`，没有 `standalone.mjs`）。
**修复：** 删除嵌套的不完整包，让 Node 回退到顶层 `D:\npm-global\node_modules\@agentmemory\agentmemory\`：

```
Remove-Item D:\npm-global\node_modules\@agentmemory\mcp\node_modules\@agentmemory -Recurse -Force
```

然后重启 Codex。

### 2. MCP tools 不出现 — 插件未启用
检查 `C:\Users\Lenovo\.codex\config.toml` 中插件配置是否正确，确认 `agentmemory` 在 `[plugins]` 列表中。重启 Codex。

### 3. Local 模式 vs Proxy 模式困惑
当前 REST API（`localhost:3111`）的 business routes 不注册（已知问题），MCP 自动进入 Local 模式。这是**正常运行状态**，不是故障。Local 模式提供 7 个工具：

- `memory_save` / `memory_recall`
- `memory_smart_search`
- `memory_sessions`
- `memory_export`
- `memory_audit`
- `memory_governance_delete`

若未来 REST API 修复，MCP 会自动切换到 Proxy 模式（50+ 工具），无需修改配置。

### 4. REST API 端口 3111 被占但 business routes 404
**现象：** `localhost:3111` 能连上（health/livez 正常），但所有 `/agentmemory/*` 业务路由返回 404。
**根源：** `iii-config.yaml` 中 `iii-exec` 的 `watch` 路径是 `src/**/*.ts`（开发路径），生产环境不触发，`dist/index.mjs` 的路由注册代码从未执行。而 iii-http worker 占用了 3111 端口。
**影响：** 不影响 Codex 插件使用（MCP 已降级到 Local 模式）。如需修复，需要改 `iii-config.yaml` 的 `watch` 和 `exec` 路径为生产值。

## 重要 Pitfalls

- **`curl` 被 `rtk` hook 包装**，输出会带 `[rtk] /!\ No hook installed` 污染信息。用 `curl.exe`（真实二进制）或 Python `urllib` 代替。
- **`node` 路径：** 本机 `D:\nodejs\node.exe` 或 `D:\npm-global\node.exe`。不要假设 `node` 不在 PATH 里，也不要用死路径。
- **`taskkill` 语法：** Windows `/PID xxx /F`（单斜杠），不是 `//PID`。
- **`start cwd` 决定 data 目录（#892）：** `file_path: ./data/state_store.db` 是相对于启动进程的 CWD 的。从 `~/.agentmemory` 启动才能保证数据在标准位置。
- **工具数量：** Local 模式 7 个，Proxy 模式下约 50+。
- **测试记忆要清理：** 诊断过程中产生的测试记忆用 `memory_governance_delete` 清理，别污染持久存储。

## FALSE-ALIVE 陷阱（重要）

**现象：** `memory_recall` 返回了历史记忆（包括之前的持久数据），但 `localhost:3111` 的 livez/health 其实挂了。
**原因：** MCP server 在探测到后端不可达时，**回退到 InMemoryKV 缓存**，里面存了之前 session 缓存的旧数据。所以 recall 看起来正常，但新写入的数据**不会持久化**。
**危险：** 比单纯的「recall 为空」更隐蔽。**永远不要用 `memory_recall` 判断后端是否活着。**

决策矩阵：
| livez/health | memory_recall | 含义 |
|---|---|---|
| 200 | 有数据 | ✅ 正常 |
| 失败 | 空 | 后端挂了，InMemoryKV 空 |
| 失败 | 有数据 | ⚠️ **FALSE-ALIVE**，后端实际挂了，新写入不持久 |

## 验证清单

所有通过才算正常：

- [ ] 工具列表中能看到 `mcp__agentmemory__*` 系列工具
- [ ] `memory_save` → 返回 `"saved": "mem_xxx"`
- [ ] `memory_recall` → 能搜到刚才保存的内容
- [ ] 重启 Codex 后数据仍然可读（持久化验证）

## 引用文件

以下文件保留供参考，但部分内容涉及 REST API 模式（当前未使用）：

- `references/windows-404-rootcause.md` — Windows 上 404 问题的 GitHub issue 研究总结
- `references/iii-http-port-conflict.md` — iii-http 端口冲突详解
- `references/delete-observations.md` — 通过 REST API 删除 Observations（REST mode 下有效）
- `references/memory-cleanup-hygiene.md` — 记忆清理指南
- `references/merge-offline-data.md` — 合并非活跃数据副本（已执行过）
- `references/standalone-json-import.md` — 从 standalone.json 导入记忆
- `scripts/probe_agentmemory.py` — 健康探测脚本（REST API mode）
- `scripts/verify_roundtrip.py` — 完整读写往返验证脚本
