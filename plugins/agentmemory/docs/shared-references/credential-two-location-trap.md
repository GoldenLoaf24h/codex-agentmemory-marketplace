# 多位置凭证陷阱（credential-two-location-trap）

> 类级经验：任何"同一 API key 写在多处"的集成都适用（exa / 任意 mcp_servers.env + .env）。
> 来源：本会话修复 Exa API key 时踩坑——上一轮只改了 config.yaml 的 key，.env 里另一个旧 key 仍生效，重启后继续 401。

## 陷阱本质

同一凭证可能同时存在于两个独立位置，值是**互相独立**的：

- `config.yaml` → `mcp_servers.<name>.env.<KEY>` （MCP server 读取）
- `.env`（%LOCALAPPDATA%\hermes\.env）→ `<KEY>=<value>` （进程环境读取）

两处谁生效取决于 agent 实际怎么读——常常是**两处都要对**，只改一处另一处仍用旧值。

## 最阴险的子陷阱：前缀相同实际不同

两个位置的旧值可能**前 8 个字符相同但实际不同**：

```
config.yaml : EXA_API_KEY=da97133a-da97-4b77-aab3-57c6676fa5f9
.env        : EXA_API_KEY=da97133a-7e34-4742-ace6-4316429ba5f9   <- 仅前8位 da97133a 相同
```

脱敏显示（只打前 8 位 `da97133a...`）会让你以为"两处是同一个旧 key"，于是只替换 config.yaml 那个，**.env 那个漏了** -> 重启后 .env 的旧 key 生效 -> 继续 `INVALID_API_KEY` 401。

## 正确修复流程

1. **精确比对完整值（不要只看前缀）**
   ```python
   import yaml
   d = yaml.safe_load(open(r"C:\Users\Lenovo\AppData\Local\hermes\config.yaml", encoding="utf-8"))
   print(d["mcp_servers"]["exa"]["env"]["EXA_API_KEY"])
   # .env：用 split("=") 取完整值，别用正则 $ 匹配（CRLF 会让 $ 失效）
   for l in open(r"C:\Users\Lenovo\AppData\Local\hermes\.env", encoding="utf-8"):
       if l.startswith("EXA_API_KEY="):
           print(l.split("=",1)[1].strip())
   ```
2. **两处都换成新 key**（脚本替换，避免手误）。
3. **直连后端 API 验证**（关键，不能只说"重启就好"）：
   ```bash
   KEY=<新key>
   curl -s --max-time 25 -X POST "https://api.exa.ai/search" \
     -H "x-api-key: $KEY" \
     -H "Content-Type: application/json" \
     -d '{"query":"test","numResults":3}'
   # 应返回 results 数组；若出现 {"error":"Invalid API key","tag":"INVALID_API_KEY"} = key 仍失效
   ```
4. **重启 gateway 重载 MCP 环境**：`/restart` 或网关外 `hermes gateway restart`。常驻 MCP 进程启动时读旧环境，不重启仍用旧 key。

## 判据

- 改完 -> 直连 API 返回真实 results（非 error）= 后端 key 有效
- 但 Hermes MCP 工具仍 401 -> 一定是 gateway 没重启（缓存旧环境）
- 两处旧值前缀相同时，**务必用脚本比对完整 36 位 UUID**，不要信脱敏显示
