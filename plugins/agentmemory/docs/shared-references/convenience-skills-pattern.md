# AgentMemory Convenience Skills Organization Pattern

## Overview

AgentMemory ships with 8 official convenience skills that provide quick access to common operations without manually calling MCP tools. These should be organized under `convenience-skills/` in the agentmemory skill directory.

## Skills Inventory

### Memory Operations
| Skill | Trigger Words | MCP Tool Used |
|-------|---------------|---------------|
| **recall** | "recall", "remember", "what did we do" | `memory_smart_search` |
| **remember** | "remember this", "save insight" | `memory_save` |
| **forget** | "forget this", "delete memory" | `memory_governance_delete` |
| **handoff** | "handoff", "resume", "where were we" | `memory_sessions` |

### Session Management
| Skill | Trigger Words | MCP Tool Used |
|-------|---------------|---------------|
| **session-history** | "session history", "past sessions" | `memory_sessions` |
| **recap** | "recap", "this week", "today" | `memory_sessions` + `memory_recall` |
| **commit-context** | "why is this code here" | `memory_commit_lookup` |
| **commit-history** | "show agent commits" | `memory_commits` |

## Installation Location

```
~/AppData/Local/hermes/skills/autonomous-ai-agents/agentmemory/convenience-skills/
├── commit-context/SKILL.md
├── commit-history/SKILL.md
├── forget/SKILL.md
├── handoff/SKILL.md
├── recall/SKILL.md
├── recap/SKILL.md
├── remember/SKILL.md
└── session-history/SKILL.md
```

## Source Location

Original skills are in `~/.agents/skills/` (installed by agentmemory plugin).

## Integration Notes

- These skills require agentmemory MCP server to be configured in `~/.hermes/config.yaml`
- They are **user-invocable** (can be called directly by user)
- They use `argument-hint` for parameter guidance
- If MCP tools fail, skills provide troubleshooting steps

## Darwin Skill Optimization Insights

When optimizing agentmemory with darwin-skill, the following patterns improved scores:

1. **Quick Start Guide (TL;DR)** - Added 30-second setup guide at top
2. **Decision Tree** - "When to use what tool" flowchart
3. **Common Scenarios Table** - 6 frequent use cases with parameter examples
4. **User Checkpoints** - 3 verification points during configuration
5. **High-Frequency Operations** - 4 copy-paste ready commands

These patterns improved workflow clarity from 13/15 to 15/15.
