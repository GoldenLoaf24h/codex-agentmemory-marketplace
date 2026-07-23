# AgentMemory 版本迁移

## 问题

AgentMemory 升级后（如 v0.9.21 → v0.9.24），旧版 `standalone.json` 中的数据**不会自动导入**到新版。MCP 工具查询返回空，但 `~/.agentmemory/standalone.json` 文件仍包含全部历史记忆。

## 诊断

```bash
# 1. 检查 REST API 是否有数据
curl -s http://localhost:3111/agentmemory/search -H "Content-Type: application/json" -d '{"query":"all","limit":5}'

# 2. 检查 standalone.json 是否有旧数据
python -c "import json; d=json.load(open('$HOME/.agentmemory/standalone.json')); print(len(d.get('mem:memories',{})),'memories')"

# 3. 如果 API 返回空但 standalone.json 有数据 → 需要迁移
```

## 迁移方法：逐条 /remember 导入

`/agentmemory/import` API 格式要求极严（`exportData` 必须是 stringified JSON + `version` 字段），容易失败。**推荐用 `/remember` 逐条导入**：

```python
import json, subprocess

with open('C:/Users/<user>/.agentmemory/standalone.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

memories = data.get('mem:memories', {})
success = 0

for mem_id, mem in memories.items():
    payload = {
        'content': mem.get('content', ''),
        'type': mem.get('type', 'fact'),
        'concepts': mem.get('concepts', []),
        'files': mem.get('files', [])
    }
    result = subprocess.run(
        ['curl', '-s', '-X', 'POST', 'http://localhost:3111/agentmemory/remember',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps(payload)],
        capture_output=True, text=True
    )
    resp = json.loads(result.stdout)
    if resp.get('success') or resp.get('id'):
        success += 1

print(f'Restored {success}/{len(memories)} memories')
```

## 验证

```bash
# 搜索一条已知记忆确认恢复成功
curl -s http://localhost:3111/agentmemory/search -H "Content-Type: application/json" -d '{"query":"ESP32","limit":3}'
```

## 关键教训

- **standalone.json 是旧版存储格式**，新版用 REST API + MCP，不自动读取旧文件
- **升级后必须验证数据**：`memory_smart_search` 返回空不代表没数据，可能是版本迁移问题
- **/remember 比 /import 可靠**：import API 格式复杂且容易报错，remember 简单直接

## npm 升级丢失知识图谱（2026-06-10 发现）

**场景**：`npm install -g @agentmemory/mcp@latest` 从 0.9.21 升级到 0.9.27

**现象**：
- 升级后 `agentmemory doctor` 显示 "Knowledge graph populated ✗"
- 记忆数据正常（`~/.agentmemory/standalone.json` 不受影响）
- 但 `dist/data/state_store.db` 被 npm 覆盖删除

**根因**：npm install 会重建 `dist/` 目录，`dist/data/` 下的 iii-engine 状态文件（state_store.db、stream_store）全部丢失。记忆数据存储在 `~/.agentmemory/standalone.json`（不在 dist 里），所以不受影响。

**修复**：重启 server 即可自动重建图谱（iii-engine 从 standalone.json 重新提取）

**预防**：升级前备份 dist/data/：
```bash
cp -r D:/npm-global/node_modules/@agentmemory/agentmemory/dist/data/ /tmp/am-data-backup/
npm install -g @agentmemory/mcp@latest
cp -r /tmp/am-data-backup/* D:/npm-global/node_modules/@agentmemory/agentmemory/dist/data/
```

**数据存储位置对照**：
| 数据类型 | 存储位置 | npm 升级影响 |
|---------|---------|-------------|
| 记忆条目 | `~/.agentmemory/standalone.json` | ✅ 安全 |
| 知识图谱 | `dist/data/state_store.db` | ❌ 会被覆盖 |
| 流数据 | `dist/data/stream_store/` | ❌ 会被覆盖 |
