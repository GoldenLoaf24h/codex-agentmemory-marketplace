# AgentMemory Troubleshooting Guide

> Detailed troubleshooting for agentmemory plugin and server issues.

## Table of Contents

1. [Server Issues](#server-issues)
2. [Plugin Issues](#plugin-issues)
3. [Connection Issues](#connection-issues)
4. [Authentication Issues](#authentication-issues)
5. [Performance Issues](#performance-issues)
6. [Cross-Agent Issues](#cross-agent-issues)
7. [Data Issues](#data-issues)
8. [Configuration Issues](#configuration-issues)

---

## 1. Server Issues

### Server won't start

**Symptoms**: `npx @agentmemory/agentmemory` fails or exits immediately.

**Diagnosis**:
```bash
# Check if port 3111 is in use
lsof -i :3111
# or on Windows
netstat -ano | findstr :3111

# Check for errors
npx @agentmemory/agentmemory 2>&1 | head -20
```

**Solutions**:
1. Kill existing process: `kill $(lsof -t -i:3111)`
2. Use different port: `PORT=3112 npx @agentmemory/agentmemory`
3. Check Node.js version: `node --version` (requires 18+)
4. Clear npm cache: `npm cache clean --force`

### Server crashes on startup

**Symptoms**: Server starts then immediately exits.

**Diagnosis**:
```bash
# Check logs
tail -f ~/.agentmemory/logs/server.log

# Check disk space
df -h ~/.agentmemory/

# Check database
ls -la ~/.agentmemory/data/
```

**Solutions**:
1. Ensure sufficient disk space (>100MB free)
2. Check database permissions
3. Remove corrupted database: `rm ~/.agentmemory/data/*.db`
4. Reinstall: `npm install -g @agentmemory/agentmemory`

---

## 2. Plugin Issues

### Plugin not loading

**Symptoms**: `hermes memory status` shows "Missing" or "Not Available".

**Diagnosis**:
```bash
# Check plugin directory
ls -la ~/.hermes/plugins/agentmemory/

# Check plugin.yaml
cat ~/.hermes/plugins/agentmemory/plugin.yaml

# Check Hermes logs
tail -f ~/.hermes/logs/hermes.log | grep agentmemory
```

**Solutions**:
1. Verify plugin exists: `ls ~/.hermes/plugins/agentmemory/__init__.py`
2. Check Python syntax: `python3 -c "import ast; ast.parse(open('__init__.py').read())"`
3. Reinstall plugin: Copy fresh copy from agentmemory repo
4. Check Hermes version compatibility

### Plugin imports fail

**Symptoms**: `ImportError` or `ModuleNotFoundError` in logs.

**Diagnosis**:
```bash
# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Check if memory_provider is available
python3 -c "from agent.memory_provider import MemoryProvider; print('OK')"
```

**Solutions**:
1. Install dependencies: `pip install agentmemory`
2. Check virtual environment activation
3. Use standalone version (no external imports needed)

---

## 3. Connection Issues

### Cannot connect to server

**Symptoms**: `curl localhost:3111/agentmemory/health` fails.

**Diagnosis**:
```bash
# Test connection
curl -v http://localhost:3111/agentmemory/health

# Check if server is running
ps aux | grep agentmemory

# Check firewall
iptables -L -n | grep 3111
```

**Solutions**:
1. Verify server is running
2. Check port configuration
3. Try different host: `0.0.0.0` vs `localhost`
4. Check firewall rules

### Connection timeout

**Symptoms**: Requests hang or timeout after 5 seconds.

**Diagnosis**:
```bash
# Test with longer timeout
curl --connect-timeout 10 http://localhost:3111/agentmemory/health

# Check network latency
ping localhost

# Check if server is overloaded
top -p $(pgrep -f agentmemory)
```

**Solutions**:
1. Increase timeout in plugin (modify `_api` function)
2. Check server load
3. Reduce concurrent requests
4. Use local connection (avoid network)

---

## 4. Authentication Issues

### Auth token rejected

**Symptoms**: 401 Unauthorized errors.

**Diagnosis**:
```bash
# Check token
echo $AGENTMEMORY_SECRET

# Test with token
curl -H "Authorization: Bearer $AGENTMEMORY_SECRET" \
  http://localhost:3111/agentmemory/health

# Check server config
cat ~/.agentmemory/.env | grep SECRET
```

**Solutions**:
1. Verify token matches server config
2. Regenerate token if needed
3. Check for whitespace in token
4. Ensure HTTPS for remote servers

### Plaintext HTTP warning

**Symptoms**: Warning about sending bearer token over plaintext HTTP.

**Diagnosis**:
```bash
# Check URL scheme
echo $AGENTMEMORY_URL

# Check if HTTPS is required
echo $AGENTMEMORY_REQUIRE_HTTPS
```

**Solutions**:
1. Use HTTPS: `AGENTMEMORY_URL=https://your-server.com:3111`
2. Set up SSH tunnel: `ssh -L 3111:localhost:3111 remote-server`
3. Use localhost (loopback is safe)
4. Acknowledge warning if intentional

---

## 5. Performance Issues

### Slow search queries

**Symptoms**: Search takes >2 seconds.

**Diagnosis**:
```bash
# Test search time
time curl -X POST http://localhost:3111/agentmemory/smart-search \
  -H "Content-Type: application/json" \
  -d '{"query":"test","limit":5}'

# Check index size
ls -lh ~/.agentmemory/data/*.idx

# Check memory usage
ps aux | grep agentmemory | awk '{print $6/1024 " MB"}'
```

**Solutions**:
1. Reduce `limit` parameter
2. Use more specific queries
3. Rebuild indexes: `npx @agentmemory/agentmemory reindex`
4. Increase server resources

### High memory usage

**Symptoms**: Server consumes >1GB RAM.

**Diagnosis**:
```bash
# Monitor memory
watch -n 5 "ps aux | grep agentmemory"

# Check session count
curl http://localhost:3111/agentmemory/sessions | jq '.sessions | length'
```

**Solutions**:
1. End old sessions: `on_session_end` hook
2. Restart server periodically
3. Configure auto-forget
4. Limit concurrent sessions

---

## 6. Cross-Agent Issues

### Memories not shared

**Symptoms**: Claude Code can't see Hermes memories.

**Diagnosis**:
```bash
# Check MCP server
curl http://localhost:3111/agentmemory/sessions

# Verify project name
echo $AGENTMEMORY_PROJECT

# Check cross-agent config
cat ~/.agentmemory/config.json | jq '.crossAgent'
```

**Solutions**:
1. Ensure same server URL in all agents
2. Verify project name matches
3. Check MCP server accessibility
4. Restart all agents after config change

### Different project contexts

**Symptoms**: Agents see different memories for same project.

**Diagnosis**:
```bash
# Check project names
curl http://localhost:3111/agentmemory/sessions | jq '.[].project'

# Verify working directory
pwd
```

**Solutions**:
1. Use consistent project names
2. Set `AGENTMEMORY_PROJECT` explicitly
3. Configure project aliases
4. Use absolute paths in config

---

## 7. Data Issues

### Missing observations

**Symptoms**: Past observations not appearing in search.

**Diagnosis**:
```bash
# Check observation count
curl http://localhost:3111/agentmemory/sessions | jq '.[].observationCount'

# Search with different terms
curl -X POST http://localhost:3111/agentmemory/search \
  -H "Content-Type: application/json" \
  -d '{"query":"your-term","limit":10}'
```

**Solutions**:
1. Check observation timestamps
2. Verify search terms match content
3. Rebuild search index
4. Check for data corruption

### Corrupted database

**Symptoms**: Database errors or crashes.

**Diagnosis**:
```bash
# Check database integrity
sqlite3 ~/.agentmemory/data/memory.db "PRAGMA integrity_check;"

# Check file permissions
ls -la ~/.agentmemory/data/
```

**Solutions**:
1. Backup database: `cp memory.db memory.db.backup`
2. Repair database: `sqlite3 memory.db ".recover" | sqlite3 memory_new.db`
3. Restore from backup
4. Reinstall and re-import data

---

## 8. Configuration Issues

### Config file not found

**Symptoms**: `~/.agentmemory/.env` missing.

**Diagnosis**:
```bash
# Check file exists
ls -la ~/.agentmemory/.env

# Check permissions
stat ~/.agentmemory/.env
```

**Solutions**:
1. Create config: `touch ~/.agentmemory/.env`
2. Set permissions: `chmod 600 ~/.agentmemory/.env`
3. Add default values
4. Check XDG config path

### ⚠️ Windows config path mismatch (血泪教训)

**Symptoms**: Changes to `~/.hermes/config.yaml` don't take effect.

**Root cause**: On Windows, `HERMES_HOME = C:\Users\<user>\AppData\Local\hermes`, NOT `~/.hermes/`. The `~/.hermes/` directory is a residual/leftover.

**Diagnosis**:
```bash
echo $HERMES_HOME
# Should show: C:\Users\<user>\AppData\Local\hermes
```

**Solutions**:
1. Always use `$HERMES_HOME/config.yaml` (not `~/.hermes/config.yaml`)
2. Check with `echo $HERMES_HOME` before writing
3. Use `patch()` for incremental changes, never `write_file` to overwrite entire config

### Wrong config values

**Symptoms**: Server uses defaults instead of custom config.

**Diagnosis**:
```bash
# Check loaded config
curl http://localhost:3111/agentmemory/config

# Check environment variables
env | grep AGENTMEMORY
```

**Solutions**:
1. Verify config syntax
2. Restart server after changes
3. Check for typos in variable names
4. Use absolute paths

---

## Quick Reference

| Problem | First Check | Quick Fix |
|---------|-------------|-----------|
| Server won't start | Port 3111 in use | `kill $(lsof -t -i:3111)` |
| Plugin not loading | Plugin directory | `ls ~/.hermes/plugins/agentmemory/` |
| Connection refused | Server running | `curl localhost:3111/agentmemory/health` |
| Auth errors | Token match | `echo $AGENTMEMORY_SECRET` |
| Slow search | Query limits | Reduce `limit` parameter |
| Missing memories | Session active | Check `memory_sessions` |
| Cross-agent issues | Same server URL | Verify MCP config in all agents |
| Data corruption | DB integrity | `sqlite3 memory.db "PRAGMA integrity_check;"` |

---

**Last Updated**: 2026-01-15 | **Version**: 0.8.0
