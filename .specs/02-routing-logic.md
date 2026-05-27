# 02 — Routing Logic

## Overview

Every LLM request from Hermes passes through a 3-stage pipeline: Bypass Check → Classification → Routing.

## Pipeline Flow

```
Request arrives (POST /v1/chat/completions)
        │
        ▼
┌─────────────────────────────────────┐
│  STAGE 1: BYPASS CHECK               │
│                                      │
│  Extract last user message.          │
│  Match against bypass patterns.      │
│                                      │
│  Match found?                        │
│    YES → resolve model → skip to     │
│          STAGE 3 (forward directly)  │
│    NO  → continue to STAGE 2        │
└──────────────┬───────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  STAGE 2: CLASSIFICATION             │
│                                      │
│  Extract last user message.          │
│  Build context hint (turn count,     │
│    conversation topic).              │
│  Send to Qwen 2.5 7B via Ollama.    │
│  Receive tier: "low" or "high".     │
│                                      │
└──────────────┬───────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  STAGE 3: FORWARD                    │
│                                      │
│  Resolve target model from tier      │
│    or bypass result.                 │
│  Forward FULL original payload       │
│    to target model via LiteLLM.      │
│  Stream response back to Hermes.     │
│                                      │
│  On failure → Fallback Handler       │
└─────────────────────────────────────┘
```

## Stage 1: Bypass Detection

### Pattern Matching

Extract the last user message content from the `messages` array. Match against patterns:

```
Patterns (case-insensitive):
  "use codex to"    → model: openai-codex
  "use claude to"   → model: claude-opus-4 (or configured claude model)
  "use gemini to"   → model: gemini-2.5-pro
  "use gpt to"      → model: gpt-4o
  "use haiku to"    → model: claude-haiku
  "use sonnet to"   → model: claude-sonnet-4
  "use ollama to"   → model: ollama/qwen2.5:7b (or configured local model)
```

### Rules
- Match is prefix-based: `"use <model> to"` at the start of the message or anywhere in it
- The bypass keyword is stripped from the prompt before forwarding (optional — TBD)
- Bypass events are still logged to Langfuse with `routing_method: "bypass"`

## Stage 2: Classification

### Input Preparation

From the incoming request payload:

1. **Extract last user message** — the final `role: "user"` entry in `messages[]`
2. **Build context hint** — lightweight metadata:
   - Turn count (number of messages in the array)
   - Presence of tool definitions (`tools` field exists?)
   - Presence of code blocks in recent messages
   - Conversation topic (extracted from system prompt if short enough)

### Classifier Prompt

Sent to Qwen 2.5 7B via Ollama:

```
System: You are a prompt complexity classifier. Classify the user's prompt into one of three categories: "chat", "low", or "high".

"chat" = casual conversation, greetings, small talk, confirmations, emoji reactions, "hi", "thanks", "ok", "yes", "no", "how are you", chit-chat with no task
"low" = simple questions, formatting, translation, short factual answers, single-step tasks, lookups
"high" = complex reasoning, architecture design, multi-step analysis, code generation, debugging, creative writing, planning

Context: This is turn {N} of a conversation. {tools_hint}. {topic_hint}.

Respond with ONLY "chat", "low", or "high".

User: {last_user_message}
```

### Output
- Expected response: `"chat"`, `"low"`, or `"high"`
- If response is unparseable → default to `"high"` (safer to over-serve than under-serve)
- Classification latency target: < 500ms

### Tier Behavior
- `chat` → uses the CHEAPEST model available (e.g., local Ollama or free-tier model)
- `low` → uses a cheap cloud model (e.g., Haiku, GPT-4o-mini)
- `high` → uses an expensive model (e.g., Opus, GPT-4o)

### Edge Cases
- Empty user message → default `"high"`
- Emoji only → classify as `"chat"`
- Very long user message (>2000 chars) → default `"high"`
- Classifier timeout (>2s) → default `"high"`, log warning

## Stage 3: Routing & Forwarding

### Model Resolution

```python
if bypass_model:
    target = bypass_model
elif tier == "chat":
    target = config.chat_tier_model  # e.g., "ollama/qwen2.5:7b" or free model
elif tier == "low":
    target = config.low_tier_model   # e.g., "claude-haiku" or "gpt-4o-mini"
elif tier == "high":
    target = config.high_tier_model  # e.g., "claude-opus-4" or "gpt-4o"
```

### Forwarding

- Forward the **original full payload** from Hermes (unchanged)
- Only modify the `model` field to the resolved target model
- Preserve all other fields: `messages`, `tools`, `temperature`, `stream`, etc.
- Use LiteLLM for the actual API call (handles auth, format translation)

### Streaming

- If `stream: true` in the request → stream SSE chunks back to Hermes
- Each chunk is forwarded as-is from the provider
- Emit a WebSocket event when streaming starts and when it completes

## Fallback Handler

### Trigger Conditions
- HTTP 429 (rate limit)
- HTTP 5xx (server error)
- Timeout (configurable, default 30s)
- Connection error

### Fallback Strategy

```yaml
fallback_chain:
  high:
    - claude-opus-4
    - gpt-4o
    - gemini-2.5-pro
  low:
    - claude-haiku
    - gpt-4o-mini
    - gemini-2.5-flash
```

On failure:
1. Try next model in the chain for that tier
2. If all fail → return error to Hermes with details
3. Log fallback event to Langfuse

## Event Emission

At each stage, emit events for observability:

```json
// Bypass detected
{"event": "bypass", "model": "claude-opus-4", "keyword": "use claude to", "timestamp": "..."}

// Classification complete
{"event": "classify", "tier": "high", "latency_ms": 320, "input_preview": "design a...", "timestamp": "..."}

// Routing decision
{"event": "route", "target_model": "claude-opus-4", "method": "classify|bypass", "timestamp": "..."}

// Forward started
{"event": "forward_start", "model": "claude-opus-4", "stream": true, "timestamp": "..."}

// Forward complete
{"event": "forward_complete", "model": "claude-opus-4", "tokens_in": 1500, "tokens_out": 800, "cost": 0.03, "latency_ms": 2100, "timestamp": "..."}

// Fallback triggered
{"event": "fallback", "from_model": "claude-opus-4", "to_model": "gpt-4o", "reason": "429", "timestamp": "..."}
```
