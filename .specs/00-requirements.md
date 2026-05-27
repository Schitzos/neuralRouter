# 00 — Project Requirements

## Project

**Name:** Schitzo Neural Router
**Type:** AI Model Routing Proxy with Real-Time Observability
**Version:** 1.0.0 (MVP)

---

## Functional Requirements

### FR-1: Prompt Classification
- The system MUST classify incoming prompts into two tiers: `low` and `high`
- Classification MUST use Qwen 2.5 7B model running locally via Ollama
- Classification MUST extract the last user message from the payload for clean signal
- Classification MUST include a context hint (turn count, tools presence) for accuracy
- If classification fails or times out (>2s), the system MUST default to `high` tier

### FR-2: Model Routing
- The system MUST route `low` tier prompts to a configured cheap model
- The system MUST route `high` tier prompts to a configured expensive model
- The system MUST support configurable model-to-tier mapping via YAML config
- The system MUST forward the original payload unchanged (except the `model` field)

### FR-3: Bypass Detection
- The system MUST detect bypass keywords in the user message (e.g., "use claude to", "use codex to")
- When a bypass keyword is detected, the system MUST skip classification and route directly to the specified model
- Bypass patterns MUST be configurable via YAML config
- Bypass matching MUST be case-insensitive

### FR-4: Fallback Handling
- On model failure (429, 5xx, timeout), the system MUST retry up to 2 times
- After retries exhausted, the system MUST try the next model in the fallback chain
- Fallback chains MUST be configurable per tier
- If all models in the chain fail, the system MUST return a clear error to the client

### FR-5: Streaming Support
- The system MUST support SSE streaming (`stream: true`)
- Streaming chunks MUST be forwarded as-is from the provider to the client
- The system MUST handle both streaming and non-streaming requests

### FR-6: OpenAI-Compatible API
- The system MUST expose `/v1/chat/completions` endpoint (OpenAI format)
- The system MUST expose `/v1/models` endpoint listing available models
- The system MUST be usable as a drop-in replacement for any OpenAI-compatible client
- Response format MUST conform to OpenAI's chat completion schema

### FR-7: Real-Time Observability (WebSocket)
- The system MUST emit events at each pipeline stage via WebSocket
- Events: `request_start`, `bypass_detected`, `classify_start`, `classify_complete`, `route_decision`, `forward_start`, `forward_stream`, `forward_complete`, `fallback_triggered`, `request_error`
- Multiple dashboard clients MUST be able to connect simultaneously
- Events MUST include request_id, session_id, timestamp, and relevant data

### FR-8: Historical Observability (Langfuse)
- The system MUST send traces to Langfuse for every request
- Each trace MUST include nested spans: bypass_check, classify, route, llm_call
- Traces MUST include: model used, tokens in/out, cost, latency, tier, routing method
- Traces MUST be grouped by session_id for multi-turn conversations

### FR-9: Live Dashboard
- The system MUST provide a web-based dashboard with three views:
  - **Live View:** real-time graph showing pipeline nodes lighting up during execution
  - **History View:** replay past sessions as a visual timeline (data from Langfuse)
  - **Analytics View:** cost, latency, volume charts (data from Langfuse)
- Clicking a node/turn MUST show details (prompt, response, model, cost, latency)

### FR-10: Configuration
- The system MUST load configuration from YAML file + .env
- The system MUST support environment variable overrides
- The system MUST hot-reload config on file change (no restart needed)
- The system MUST provide a CLI setup wizard for first-time configuration

### FR-11: Health & Status
- The system MUST expose `/health` endpoint (no auth, for probes)
- The system MUST expose `/status` endpoint with runtime stats
- The system MUST expose `/metrics` endpoint in Prometheus format

### FR-12: Persistence
- The system MUST store request logs and stats in SQLite
- Data MUST survive restarts
- SQLite database location MUST be configurable

---

## Non-Functional Requirements

### NFR-1: Performance
- Classification latency MUST be < 500ms (target: ~300ms)
- Total routing overhead (bypass check + classify + route decision) MUST be < 600ms
- Streaming first-byte latency MUST not add more than 100ms over direct provider call
- The system MUST handle at least 10 concurrent requests

### NFR-2: Reliability
- The system MUST not crash on provider failures (graceful error handling)
- The system MUST recover from Ollama disconnection (retry classifier, or default to high)
- The system MUST handle malformed requests with clear error messages
- Uptime target: 99% (local service, restarts acceptable)

### NFR-3: Security
- API keys MUST be stored in .env file with restricted permissions (600)
- API keys MUST never appear in logs, traces, or API responses
- Optional bearer token auth for the router API
- Dashboard accessible on localhost only (no external exposure by default)

### NFR-4: Maintainability
- Code MUST follow Clean Architecture principles (see Architecture section)
- Code MUST follow SOLID design principles
- All business logic MUST have unit tests
- Integration tests MUST cover the full routing pipeline
- Code MUST pass linting (ruff) with zero warnings

### NFR-5: Observability
- All errors MUST be logged with context (request_id, model, error type)
- Application logs MUST be structured JSON to stdout
- Log levels: ERROR, WARN, INFO, DEBUG
- Default log level: INFO (configurable)

### NFR-6: Portability
- The system MUST run on macOS and Linux
- The system MUST be deployable via Docker Compose (single command)
- The system MUST work without GPU (CPU-only Ollama, slower but functional)

---

## Constraints

1. **Single user only** (MVP) — multi-user is a future requirement
2. **Local deployment only** — no cloud deployment in MVP
3. **Hermes is external** — we don't modify Hermes, only configure it
4. **LiteLLM handles provider differences** — we don't write provider-specific adapters
5. **Langfuse is self-hosted** — no cloud Langfuse dependency
6. **No caching** — every request goes to a model (no response caching)
7. **No rate limiting** — left to providers to enforce

---

## Architecture: Clean Architecture

### Layers

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                     │
│  (FastAPI routes, WebSocket handlers, CLI)               │
│                                                          │
│  Depends on: Application Layer                           │
│  Contains: HTTP handlers, request/response serialization │
└────────────────────────────┬────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────┐
│                    APPLICATION LAYER                      │
│  (Use cases / services)                                  │
│                                                          │
│  Depends on: Domain Layer                                │
│  Contains: RoutePromptUseCase, ClassifyPromptUseCase,   │
│            EmitEventUseCase, GetStatusUseCase            │
└────────────────────────────┬────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────┐
│                    DOMAIN LAYER                           │
│  (Entities, interfaces, business rules)                  │
│                                                          │
│  Depends on: Nothing                                     │
│  Contains: Entities (Prompt, Tier, Route, Event),       │
│            Interfaces (IClassifier, IForwarder,          │
│            IEventEmitter, ITracer)                       │
└────────────────────────────┬────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────┐
│                 INFRASTRUCTURE LAYER                      │
│  (External implementations)                              │
│                                                          │
│  Depends on: Domain Layer (implements interfaces)        │
│  Contains: OllamaClassifier, LiteLLMForwarder,          │
│            WebSocketEmitter, LangfuseTracer,             │
│            SQLiteRepository, ConfigLoader                │
└─────────────────────────────────────────────────────────┘
```

### Dependency Rule
- Inner layers MUST NOT depend on outer layers
- Domain layer has ZERO external dependencies
- Infrastructure implements domain interfaces
- Presentation calls application layer only

### Directory Structure (Backend)

```
router/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app factory
│   │
│   ├── domain/                    # DOMAIN LAYER
│   │   ├── __init__.py
│   │   ├── entities.py            # Prompt, Tier, RouteDecision, Event
│   │   ├── interfaces/
│   │   │   ├── __init__.py
│   │   │   ├── classifier.py     # IClassifier (abstract)
│   │   │   ├── forwarder.py      # IForwarder (abstract)
│   │   │   ├── event_emitter.py  # IEventEmitter (abstract)
│   │   │   ├── tracer.py         # ITracer (abstract)
│   │   │   └── repository.py     # IRepository (abstract)
│   │   └── exceptions.py         # Domain exceptions
│   │
│   ├── application/               # APPLICATION LAYER
│   │   ├── __init__.py
│   │   ├── route_prompt.py        # RoutePromptUseCase (main orchestrator)
│   │   ├── classify_prompt.py     # ClassifyPromptUseCase
│   │   ├── detect_bypass.py       # DetectBypassUseCase
│   │   └── get_status.py          # GetStatusUseCase
│   │
│   ├── infrastructure/            # INFRASTRUCTURE LAYER
│   │   ├── __init__.py
│   │   ├── ollama_classifier.py   # IClassifier → Ollama/Qwen
│   │   ├── litellm_forwarder.py   # IForwarder → LiteLLM
│   │   ├── websocket_emitter.py   # IEventEmitter → WebSocket
│   │   ├── langfuse_tracer.py     # ITracer → Langfuse
│   │   ├── sqlite_repository.py   # IRepository → SQLite
│   │   └── config_loader.py       # YAML + .env loading
│   │
│   ├── presentation/              # PRESENTATION LAYER
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── completions.py    # POST /v1/chat/completions
│   │   │   ├── models.py         # GET /v1/models
│   │   │   ├── health.py         # GET /health, /status, /metrics
│   │   │   └── websocket.py      # WS /ws/events
│   │   └── schemas/
│   │       ├── requests.py        # Pydantic request models
│   │       └── responses.py       # Pydantic response models
│   │
│   └── container.py               # Dependency injection container
│
├── tests/
│   ├── unit/
│   │   ├── test_bypass.py
│   │   ├── test_classifier.py
│   │   ├── test_router.py
│   │   └── test_route_prompt.py
│   ├── integration/
│   │   ├── test_completions_endpoint.py
│   │   ├── test_streaming.py
│   │   └── test_fallback.py
│   └── conftest.py                # Fixtures, mocks
│
├── pyproject.toml
├── requirements.txt
└── Dockerfile
```

### Directory Structure (Frontend)

```
dashboard/
├── src/
│   ├── App.tsx                    # Root component + routing
│   ├── main.tsx                   # Vite entry point
│   │
│   ├── components/                # COMPONENT-BASED ARCHITECTURE
│   │   ├── layout/
│   │   │   ├── Layout.tsx         # Main layout (sidebar + content)
│   │   │   ├── Sidebar.tsx        # Navigation + session list
│   │   │   └── Header.tsx
│   │   ├── live/
│   │   │   ├── LiveGraph.tsx      # React Flow graph (main live view)
│   │   │   ├── GraphNode.tsx      # Custom node component
│   │   │   └── NodeDetail.tsx     # Detail panel on node click
│   │   ├── history/
│   │   │   ├── HistoryView.tsx    # Session timeline
│   │   │   ├── SessionList.tsx    # List of past sessions
│   │   │   └── TurnCard.tsx       # Individual turn detail
│   │   └── analytics/
│   │       ├── Analytics.tsx      # Main analytics view
│   │       ├── CostChart.tsx      # Cost over time
│   │       ├── TierPieChart.tsx   # Low vs high distribution
│   │       └── LatencyChart.tsx   # Latency histogram
│   │
│   ├── hooks/                     # Custom React hooks
│   │   ├── useWebSocket.ts        # WebSocket connection + events
│   │   ├── useLangfuse.ts         # Langfuse API queries
│   │   └── useStats.ts            # Aggregated stats
│   │
│   ├── types/                     # TypeScript types
│   │   ├── events.ts              # WebSocket event types
│   │   ├── traces.ts              # Langfuse trace types
│   │   └── models.ts              # Model/config types
│   │
│   └── utils/                     # Helpers
│       ├── api.ts                 # HTTP client for router API
│       └── format.ts              # Cost/time formatters
│
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
└── Dockerfile
```

---

## SOLID Principles Applied

### Single Responsibility (S)
- `OllamaClassifier` — only classifies prompts
- `LiteLLMForwarder` — only forwards requests to models
- `WebSocketEmitter` — only broadcasts events
- `LangfuseTracer` — only sends traces
- Each use case does ONE thing

### Open/Closed (O)
- New providers → implement `IForwarder` interface (no existing code changes)
- New classifiers → implement `IClassifier` interface
- New event destinations → implement `IEventEmitter` interface
- System is extendable without modifying existing code

### Liskov Substitution (L)
- Any `IClassifier` implementation can replace `OllamaClassifier`
- Any `IForwarder` implementation can replace `LiteLLMForwarder`
- Swap implementations without breaking the application layer

### Interface Segregation (I)
- `IClassifier` — only `classify(prompt) → Tier`
- `IForwarder` — only `forward(request, model) → Response`
- `IEventEmitter` — only `emit(event)`
- `ITracer` — only `trace(span_data)`
- Small, focused interfaces — no god interfaces

### Dependency Inversion (D)
- Application layer depends on abstractions (interfaces), not implementations
- `RoutePromptUseCase` receives `IClassifier`, `IForwarder`, `IEventEmitter` via injection
- Concrete implementations injected at startup via DI container
- Easy to mock for testing

---

## Domain Entities

```python
# Tier
class Tier(Enum):
    LOW = "low"
    HIGH = "high"

# Route Decision
@dataclass
class RouteDecision:
    tier: Tier
    target_model: str
    method: str  # "classify" | "bypass"
    classification_latency_ms: float | None

# Router Event
@dataclass
class RouterEvent:
    id: str
    session_id: str
    request_id: str
    event_type: str
    timestamp: datetime
    data: dict

# Completion Request (domain representation)
@dataclass
class CompletionRequest:
    messages: list[dict]
    model: str | None
    stream: bool
    tools: list[dict] | None
    temperature: float | None
    max_tokens: int | None
    raw_payload: dict  # original full payload
```

---

## Testing Strategy

### Unit Tests
- Test bypass detection (pattern matching, case insensitivity)
- Test classification logic (prompt extraction, context hint building)
- Test routing logic (tier → model resolution, fallback chain)
- Test event emission (correct event types and data)
- Mock all infrastructure (Ollama, LiteLLM, Langfuse)

### Integration Tests
- Full request flow: request → classify → route → mock provider → response
- Streaming end-to-end
- Fallback chain (simulate provider failure)
- WebSocket event delivery
- Config loading and hot-reload

### Test Tools
- `pytest` + `pytest-asyncio` for async tests
- `httpx` for API testing
- `unittest.mock` for mocking infrastructure
- Test fixtures for sample payloads

---

## Versioning

- Semantic versioning: `MAJOR.MINOR.PATCH`
- Config and data stored in `~/.schitzo/` (persists across updates)
- `CHANGELOG.md` tracks all changes
- Docker image tagged with version

---

## Acceptance Criteria (MVP)

The MVP is DONE when:

1. [ ] A request to `/v1/chat/completions` is classified and routed to the correct model
2. [ ] Bypass keywords skip classification and route directly
3. [ ] Streaming works end-to-end
4. [ ] Fallback triggers on provider failure (after 2 retries)
5. [ ] WebSocket emits events at each pipeline stage
6. [ ] Langfuse shows traces with nested spans, cost, and latency
7. [ ] Dashboard Live View shows nodes lighting up in real-time
8. [ ] Dashboard History View replays a past session as a timeline
9. [ ] Dashboard Analytics View shows cost and tier distribution charts
10. [ ] `docker compose up` starts all services
11. [ ] Hermes configured to use the router and works normally
12. [ ] All unit tests pass
13. [ ] All integration tests pass
