# Project Scope Migration

When `memory_diagnose` reports memories without `project` scope (FAIL on `memory-project-coverage`).

## Problem

- `POST /agentmemory/migrate {"step":"infer-memory-projects"}` returns `"ambiguous": N, "updated": 0`
- Old memories created before project scope was required have `project: null`
- The MCP `memory_save` tool's `project` parameter may not be passed through in all versions

## Solution

### Step 1: Re-save each memory with project scope via REST API

```bash
# For each memory without project, POST to /remember with project field
curl -s -X POST http://localhost:3111/agentmemory/remember \
  -H "Content-Type: application/json" \
  -d @payload.json
```

payload.json:
```json
{
  "content": "original memory content here",
  "project": "global",
  "type": "fact"
}
```

**Windows shell escaping**: If content contains backslashes (file paths), MUST use `@file` pattern. Bash will eat `\` characters in inline `-d '...'` strings.

### Step 2: Delete old unscoped memories

Two options (both work):

**Option A — REST API (simpler for batch):**
```bash
curl -s -X POST http://localhost:3111/agentmemory/forget \
  -H "Content-Type: application/json" \
  -d '{"memoryId":"mem_xxx"}'
```

**Option B — MCP tool (for interactive use):**
```
memory_governance_delete(memoryIds="id1,id2,id3", reason="replaced with project-scoped versions")
```

⚠️ `DELETE /memories/:id` does NOT work. Use `POST /forget` or MCP `governance_delete`.

### Step 3: Deduplicate

Check for duplicate memories (same title/content) and delete older versions.

### Step 4: Verify

```
memory_diagnose()
```

The `memory-project-coverage` check should now show PASS.

## Automation Script Pattern

Use `subprocess.run` instead of `hermes_tools.terminal` — the latter mixes rtk warnings into stdout, breaking JSON parsing.

```python
import json, os, subprocess
from hermes_tools import write_file

# Get all memories
result = subprocess.run(['curl', '-s', 'http://localhost:3111/agentmemory/memories?limit=100'],
                       capture_output=True, text=True)
lines = result.stdout.strip().split('\n')
json_line = [l for l in lines if l.startswith('{')][-1]  # skip rtk warnings
memories = json.loads(json_line)['memories']

for m in memories:
    if not m.get('project'):
        # Write payload to file (avoids Windows shell escaping)
        payload = {'content': m['content'], 'project': 'your-project', 'type': m['type']}
        write_file('/tmp/payload.json', json.dumps(payload, ensure_ascii=False))

        # Re-save with project
        subprocess.run(['curl', '-s', '-X', 'POST', 'http://localhost:3111/agentmemory/remember',
                        '-H', 'Content-Type: application/json', '-d', '@/tmp/payload.json'],
                       capture_output=True)

        # Delete old version via REST
        subprocess.run(['curl', '-s', '-X', 'POST', 'http://localhost:3111/agentmemory/forget',
                        '-H', 'Content-Type: application/json',
                        '-d', json.dumps({'memoryId': m['id']})],
                       capture_output=True)
```

### Project Classification Map

For batch migration, classify memories by content keywords:

| Project | Keywords |
|---------|----------|
| `environment` | Windows, Git Bash, MSYS, python3, Hermes Home, GBK |
| `agentmemory` | AgentMemory, agentmemory, MEMORY.md, memory_save |
| `wechat-official` | 公众号, 微信公众号, 图灵的脑洞, content-pipeline |
| `wrong-question-notebook` | WQN, 错题本, Wrong-Question, wqn-desktop |
| `image-generation` | 生图, xiaohei-image, ian-xiaohei, 配图 |
| `test` | 测试记忆, 已删除测试记忆 |
