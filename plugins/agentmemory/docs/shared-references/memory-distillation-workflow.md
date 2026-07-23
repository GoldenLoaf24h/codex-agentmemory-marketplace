# 记忆精炼总结工作流（Memory Distillation）

## 触发条件

用户说"提取精炼总结"、"整理一下记忆"、"总结一下我知道什么"、"都给我找到"时执行。

## 与"整理记忆"的区别

| 操作 | 目的 | 工具 |
|------|------|------|
| **整理记忆** | 维护操作（诊断→合并→反思→清理） | memory_diagnose → consolidate → reflect |
| **精炼总结** | 分析已有记忆，提取主题和洞察，保存结构化摘要 | REST API 读取 → 分析 → memory_save |

## 执行流程

### Step 1: 获取全量数据

**PREFERRED: 直接读取 standalone.json（唯一可靠数据源）**

```python
import json, os
with open(os.path.expanduser('~/.agentmemory/standalone.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)
memories = data.get('mem:memories', {})
# memories 是 dict，key 是 memory_id，value 是记忆内容
```

**Fallback: REST API（仅用于状态验证，不用于获取记忆列表）**

```python
# ⚠️ REST API /agentmemory/memories 返回格式不稳定（有时 dict 有时 list）
# 只用这些端点做验证：
health = GET /agentmemory/health    # 服务状态
graph = GET /agentmemory/graph/stats  # 图谱统计
```

### Step 2: 按类型分组分析

```python
# 统计记忆类型分布
types = {}
for m in memories:
    t = m['type']
    types[t] = types.get(t, 0) + 1

# 输出：architecture: 14, fact: 11, workflow: 6, pattern: 4, preference: 1
```

### Step 3: 提取高频概念

```python
# 统计概念频率
concepts = {}
for m in memories:
    for c in m.get('concepts', []):
        concepts[c] = concepts.get(c, 0) + 1

# 输出：agentmemory(3), database migration(3), spawn_blocking(3)...
```

### Step 4: 按主题归类

将记忆按内容主题分组：

| 主题 | 判断标准 | 示例 |
|------|----------|------|
| 环境配置 | concepts 含 windows/hermes/环境 | OS、路径、MCP 配置 |
| 开发工具 | concepts 含 officecli/skill/agentmemory | 工具使用方法 |
| 工作流程 | type=workflow | 流水线、操作步骤 |
| 用户偏好 | type=preference | 沟通风格、决策习惯 |
| 技术踩坑 | concepts 含 bug/error/踩坑 | 已知问题和解决方案 |

### Step 5: 保存结构化摘要

```python
memory_save(
    content="""记忆精炼总结（日期）：

## 状态
- 总记忆: N 条
- 知识图谱: X 节点 / Y 边
- 会话数: Z 个

## 类型分布
- architecture: N 条
- fact: N 条
...

## 高频概念
- concept1 (N次), concept2 (N次)...

## 主要主题
1. **主题A** (N条): 摘要
2. **主题B** (N条): 摘要

## 关键洞察
1. 洞察1
2. 洞察2""",
    type="workflow",
    concepts=["记忆整理", "总结", "精炼"]
)
```

## 注意事项

- 摘要本身也是一条记忆，type 用 `workflow`
- concepts 加上"记忆整理""总结"便于后续搜索
- 如果记忆数量 >50，先执行 `memory_consolidate` 合并再分析
- 摘要应精炼，每条洞察一句话，不要复制原始记忆内容
