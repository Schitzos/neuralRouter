# 04 — API Contract

## Overview

Schitzo Neural Router exposes an OpenAI-compatible API so Hermes (or any OpenAI client) can use it as a drop-in model endpoint. Additionally, it exposes management and observability endpoints.

## Base URL

```
http://localhost:8000
```

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/chat/completions` | Main proxy endpoint (OpenAI-compatible) |
| GET | `/v1/models` | List available models |
| GET | `/health` | Health check |
| GET | `/status` | Router status and stats |
| WS | `/ws/events` | Real-time event stream |
| GET | `/metrics` | Prometheus metrics |

---

## POST `/v1/chat/completions`

The main endpoint. Receives requests from Hermes, classifies, routes, and returns the response.

### Request

Fully OpenAI-compatible. Hermes sends this as-is.

```json
{
  "model": "auto",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant..."},
    {"role": "user", "content": "design a distributed cache"},
    {"role": "assistant", "content": "Here's my approach..."},
    {"role": "user", "content": "now implement it in Go"}
  ],
  "stream": true,
  "temperature": 0.7,
  "max_tokens": 4096,
  "tools": [...]
}
```

**Model field behavior:**
- `"auto"` or omitted → normal classification flow
- `"bypass:claude-opus-4"` → skip classification, use specified model (alternative to keyword bypass)
- Any other value → treated as direct model request (bypass)

### Response (non-streaming)

Standard OpenAI format:

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1716620218,
  "model": "claude-opus-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Here's the implementation..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 1500,
    "completion_tokens": 800,
    "total_tokens": 2300
  },
  "x_schitzo": {
    "tier": "high",
    "routing_method": "classify",
    "classification_latency_ms": 320,
    "target_model": "claude-opus-4",
    "cost_usd": 0.034
  }
}
```

**Note:** `x_schitzo` is a custom extension field. Clients that don't understand it will ignore it.

### Response (streaming)

Standard SSE format:

```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1716620218,"model":"claude-opus-4","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1716620218,"model":"claude-opus-4","choices":[{"index":0,"delta":{"content":"Here's"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1716620218,"model":"claude-opus-4","choices":[{"index":0,"delta":{"content":" the"},"finish_reason":null}]}

...

data: [DONE]
```

### Error Response

```json
{
  "error": {
    "message": "All models in fallback chain failed",
    "type": "routing_error",
    "code": "all_models_failed",
    "details": {
      "attempted": ["claude-opus-4", "gpt-4o", "gemini-2.5-pro"],
      "errors": ["429", "500", "timeout"]
    }
  }
}
```

HTTP status codes:
- `200` — success
- `429` — all models rate limited
- `500` — internal router error
- `502` — upstream provider error
- `504` — all models timed out

---

## GET `/v1/models`

List available models (OpenAI-compatible).

### Response

```json
{
  "object": "list",
  "data": [
    {
      "id": "auto",
      "object": "model",
      "owned_by": "schitzo-router",
      "description": "Smart routing — classifies and picks the best model"
    },
    {
      "id": "claude-opus-4",
      "object": "model",
      "owned_by": "anthropic",
      "tier": "high"
    },
    {
      "id": "claude-haiku",
      "object": "model",
      "owned_by": "anthropic",
      "tier": "low"
    },
    {
      "id": "gpt-4o",
      "object": "model",
      "owned_by": "openai",
      "tier": "high"
    },
    {
      "id": "gpt-4o-mini",
      "object": "model",
      "owned_by": "openai",
      "tier": "low"
    }
  ]
}
```

---

## GET `/health`

Simple health check. No auth required.

### Response

```json
{
  "status": "ok",
  "classifier": "ready",
  "uptime_seconds": 3600
}
```

---

## GET `/status`

Detailed router status.

### Response

```json
{
  "status": "running",
  "classifier": {
    "model": "qwen2.5:7b",
    "status": "ready",
    "avg_latency_ms": 310
  },
  "stats": {
    "total_requests": 847,
    "requests_today": 52,
    "tier_distribution": {
      "low": 0.62,
      "high": 0.38
    },
    "bypass_count": 15,
    "fallback_count": 3,
    "total_cost_today_usd": 1.23,
    "estimated_savings_usd": 2.87
  },
  "models": {
    "low": "claude-haiku",
    "high": "claude-opus-4"
  },
  "uptime_seconds": 3600
}
```

---

## WS `/ws/events`

WebSocket endpoint for real-time event streaming. See `03-observability.md` for event format details.

### Connection

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/events");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // handle event
};
```

### Optional Filters (via query params)

```
ws://localhost:8000/ws/events?session_id=sess_xyz
ws://localhost:8000/ws/events?events=classify_complete,forward_complete
```

---

## GET `/metrics`

Prometheus-compatible metrics endpoint.

### Response (text/plain)

```
# HELP schitzo_requests_total Total requests processed
# TYPE schitzo_requests_total counter
schitzo_requests_total{model="claude-opus-4",tier="high"} 142
schitzo_requests_total{model="claude-haiku",tier="low"} 305

# HELP schitzo_classification_latency_ms Classification latency
# TYPE schitzo_classification_latency_ms histogram
schitzo_classification_latency_ms_bucket{le="100"} 12
schitzo_classification_latency_ms_bucket{le="300"} 380
schitzo_classification_latency_ms_bucket{le="500"} 445
schitzo_classification_latency_ms_bucket{le="1000"} 447

# HELP schitzo_cost_usd_total Total cost in USD
# TYPE schitzo_cost_usd_total counter
schitzo_cost_usd_total{model="claude-opus-4"} 8.45
schitzo_cost_usd_total{model="claude-haiku"} 0.31

# HELP schitzo_tokens_total Total tokens consumed
# TYPE schitzo_tokens_total counter
schitzo_tokens_total{model="claude-opus-4",type="input"} 213000
schitzo_tokens_total{model="claude-opus-4",type="output"} 96000
```

---

## Authentication

### Default (local use)
- No auth required (localhost only)

### Optional Token Auth
- Set `SCHITZO_AUTH_TOKEN` env var to enable
- Clients pass: `Authorization: Bearer <token>`
- `/health` endpoint is always public (no auth)

---

## Headers

### Request Headers (from Hermes)
```
Content-Type: application/json
Authorization: Bearer <token>  (if auth enabled)
```

### Response Headers (from Router)
```
Content-Type: application/json
X-Schitzo-Model: claude-opus-4
X-Schitzo-Tier: high
X-Schitzo-Routing-Method: classify
X-Schitzo-Classification-Latency-Ms: 320
```

Custom `X-Schitzo-*` headers provide routing metadata without modifying the response body (useful for clients that strictly parse OpenAI format).
