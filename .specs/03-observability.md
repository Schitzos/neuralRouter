# 03 — Observability

## Overview

Schitzo Neural Router provides three observability layers:
1. **Real-time** — WebSocket events powering a live graph dashboard
2. **Historical** — Langfuse traces for replay and debugging
3. **Analytics** — Langfuse dashboards for cost/latency/volume trends

## Data Sources

```
┌─────────────────────┐         ┌─────────────────────┐
│  SCHITZO ROUTER      │         │  HERMES AGENT        │
│                      │         │                      │
│  Emits:              │         │  Emits (OTel):       │
│  • classify event    │         │  • tool executions   │
│  • route event       │         │  • memory reads      │
│  • forward event     │         │  • memory writes     │
│  • fallback event    │         │  • skill creation    │
│  • cost/tokens       │         │  • skill usage       │
└──────────┬───────────┘         └──────────┬───────────┘
           │                                │
           ▼                                ▼
┌──────────────────────────────────────────────────────┐
│                    LANGFUSE                            │
│           (single source of truth)                    │
│                                                      │
│  Correlates via shared session_id / trace_id         │
└──────────────────────────────────────────────────────┘
```

## 1. Real-Time Layer (WebSocket)

### Connection

- Endpoint: `ws://localhost:8000/ws/events`
- Protocol: WebSocket
- Auth: optional token (same as API auth)
- Supports multiple concurrent dashboard connections

### Event Format

All events follow this structure:

```json
{
  "id": "evt_abc123",
  "session_id": "sess_xyz",
  "timestamp": "2025-05-25T10:36:58.123Z",
  "event": "<event_type>",
  "data": { ... }
}
```

### Event Types

#### `request_start`
Fired when a new request arrives from Hermes.
```json
{
  "event": "request_start",
  "data": {
    "request_id": "req_001",
    "session_id": "sess_xyz",
    "message_preview": "design a distributed...",
    "turn_number": 5,
    "has_tools": true,
    "stream": true
  }
}
```

#### `bypass_detected`
Fired when a bypass keyword is found.
```json
{
  "event": "bypass_detected",
  "data": {
    "request_id": "req_001",
    "keyword": "use claude to",
    "target_model": "claude-opus-4"
  }
}
```

#### `classify_start`
```json
{
  "event": "classify_start",
  "data": {
    "request_id": "req_001",
    "input_preview": "design a distributed..."
  }
}
```

#### `classify_complete`
```json
{
  "event": "classify_complete",
  "data": {
    "request_id": "req_001",
    "tier": "high",
    "latency_ms": 320
  }
}
```

#### `route_decision`
```json
{
  "event": "route_decision",
  "data": {
    "request_id": "req_001",
    "target_model": "claude-opus-4",
    "method": "classify",
    "tier": "high"
  }
}
```

#### `forward_start`
```json
{
  "event": "forward_start",
  "data": {
    "request_id": "req_001",
    "model": "claude-opus-4",
    "stream": true
  }
}
```

#### `forward_stream`
Periodic updates during streaming (every N tokens or every second).
```json
{
  "event": "forward_stream",
  "data": {
    "request_id": "req_001",
    "tokens_so_far": 150,
    "elapsed_ms": 1200
  }
}
```

#### `forward_complete`
```json
{
  "event": "forward_complete",
  "data": {
    "request_id": "req_001",
    "model": "claude-opus-4",
    "tokens_in": 1500,
    "tokens_out": 800,
    "cost_usd": 0.034,
    "latency_ms": 2100,
    "status": "success"
  }
}
```

#### `fallback_triggered`
```json
{
  "event": "fallback_triggered",
  "data": {
    "request_id": "req_001",
    "from_model": "claude-opus-4",
    "to_model": "gpt-4o",
    "reason": "429_rate_limit"
  }
}
```

#### `request_error`
```json
{
  "event": "request_error",
  "data": {
    "request_id": "req_001",
    "error": "all_models_failed",
    "details": "Exhausted fallback chain"
  }
}
```

## 2. Historical Layer (Langfuse)

### Trace Structure

Each request creates one Langfuse trace with nested spans:

```
Trace: "chat_completion" (session_id = sess_xyz)
├── Span: "bypass_check" (duration: 1ms)
│   └── metadata: { matched: false }
├── Span: "classify" (duration: 320ms)
│   └── metadata: { tier: "high", model: "qwen2.5:7b" }
│   └── input: "design a distributed..."
│   └── output: "high"
├── Span: "route" (duration: 0ms)
│   └── metadata: { target: "claude-opus-4", method: "classify" }
└── Generation: "llm_call" (duration: 2100ms)
    └── model: "claude-opus-4"
    └── input: { messages: [...] }
    └── output: { content: "..." }
    └── usage: { prompt_tokens: 1500, completion_tokens: 800 }
    └── cost: 0.034
```

### Session Grouping

- All requests in the same Hermes conversation share a `session_id`
- Langfuse groups them into a session view
- History replay shows the full conversation timeline

### Hermes OTel Spans (correlated)

When Hermes emits OTel spans to the same Langfuse instance:

```
Trace: "chat_completion" (session_id = sess_xyz)
├── Span: "classify" (from router)
├── Generation: "llm_call" (from router)
├── Span: "tool_execution" (from Hermes OTel)
│   └── tool: "write_file"
│   └── input: { path: "/src/auth.ts" }
│   └── duration: 50ms
├── Span: "classify" (from router, next turn)
├── Generation: "llm_call" (from router, next turn)
```

### Correlation Strategy

- Router generates a `trace_id` per request
- Hermes passes this trace_id via request headers (if supported) or we correlate by `session_id` + timestamp proximity
- Both systems tag spans with `session_id` for grouping

## 3. Analytics Layer (Langfuse Dashboard)

### Built-in Metrics (no custom code needed)

- **Cost per model** — daily/weekly/monthly breakdown
- **Cost per session** — how much each conversation costs
- **Latency distribution** — p50, p95, p99 per model
- **Volume** — requests per hour/day, tokens consumed
- **Tier distribution** — % of requests classified as low vs high
- **Fallback rate** — how often fallbacks trigger

### Custom Dashboard Views

Configure in Langfuse:
- "Routing Efficiency" — cost savings vs sending everything to expensive model
- "Classification Accuracy" — (requires manual labeling or feedback loop)
- "Model Usage" — pie chart of which models handle what %

### Data Export

Available from Langfuse:
- REST API (programmatic queries)
- CSV export (one-off from UI)
- S3 blob export (scheduled bulk)
- PostHog/Mixpanel push

## Live Dashboard UI

### Technology
- React + React Flow (node graph)
- WebSocket client for real-time updates
- Langfuse API client for history

### Views

#### Live View
```
┌─────────────────────────────────────────────────────┐
│  LIVE — Session: sess_xyz                            │
│                                                      │
│  [BYPASS]──→[CLASSIFY]──→[ROUTE]──→[GENERATE]       │
│   skip       ✅ high      opus     🔄 streaming     │
│   1ms        320ms        0ms      1.2s...          │
│                                                      │
│  Active sessions: 2                                  │
│  Current cost: $0.034                                │
└─────────────────────────────────────────────────────┘
```

#### History View
```
┌─────────────────────────────────────────────────────┐
│  HISTORY — Session: sess_xyz (12 turns)              │
│                                                      │
│  [Turn 1]──→[Turn 2]──→[Turn 3]──→[Turn 4]         │
│   Haiku      Haiku      Opus       Opus             │
│   $0.001     $0.001     $0.03      $0.02            │
│                           ↑                          │
│                     model switch                     │
│                                                      │
│  [Turn 3 detail]                                     │
│  Prompt: "design a distributed cache..."            │
│  Model: claude-opus-4                                │
│  Tokens: 1500 in / 800 out                          │
│  Cost: $0.03                                         │
│  Latency: 2.1s                                       │
│  Between turns: [tool: write_file] [tool: run_test] │
└─────────────────────────────────────────────────────┘
```

#### Analytics View
```
┌─────────────────────────────────────────────────────┐
│  ANALYTICS — Last 7 days                             │
│                                                      │
│  Total cost: $12.45 (saved ~$28 vs all-premium)     │
│  Requests: 847                                       │
│  Tier split: 62% low / 38% high                     │
│  Avg latency: 1.8s (incl. 320ms classification)    │
│  Fallback rate: 2.1%                                 │
│                                                      │
│  [Cost chart over time]                              │
│  [Model usage pie chart]                             │
│  [Latency histogram]                                 │
└─────────────────────────────────────────────────────┘
```
