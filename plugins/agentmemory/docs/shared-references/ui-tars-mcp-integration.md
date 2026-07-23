# Windows 视觉兜底说明

uitars-mcp 已从系统中删除。当前视觉兜底由以下两个能力承担：

- **Windows-MCP**：标准 Windows 应用/网页的首选，基于 UIAutomation，不消耗 vision token。
- **Hermes native computer_use**：跨平台 + 视觉兜底，用于标准 UIA 无法识别的复杂 GUI、游戏、老软件。

如需处理无标准控件的界面，直接启用 `computer_use` 的 vision 模式即可，不需要额外部署独立视觉 MCP 服务。
