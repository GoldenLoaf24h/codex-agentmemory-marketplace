# AgentMemory Environment Variables — Full Reference

> Complete list of environment variables for agentmemory server and plugin.

## Table of Contents

1. [Server Variables](#server-variables)
2. [Plugin Variables](#plugin-variables)
3. [Hermes Variables](#hermes-variables)
4. [Configuration Files](#configuration-files)
5. [Variable Precedence](#variable-precedence)

---

## 1. Server Variables

### Core Server

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `PORT` | `3111` | HTTP server port | `PORT=3112` |
| `HOST` | `0.0.0.0` | Bind address | `HOST=localhost` |
| `NODE_ENV` | `development` | Environment mode | `NODE_ENV=production` |
| `LOG_LEVEL` | `info` | Logging verbosity | `LOG_LEVEL=debug` |

### Database

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `DB_PATH` | `~/.agentmemory/data/memory.db` | SQLite database path | `DB_PATH=/data/memory.db` |
| `DB_BACKUP_PATH` | `~/.agentmemory/backups/` | Backup directory | `DB_BACKUP_PATH=/backups/` |
| `DB_MAX_SIZE` | `1GB` | Maximum database size | `DB_MAX_SIZE=500MB` |

### Search

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `SEARCH_INDEX_PATH` | `~/.agentmemory/data/index/` | Search index directory | `SEARCH_INDEX_PATH=/data/index/` |
| `BM25_K1` | `1.2` | BM25 parameter k1 | `BM25_K1=1.5` |
| `BM25_B` | `0.75` | BM25 parameter b | `BM25_B=0.8` |
| `VECTOR_DIMENSION` | `384` | Embedding vector dimension | `VECTOR_DIMENSION=768` |

### Memory Management

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `MEMORY_DECAY_RATE` | `0.1` | Memory decay rate per day | `MEMORY_DECAY_RATE=0.05` |
| `MEMORY_FORGET_THRESHOLD` | `0.1` | Minimum importance to keep | `MEMORY_FORGET_THRESHOLD=0.2` |
| `MEMORY_MAX_OBSERVATIONS` | `100000` | Max observations per project | `MEMORY_MAX_OBSERVATIONS=50000` |

### Security

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `AUTH_SECRET` | (none) | JWT secret for API auth | `AUTH_SECRET=your-secret-key` |
| `CORS_ORIGIN` | `*` | Allowed CORS origins | `CORS_ORIGIN=http://localhost:3000` |
| `RATE_LIMIT_MAX` | `100` | Max requests per window | `RATE_LIMIT_MAX=50` |
| `RATE_LIMIT_WINDOW` | `60000` | Rate limit window (ms) | `RATE_LIMIT_WINDOW=30000` |

### Logging

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `LOG_FILE` | `~/.agentmemory/logs/server.log` | Log file path | `LOG_FILE=/var/log/agentmemory.log` |
| `LOG_ROTATE_SIZE` | `10MB` | Log rotation size | `LOG_ROTATE_SIZE=5MB` |
| `LOG_ROTATE_COUNT` | `5` | Number of rotated logs | `LOG_ROTATE_COUNT=10` |

---

## 2. Plugin Variables

### Connection

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `AGENTMEMORY_URL` | `http://localhost:3111` | Server URL | `AGENTMEMORY_URL=https://memory.example.com` |
| `AGENTMEMORY_SECRET` | (none) | Auth token for server | `AGENTMEMORY_SECRET=abc123` |
| `AGENTMEMORY_REQUIRE_HTTPS` | (off) | Force HTTPS for auth | `AGENTMEMORY_REQUIRE_HTTPS=1` |
| `AGENTMEMORY_TIMEOUT` | `5000` | Request timeout (ms) | `AGENTMEMORY_TIMEOUT=10000` |

### Session

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `AGENTMEMORY_PROJECT` | (cwd) | Project identifier | `AGENTMEMORY_PROJECT=my-app` |
| `AGENTMEMORY_SESSION_PREFIX` | `session-` | Session ID prefix | `AGENTMEMORY_SESSION_PREFIX=hermes-` |

### Behavior

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `AGENTMEMORY_AUTO_SAVE` | `true` | Auto-save observations | `AGENTMEMORY_AUTO_SAVE=false` |
| `AGENTMEMORY_PREFETCH_LIMIT` | `5` | Max prefetch results | `AGENTMEMORY_PREFETCH_LIMIT=10` |
| `AGENTMEMORY_SYNC_TURNS` | `true` | Sync conversation turns | `AGENTMEMORY_SYNC_TURNS=false` |

---

## 3. Hermes Variables

### Memory Provider

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `HERMES_MEMORY_PROVIDER` | `builtin` | Memory provider choice | `HERMES_MEMORY_PROVIDER=agentmemory` |
| `HERMES_MEMORY_DEBUG` | `false` | Debug memory operations | `HERMES_MEMORY_DEBUG=true` |

### Session

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `HERMES_SESSION_ID` | (auto) | Current session ID | `HERMES_SESSION_ID=abc123` |
| `HERMES_WORKING_DIR` | (cwd) | Working directory | `HERMES_WORKING_DIR=/project` |

---

## 4. Configuration Files

### ~/.agentmemory/.env

Primary configuration file for agentmemory server.

```bash
# Server
PORT=3111
HOST=0.0.0.0
NODE_ENV=production

# Database
DB_PATH=~/.agentmemory/data/memory.db

# Security
AUTH_SECRET=your-secret-key-here

# Search
SEARCH_INDEX_PATH=~/.agentmemory/data/index/
```

### ~/.hermes/config.yaml

Hermes configuration for memory provider.

```yaml
# Memory provider
memory:
  provider: agentmemory

# MCP server
mcp_servers:
  agentmemory:
    command: npx
    args: ["-y", "@agentmemory/mcp"]
```

### ~/.hermes/plugins/agentmemory/plugin.yaml

Plugin configuration.

```yaml
name: agentmemory
version: 0.8.0
description: "Persistent cross-session memory for Hermes Agent"
author: "Rohit Ghumare"
hooks:
  - prefetch
  - sync_turn
  - on_session_end
  - on_pre_compress
  - on_memory_write
  - system_prompt_block
```

---

## 5. Variable Precedence

Variables are loaded in this order (later overrides earlier):

1. **Hardcoded defaults** in plugin/server code
2. **Configuration files** (`~/.agentmemory/.env`, `~/.hermes/config.yaml`)
3. **Environment variables** (shell exports)
4. **Command-line arguments** (highest priority)

### Loading Process

```python
# Pseudo-code for variable loading
def load_config():
    # 1. Start with defaults
    config = DEFAULTS.copy()
    
    # 2. Load from .env file
    config.update(load_dotenv('~/.agentmemory/.env'))
    
    # 3. Override with environment variables
    for key in config:
        if key in os.environ:
            config[key] = os.environ[key]
    
    # 4. Command-line args (if any)
    config.update(parse_args())
    
    return config
```

### Best Practices

1. **Use .env for secrets**: Never commit secrets to git
2. **Shell exports for development**: Quick overrides during testing
3. **Config files for production**: Persistent settings
4. **Command-line for debugging**: One-time overrides

---

## 6. Variable Reference by Use Case

### Local Development

```bash
# Minimal config
export AGENTMEMORY_URL=http://localhost:3111
export AGENTMEMORY_PROJECT=my-dev-project
```

### Production Server

```bash
# Secure config
export AGENTMEMORY_URL=https://memory.prod.com:3111
export AGENTMEMORY_SECRET=your-production-secret
export AGENTMEMORY_REQUIRE_HTTPS=1
export AGENTMEMORY_PROJECT=production
```

### Cross-Agent Setup

```bash
# Shared server
export AGENTMEMORY_URL=http://shared-memory.internal:3111
export AGENTMEMORY_SECRET=shared-secret-key
export AGENTMEMORY_PROJECT=cross-agent-project
```

### High-Volume Setup

```bash
# Optimized config
export AGENTMEMORY_TIMEOUT=10000
export AGENTMEMORY_PREFETCH_LIMIT=20
export AGENTMEMORY_AUTO_SAVE=true
```

---

## 7. Troubleshooting Variables

### Debug Mode

```bash
# Enable debug logging
export AGENTMEMORY_DEBUG=true
export LOG_LEVEL=debug

# Check loaded config
curl http://localhost:3111/agentmemory/config
```

### Common Issues

| Issue | Variable to Check | Solution |
|-------|-------------------|----------|
| Connection refused | `AGENTMEMORY_URL` | Verify server URL |
| Auth errors | `AGENTMEMORY_SECRET` | Match server config |
| Slow performance | `AGENTMEMORY_TIMEOUT` | Increase timeout |
| Missing data | `AGENTMEMORY_PROJECT` | Verify project name |
| Memory leaks | `MEMORY_DECAY_RATE` | Adjust decay rate |

### Validation Commands

```bash
# Check all AGENTMEMORY_* variables
env | grep AGENTMEMORY

# Validate URL format
echo $AGENTMEMORY_URL | grep -E '^https?://'

# Test connection
curl -s $AGENTMEMORY_URL/agentmemory/health | jq .

# Check plugin status
hermes memory status
```

---

**Version**: 0.8.0 | **Last Updated**: 2026-01-15
