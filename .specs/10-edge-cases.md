# 10 — Edge Cases & Handling

## Classification Edge Cases

| Case | Handling |
|------|----------|
| Empty user message (`""`) | Default to HIGH |
| Emoji only (`"👍"`, `"🔥"`) | Classify as CHAT (cheapest) |
| Non-English language | Accept as-is — Qwen handles multilingual |
| Base64/file dump in message | Default to HIGH |
| No user message in payload (system only) | Default to HIGH |
| Tool-only request (no new user message) | Default to HIGH (mid-agent-loop) |
| Very long message (>2000 chars) | Still classify normally (only last message sent to classifier) |

## Bypass Edge Cases

| Case | Handling |
|------|----------|
| Bypass keyword inside a code block | Only match if message STARTS with bypass keyword |
| Bypass keyword in middle of sentence | No match — must be at start |
| Multiple bypass keywords in one message | First match wins |
| Bypass to a model that's not configured | Return error: "Model X not available" |
| Bypass to a model with no API key | Fallback chain, or error if no alternatives |

## Streaming Edge Cases

| Case | Handling |
|------|----------|
| Provider disconnects mid-stream | Send SSE error event, close stream |
| Client disconnects mid-stream | Cancel upstream request (save cost) |
| Classifier slow (>2s) + streaming request | Accept latency — classification must complete before streaming starts |
| Provider returns empty stream | Forward empty, let client handle |

## Fallback Edge Cases

| Case | Handling |
|------|----------|
| All providers down | Return error after exhausting chain (max 2 retries + fallback) |
| Provider returns 200 but garbage response | Pass through — not router's job to validate quality |
| Target model's context window < payload size | Detect before forwarding → pick model with larger context from same tier |
| Fallback model also fails | Continue down the chain until exhausted |

## Concurrency Edge Cases

| Case | Handling |
|------|----------|
| Multiple requests hit classifier simultaneously | Accept latency spikes (Ollama queues internally). Optimize later if needed |
| Many WebSocket clients connected (50+) | Broadcast to all — acceptable for local use. Add limit later if needed |
| Config hot-reload during active request | Request uses config snapshot taken at request start (not mid-request) |

## Hermes-Specific Edge Cases

| Case | Handling |
|------|----------|
| Hermes sends 100k+ token payload | Classification still works (reads last message only). Forward as-is — if model rejects, fallback to larger-context model |
| Hermes retries its own request (timeout) | Router treats as new request — acceptable, logged as separate trace |
| Hermes sends request with model field set (not "auto") | Treat as bypass — forward to that model directly |

---

## Context Window Protection

Before forwarding, the router SHOULD check:

```python
estimated_tokens = len(str(payload)) / 4  # rough estimate
if estimated_tokens > target_model.max_tokens * 0.9:
    # Switch to a model with larger context in the same tier
    target_model = find_larger_context_model(tier)
```

This prevents forwarding failures due to context overflow.
