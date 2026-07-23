# AgentMemory Model Configuration (本机配置)

> 最后更新：2026-06-22

## LLM（压缩/摘要/反思/聊天）
| 配置项 | 值 |
|--------|-----|
| Provider | SiliconFlow |
| 模型 | `Qwen/Qwen3-8B` |
| API地址 | `https://api.siliconflow.cn` |
| 超时 | 180秒 |

## Embedding（向量搜索）
| 配置项 | 值 |
|--------|-----|
| 模型 | `BAAI/bge-m3` |
| 维度 | 1024 |
| Provider | SiliconFlow |

## 搜索权重（三路混合）
| 路径 | 权重 |
|------|------|
| BM25（关键词） | 0.4 |
| Vector（向量） | 0.6 |
| Graph（图谱） | 0.2 |

## 功能开关（.env）
```env
GRAPH_EXTRACTION_ENABLED=true
CONSOLIDATION_ENABLED=true
AGENTMEMORY_AUTO_COMPRESS=true
AGENTMEMORY_INJECT_CONTEXT=true
SNAPSHOT_ENABLED=true
AGENTMEMORY_REFLECT=true
AGENTMEMORY_SLOTS=true
AGENTMEMORY_TOOLS=all
AGENTMEMORY_IMAGE_EMBEDDINGS=true
RERANK_ENABLED=true
```

## 配置文件位置
- AgentMemory: `~/.agentmemory/.env`
- Hermes: `$HERMES_HOME/config.yaml`（Windows: `C:\\Users\\<user>\\AppData\\Local\\hermes\\config.yaml`）

## Reranker（本地，2026-06-19 启用）

| 配置项 | 值 |
|--------|-----|
| 模型 | `Xenova/ms-marco-MiniLM-L-6-v2` |
| 引擎 | `@xenova/transformers`（本地推理） |
| 启用 | `RERANK_ENABLED=true` |
| VRAM | ~100MB |
| 首次调用 | 自动下载模型到 `~/.cache/huggingface/hub/` |

**搜索流程（4层）：**
```
查询 → BM25 (0.4) → Vector (0.6) → RRF融合 → Reranker重排序 → 返回
```

**依赖安装：**
```bash
npm install -g @xenova/transformers
```

**注意：** Reranker 不支持云端 API，只有本地 `@xenova/transformers`。

## LLM 与 Embedding 独立配置

LLM 和 Embedding 的 provider 是独立检测的，可以用不同提供商：

**LLM 检测顺序：**
```
OPENAI_API_KEY → openai
MINIMAX_API_KEY → minimax
ANTHROPIC_API_KEY → anthropic
GEMINI_API_KEY → gemini
OPENROUTER_API_KEY → openrouter
```

**Embedding 检测顺序：**
```
GEMINI_API_KEY → gemini embedding
OPENAI_API_KEY → openai embedding
VOYAGE_API_KEY → voyage embedding
COHERE_API_KEY → cohere embedding
OPENROUTER_API_KEY → openrouter embedding
@xenova/transformers → local embedding
```

**本机配置：** 两者都用 SiliconFlow（通过 OPENAI_API_KEY + OPENAI_BASE_URL），但模型不同。
