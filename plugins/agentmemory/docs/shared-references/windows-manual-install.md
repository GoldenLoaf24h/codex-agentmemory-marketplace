# AgentMemory 官方安装（Windows 手动，connect 不支持）

官方 runbook: https://raw.githubusercontent.com/rohitg00/agentmemory/main/INSTALL_FOR_AGENTS.md
源码: https://github.com/rohitg00/agentmemory

> Windows 上 `agentmemory connect hermes` 明确不支持（"Windows: automated connect is not supported"）。
> 所有 wiring 必须手动改 `C:\Users\<user>\AppData\Local\hermes\config.yaml`（不是 ~/.hermes/）。

## 标准步骤（按顺序，每步验后再进）

### 1. 装 CLI（全局）
```bash
npm install -g @agentmemory/agentmemory
agentmemory --version        # 期望打印版本（如 0.9.27）
```

### 2. 启动 server（Windows 必须 pty=true，否则 stdin is not a tty 立即退出）
```bash
# terminal(background=true, pty=true) 跑：
agentmemory
# 验证：
netstat -ano | grep ':3111.*LISTENING'     # 端口在听
agentmemory status                          # Connected / healthy
```

### 3. 配 Hermes MCP（手动写 config.yaml，key 名用 agentmemory）
```yaml
mcp_servers:
  agentmemory:
    command: npx
    args: ["-y", "@agentmemory/mcp"]
    env:
      AGENTMEMORY_URL: http://localhost:3111   # 必填，缺它 shim 降级 7 工具本地 fallback
      AGENTMEMORY_TOOLS: all
memory:
  provider: agentmemory
```
改完重启 gateway（`/restart` 或网关外 `hermes gateway restart`）让 MCP 重连。

### 4. 装官方原生技能（含 /forget）
```bash
npx skills add rohitg00/agentmemory -y
```
装 15 个原生技能（8 可调用 + 7 reference）。MCP 侧 4 个 slash 技能：`/recall` `/remember` `/session-history` `/forget`。

### 5. 验证 round-trip（不许跳过，这是用户铁律）
```bash
curl -fsS http://localhost:3111/agentmemory/health
curl -X POST http://localhost:3111/agentmemory/remember \
  -H "Content-Type: application/json" \
  -d '{"content":"agentmemory install verification probe","concepts":["install-check"]}'
curl -X POST http://localhost:3111/agentmemory/smart-search \
  -H "Content-Type: application/json" \
  -d '{"query":"install verification probe","limit":5}'
# 期望：remember 返回 201，smart-search 返回 200 且含刚才那条
```
若用 MCP 工具：先 `memory_save` 再 `memory_recall` 同条，召回非空 = 真落库（不在 7 工具本地 fallback）。

## 致命坑：MCP shim 降级
- 缺 `AGENTMEMORY_URL` 或 server 未起 → shim 走 7 工具本地 fallback。
- 症状：`memory_save` 返回"成功"但 recall 为空、`standalone.json` 无新条目。
- 修复：配官方 mcp_servers + 重启 gateway 重连；save 后 recall 验证。

## 端口
- 3111 REST / 3113 viewer / 49134 engine。占用的先 `taskkill /F /PID <pid>`。

## 数据位置
- 持久化数据：`C:\Users\<user>\.agentmemory\standalone.json`（权威数据源）
- 配置：`C:\Users\<user>\.agentmemory\.env`
