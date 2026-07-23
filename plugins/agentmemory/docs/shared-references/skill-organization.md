# AgentMemory Skill Organization Best Practices

> Guide for organizing skills and best practices for using agentmemory effectively.

## Table of Contents

1. [Skill Structure](#skill-structure)
2. [Memory Patterns](#memory-patterns)
3. [Integration Patterns](#integration-patterns)
4. [Performance Optimization](#performance-optimization)
5. [Team Collaboration](#team-collaboration)
6. [Advanced Patterns](#advanced-patterns)

---

## 1. Skill Structure

### Recommended Directory Layout

```
~/.hermes/skills/
├── agent-memory/
│   ├── SKILL.md                 # Main skill documentation
│   ├── references/
│   │   ├── troubleshooting-detailed.md
│   │   ├── env-variables-full.md
│   │   └── skill-organization.md
│   └── examples/
│       ├── basic-usage.md
│       └── advanced-usage.md
```

### Skill File Best Practices

| File | Purpose | Lines |
|------|---------|-------|
| `SKILL.md` | Quick reference, core commands | <800 |
| `references/*.md` | Detailed documentation | Any |
| `examples/*.md` | Usage examples | Any |

### Naming Conventions

- Use lowercase with hyphens for directory names
- Keep file names descriptive but concise
- Group related files in subdirectories

---

## 2. Memory Patterns

### When to Save Memories

| Type | When to Save | Example |
|------|--------------|---------|
| `pattern` | Repeated behavior identified | "User prefers dark mode" |
| `preference` | User preference expressed | "Always use tabs, not spaces" |
| `architecture` | Design decision made | "Using microservices for this module" |
| `bug` | Bug discovered and fixed | "Race condition in auth module" |
| `workflow` | Process established | "Deploy flow: test → stage → prod" |
| `fact` | Important information | "API key stored in ~/.env" |

### Memory Quality Guidelines

1. **Be specific**: "Uses Python 3.11 with type hints" not "Uses Python"
2. **Include context**: "When refactoring auth, always update tests first"
3. **Add timestamps**: Let agentmemory handle this automatically
4. **Use concepts**: Tag with relevant concepts for better search

### Memory Lifecycle

```
Save → Index → Search → Recall → Decay → Forget
  ↑                              ↓
  └──────────────────────────────┘
        (re-save if still relevant)
```

---

## 3. Integration Patterns

### Basic Integration

```python
# Simple memory recall before coding
def before_coding(task):
    memories = memory_recall(f"how to implement {task}")
    context = "\n".join([m['narrative'] for m in memories])
    return f"Based on past experience:\n{context}"
```

### Advanced Integration

```python
# Session-aware memory with project context
def session_start(session_id, project):
    # Initialize with project context
    memory_save(
        content=f"Starting work on {project}",
        type="workflow",
        concepts=[project, "session-start"]
    )
    
    # Prefetch relevant memories
    context = prefetch(f"project {project} recent decisions")
    return context
```

### Cross-Agent Pattern

```yaml
# Shared memory server configuration
# All agents connect to same server
mcp_servers:
  agentmemory:
    command: npx
    args: ["-y", "@agentmemory/mcp"]
    env:
      AGENTMEMORY_URL: http://shared-memory:3111
      AGENTMEMORY_PROJECT: shared-project
```

---

## 4. Performance Optimization

### Query Optimization

| Technique | Before | After |
|-----------|--------|-------|
| Specific queries | "code" | "Python async decorator pattern" |
| Limit results | `limit: 100` | `limit: 5` |
| Use concepts | free text | `concepts: ["python", "async"]` |
| Cache frequent | API calls | local cache |

### Memory Management

```bash
# Regular cleanup
curl -X POST http://localhost:3111/agentmemory/session/end \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "old-session-id"}'

# Monitor memory usage
curl http://localhost:3111/agentmemory/sessions | \
  jq '.sessions | length'
```

### Index Optimization

```bash
# Rebuild indexes periodically
npx @agentmemory/agentmemory reindex

# Check index size
ls -lh ~/.agentmemory/data/index/

# Monitor search performance
time curl -X POST http://localhost:3111/agentmemory/smart-search \
  -d '{"query":"test","limit":5}'
```

---

## 5. Team Collaboration

### Shared Memory Setup

1. **Central server**: Deploy agentmemory server accessible to all team members
2. **Project naming**: Use consistent project names across team
3. **Access control**: Configure AUTH_SECRET for production
4. **Documentation**: Share SKILL.md with team

### Conflict Resolution

| Scenario | Solution |
|----------|----------|
| Same memory, different versions | Use memory versioning |
| Conflicting preferences | Use user-specific tags |
| Different project contexts | Use project-scoped queries |

### Communication Patterns

```python
# Share decision with team
memory_save(
    content="Decided to use PostgreSQL for user data",
    type="architecture",
    concepts=["database", "decision", "team-shared"]
)

# Search team decisions
memories = memory_search("team database decisions")
```

---

## 6. Advanced Patterns

### Memory Composition

```python
# Combine multiple memories into context
def build_context(topic):
    memories = memory_search(topic, limit=10)
    
    context_parts = []
    for mem in memories:
        context_parts.append(f"- {mem['title']}: {mem['narrative'][:200]}")
    
    return "\n".join(context_parts)
```

### Conditional Memory

```python
# Save memory only if not already exists
def save_if_new(content, type, concepts):
    existing = memory_search(content, limit=1)
    
    if not existing['results']:
        memory_save(
            content=content,
            type=type,
            concepts=concepts
        )
        return True
    return False
```

### Memory Chains

```python
# Chain related memories
def chain_memories(start_topic, depth=3):
    current = start_topic
    chain = []
    
    for _ in range(depth):
        memories = memory_search(current, limit=1)
        if memories['results']:
            chain.append(memories['results'][0])
            current = memories['results'][0]['title']
        else:
            break
    
    return chain
```

### Memory Analytics

```python
# Analyze memory patterns
def analyze_patterns(project):
    sessions = memory_sessions()
    
    project_sessions = [
        s for s in sessions 
        if s.get('project') == project
    ]
    
    return {
        'total_sessions': len(project_sessions),
        'avg_observations': sum(
            s.get('observationCount', 0) 
            for s in project_sessions
        ) / len(project_sessions) if project_sessions else 0
    }
```

---

## 7. Common Pitfalls

### Don'ts

1. **Don't save every message**: Only save important insights
2. **Don't use vague queries**: Be specific in searches
3. **Don't ignore session cleanup**: End sessions when done
4. **Don't hardcode credentials**: Use environment variables

### Do's

1. **Do use concepts**: Tag memories for better search
2. **Do review periodically**: Clean up irrelevant memories
3. **Do document decisions**: Save architecture decisions
4. **Do share with team**: Use cross-agent features

---

## 8. Examples

### Example: Feature Development

```python
# 1. Start session
memory_save(
    content="Starting user authentication feature",
    type="workflow",
    concepts=["auth", "feature-dev"]
)

# 2. Research existing patterns
existing = memory_search("authentication patterns")

# 3. Save decision
memory_save(
    content="Using JWT tokens for auth (24h expiry)",
    type="architecture",
    concepts=["auth", "jwt", "security"]
)

# 4. Save implementation notes
memory_save(
    content="Auth middleware must check token before /api/* routes",
    type="pattern",
    concepts=["auth", "middleware", "express"]
)

# 5. End session
# (handled automatically by on_session_end hook)
```

### Example: Bug Fix

```python
# 1. Save bug discovery
memory_save(
    content="Race condition in user creation: two users with same email",
    type="bug",
    concepts=["race-condition", "user-creation", "email"]
)

# 2. Save fix
memory_save(
    content="Added unique constraint on email column + retry logic",
    type="workflow",
    concepts=["race-condition", "fix", "database"]
)

# 3. Save prevention
memory_save(
    content="Always add unique constraints for natural keys",
    type="pattern",
    concepts=["database", "best-practice", "prevention"]
)
```

---

## 9. Checklist

### Before Starting Work

- [ ] Check for relevant past memories
- [ ] Review project context
- [ ] Understand existing patterns

### During Work

- [ ] Save important decisions
- [ ] Document new patterns
- [ ] Tag with relevant concepts

### After Work

- [ ] Save final implementation notes
- [ ] Update relevant memories
- [ ] End session properly

---

**Version**: 0.8.0 | **Last Updated**: 2026-01-15
