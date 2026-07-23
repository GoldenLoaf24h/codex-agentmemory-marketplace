# AgentMemory Cronjob 保活模式

## 问题

AgentMemory REST 后端不会随 Hermes 自动启动，且重启 Hermes 后需要手动拉起。

## 方案对比

| 方案 | 复杂度 | 可靠性 | 资源占用 |
|------|:---:|:---:|:---:|
| bat + 桌面快捷方式（连携启动） | 中 | ✅ | 按需 |
| **cronjob 保活** 🆕 | 低 | ✅✅ | 6 小时检查一次 |
| Windows 服务 | 高 | ✅✅✅ | 常驻 |

## Cronjob 保活（推荐）

用 Hermes 内置 cron 系统，每 N 小时检查 AgentMemory 是否存活，挂了就拉起来。

### 创建命令

在 Hermes 对话中：

```
创建 cronjob：每 6 小时检查 AgentMemory 是否在运行。
先用 curl -s http://localhost:3111/health 检查。
如果已运行（exit code 0），什么都不做，报告"AgentMemory 已在运行"。
如果未运行，用 terminal(background=true, workdir=C:\Users\Lenovo) 启动 npx @agentmemory/agentmemory，等 3 秒后验证。
```

### 工作原理

```
cronjob 触发（每 N 小时）
  ↓
curl health check
  ├── 200 → "已在运行"，跳过
  └── 连接失败 → 启动 AgentMemory → 验证 → 报告
```

### 关键设计原则

1. **幂等**：先 `curl` 检查再决定是否启动，避免重复
2. **非阻塞**：`background=true` 启动，不占 cron 会话
3. **自动恢复**：即使 AgentMemory 崩溃，最迟 N 小时自动恢复

### 验证

```bash
# 查看 cronjob 状态
hermes cron list

# 手动触发测试
hermes cron run <job_id>

# 确认 AgentMemory 响应
curl -s http://localhost:3111/health
```

### 调度建议

| 频率 | 适用场景 |
|------|---------|
| 每小时 | 高可用需求 |
| 每 6 小时 | 日常使用（推荐） |
| 每天 | 低频使用 |
