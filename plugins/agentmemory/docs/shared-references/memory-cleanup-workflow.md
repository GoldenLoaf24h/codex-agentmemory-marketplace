# 记忆整理工作流

> 诊断→清理→合并→验证

## Step 1：诊断当前状态
```bash
# 基本状态
agentmemory status

# 导出全部数据（查看总量）
curl -s http://localhost:3111/agentmemory/export > /tmp/memory-export.json
wc -c /tmp/memory-export.json
```

## Step 2：分析记忆
```bash
# 读取 standalone.json（主数据源）
cat ~/.agentmemory/standalone.json | python -c "
import json,sys
data=json.load(sys.stdin)
memories=data.get('mem:memories',{})
print(f'总记忆: {len(memories)}')
# 按类型统计
types={}
for m in memories.values():
    t=m.get('type','unknown')
    types[t]=types.get(t,0)+1
for t,c in sorted(types.items(),key=lambda x:-x[1]):
    print(f'  {t}: {c}')
"
```

## Step 3：清理过时记忆
识别过时记忆的标准：
- 旧版本号（v4/v5/v6 被 v7 替代）
- 已废弃的工具/Provider（Seedream/SiliconFlow 被 DashScope 替代）
- 已修复的 bug（不再相关）
- 重复条目（合并为一条）

### ⚠️ 关键：standalone.json 是权威数据源
REST API 的 `forget` 操作**不持久化到 standalone.json**。服务器重启后会从 standalone.json 恢复旧数据，导致删除失效。

**正确清理流程：**
1. 备份 standalone.json
2. 直接编辑 standalone.json，删除过时记忆条目
3. 重启 AgentMemory 服务器加载新数据
4. 用 `memory_recall` 验证删除生效

```python
# 删除记忆的标准操作
import json, shutil
src = pathlib.Path.home() / '.agentmemory/standalone.json'
shutil.copy2(src, src.with_suffix('.json.bak'))  # 备份
data = json.loads(src.read_text(encoding='utf-8'))
memories = data.get('mem:memories', {})
for mid in ['mem_xxx', 'mem_yyy']:
    memories.pop(mid, None)  # 安全删除
data['mem:memories'] = memories
src.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
```

## Step 3.5：切换嵌入模型（如需要）

如果更换 Embedding 模型且维度变化，必须重建向量索引：

```bash
# 1. 修改 .env
OPENAI_EMBEDDING_MODEL=BAAI/bge-m3
OPENAI_EMBEDDING_DIMENSIONS=1024

# 2. 删除旧向量索引文件（关键！否则维度不匹配报错）
rm ~/.agentmemory/data/state_store.db/mem%3Aindex%3Abm25%3Avectors%3A*

# 3. 重启服务器
# Windows 注意：必须用 pty=true，否则 "stdin is not a tty"
terminal(command='node dist/cli.mjs', background=true, pty=true)

# 4. 验证
memory_save  # 测试新模型是否正常工作
```

⚠️ **维度变化必须删索引**：Qwen3-Embedding-8B(4096) → bge-m3(1024) 等。

## Step 4：保存合并后的记忆
使用 `memory_save` 保存当前正确状态：
```
content: "最新配置/工作流/铁律"
type: "workflow|preference|architecture|..."
concepts: "tag1,tag2,..."
```

## Step 5：验证
```
memory_recall(query="关键词", limit=3)
```
确认只返回最新版本。

## 记忆整理原则
- MEMORY（系统提示词）：环境事实+项目约定+工具配置
- USER PROFILE：用户信息+偏好
- SKILL.md：工作流细节+铁律
- AgentMemory：跨会话经验+踩坑+项目架构
- 目标：MEMORY ≤50% 使用率

## 实战案例：2026-06-19 整理

**清理了 14 条过时记忆**：
- 旧工作流版本 v4.10.0 ~ v6.0.2（7条）
- Seedream/Gemini/Kimi WebBridge 旧配置（4条）
- 旧 MCP 配置信息（2条）
- 旧配图铁律（1条）

**识别过时记忆的方法**：
1. 搜索旧版本号：`memory_smart_search(query="v4 v5 v6")`
2. 搜索废弃 provider：`memory_smart_search(query="Seedream SiliconFlow")`
3. 检查 MEMORY 中的版本号和 provider 名字
4. 对比当前正确配置

**更新了 3 条记忆**：
- Hermes 配置路径铁律（AppData/Local/hermes）
- 文生图配置（DashScope 唯一，不设 fallback）
- 公众号工作流 v7.1.0

**注意：** REST API 的 `forget` 仅影响当前运行实例内存，**不会持久化到 standalone.json**。服务器重启后会恢复旧数据。因此清理必须直接编辑文件 + 重启。