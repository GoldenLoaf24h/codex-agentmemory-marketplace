# CodeGraph — 代码知识图谱 for Hermes

> 来源: https://github.com/colbymchenry/codegraph (43k ⭐)
> 描述: 预索引的代码知识图谱，减少 token 消耗和工具调用数，100% 本地

## 安装

```bash
# 1. 安装 CLI（自带 Node 运行时，无需独立装 Node）
npm i -g @colbymchenry/codegraph

# 2. 接入 Hermes（自动修改 ~/.hermes/config.yaml，添加 MCP server）
codegraph install --yes

# 3. 初始化项目（在代码项目目录下运行）
cd your-code-project
codegraph init -i
```

## Hermes 配置

自动写入 `config.yaml`:

```yaml
codegraph:
    command: codegraph
    args:
      - serve
      - --mcp
    timeout: 120
    connect_timeout: 60
    enabled: true
```

重启 Hermes 会话后生效。

## 支持 Agent

Claude Code / Codex CLI / OpenCode / Hermes Agent / Gemini / Cursor / Antigravity / Kiro

## 当前状态 (2026-06-07)

- ✅ 已安装 v0.9.9
- ✅ 已接入 Hermes + Claude Code + Codex CLI
- 🟡 D:\workspace\Hermes\ 和 D:\workspace\vibe\ 无代码文件，未建索引
- 📌 日后打开代码项目时运行 `codegraph init -i` 即可
