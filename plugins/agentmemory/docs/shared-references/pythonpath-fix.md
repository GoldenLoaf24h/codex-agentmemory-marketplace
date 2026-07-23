# PYTHONPATH 冲突修复

## 问题

安装 `notebooklm-mcp-cli` 等 uv 工具后，运行时报错：

```
ImportError: cannot import name 'BaseModel' from 'pydantic'
```

**原因：** Hermes 的 venv 被加入 `sys.path` 最前面，导致 uv 安装的独立包解析到了 Hermes 的旧版 pydantic。

## 修复

**临时方案：** 每次运行前清空 PYTHONPATH

```bash
PYTHONPATH="" nlm notebook list
PYTHONPATH="" nlm doctor
```

**永久方案：** 创建 bat 包装脚本

```bat
@echo off
set PYTHONPATH=
nlm %*
```

保存为 `nlm.bat`，放在 PATH 中。

## 影响的工具

- `notebooklm-mcp-cli` (nlm)
- 其他通过 `uv tool install` 安装的 CLI 工具

## 验证

```bash
PYTHONPATH="" nlm doctor
# 应该看到版本号和健康检查结果
```
