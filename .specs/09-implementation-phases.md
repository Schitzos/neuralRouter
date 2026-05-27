# 09 — Implementation Phases & Tasks

---

## Phase 0: Project Setup

**Goal:** Install system dependencies, initialize project structure, configure dev environment.

### Task 0.1: Install System Dependencies
- Install Python 3.12: `brew install python@3.12`
- Install Node.js 20: `brew install node@20`
- Install Docker: `brew install --cask docker`
- Install Ollama: `brew install ollama`
- Verify all installed:
  - `python3 --version` → 3.12+
  - `node --version` → 20+
  - `docker --version` → 24+
  - `ollama --version`

### Task 0.2: Setup Ollama & Pull Classifier Model
- Start Ollama server: `ollama serve`
- Pull Qwen 2.5 7B model: `ollama pull qwen2.5:7b` (~4.5 GB download)
- Verify classifier is ready: `curl http://localhost:11434/api/tags` (should list qwen2.5:7b)
- Test classification: `curl http://localhost:11434/api/generate -d '{"model":"qwen2.5:7b","prompt":"hi"}'`

### Task 0.3: Initialize Python Backend
- Create `router/` directory
- Create `pyproject.toml` with project metadata and dependencies
- Create `requirements.txt` (pinned versions)
- Set up virtual environment: `python3 -m venv .venv`
- Install dependencies: fastapi, uvicorn, litellm, langfuse, pyyaml, python-dotenv, httpx, pydantic, watchfiles, prometheus-client
- Verify: `python -c "import fastapi; print(fastapi.__version__)"` works

### Task 0.4: Initialize React Frontend
- Create `dashboard/` directory
- Scaffold with Vite: `npm create vite@latest dashboard -- --template react-ts`
- Install dependencies: `@xyflow/react`, `recharts`
- Verify: `npm run dev` starts without errors

### Task 0.5: Docker Compose Setup
- Create `docker-compose.yaml` with services:
  - `langfuse` (image: langfuse/langfuse, port 3000)
  - `langfuse-db` (image: postgres:16, port 5432)
- Create `.env.example` with all required variables
- Verify: `docker compose up -d langfuse langfuse-db` starts cleanly
- Verify Langfuse dashboard accessible at http://localhost:3000

### Task 0.4: Project Scaffolding
- Create backend directory structure (Clean Architecture layers):
  ```
  router/app/domain/
  router/app/domain/interfaces/
  router/app/application/
  router/app/infrastructure/
  router/app/presentation/
  router/app/presentation/api/
  router/app/presentation/schemas/
  ```
- Create `__init__.py` in all packages
- Create `router/app/main.py` with empty FastAPI app
- Create `router/tests/` with `conftest.py`
- Verify: `uvicorn app.main:app --reload` starts on port 8000

### Task 0.5: Configuration Files
- Create `config.yaml` with default values (models, tiers, bypass patterns, timeouts)
- Create `.env.example` with all API key placeholders
- Create `router/app/infrastructure/config_loader.py` — loads YAML + .env, merges env overrides
- Create `router/app/domain/entities.py` — define `Settings` dataclass
- Verify: app starts and prints loaded config

### Task 0.6: Dev Tooling
- Configure `ruff` for linting (in `pyproject.toml`)
- Configure `pytest` (in `pyproject.toml`)
- Create `Makefile` with commands: `dev`, `test`, `lint`, `format`
- Verify: `make lint` and `make test` run without errors

---

## Phase 1: Core Router

**Goal:** Working proxy that classifies and routes. Testable via curl.

### Task 1.1: Domain Layer — Entities
- Define `Tier` enum (LOW, HIGH)
- Define `RouteDecision` dataclass (tier, target_model, method, latency)
- Define `CompletionRequest` dataclass (messages, model, stream, tools, raw_payload)
- Define `RouterEvent` dataclass (id, session_id, request_id, event_type, timestamp, data)
- Define domain exceptions: `ClassificationError`, `ForwardingError`, `AllModelsFailedError`

### Task 1.2: Domain Layer — Interfaces
- Define `IClassifier` abstract class:
  - `async classify(prompt: str, context_hint: str) → Tier`
- Define `IForwarder` abstract class:
  - `async forward(request: dict, model: str) → dict`
  - `async forward_stream(request: dict, model: str) → AsyncGenerator`
- Define `IEventEmitter` abstract class:
  - `async emit(event: RouterEvent) → None`
- Define `ITracer` abstract class:
  - `start_trace(request_id, session_id) → TraceContext`
  - `add_span(trace_ctx, name, data) → None`
  - `end_trace(trace_ctx) → None`
- Define `IRepository` abstract class:
  - `log_request(request_id, model, tier, cost, latency) → None`
  - `get_stats() → dict`

### Task 1.3: Bypass Detection
- Create `router/app/application/detect_bypass.py`
- Implement `DetectBypassUseCase`:
  - Input: last user message string
  - Logic: match against configured bypass patterns (case-insensitive)
  - Output: `target_model: str | None`
- Load bypass patterns from config
- Write unit tests: match found, no match, case insensitivity, partial match

### Task 1.4: Classifier Implementation
- Create `router/app/infrastructure/ollama_classifier.py`
- Implement `OllamaClassifier(IClassifier)`:
  - Connects to Ollama API (`http://localhost:11434/api/generate`)
  - Sends classification prompt with last user message + context hint
  - Parses response: extract "low" or "high"
  - Handles timeout (>2s → default HIGH)
  - Handles connection error (→ default HIGH, log warning)
- Write unit tests with mocked Ollama responses

### Task 1.5: Prompt Extraction
- Create helper in `router/app/application/classify_prompt.py`
- Implement `ClassifyPromptUseCase`:
  - Extract last `role: "user"` message from messages array
  - Build context hint: turn count, has_tools boolean, code presence
  - Call `IClassifier.classify(prompt, context_hint)`
  - Return `Tier`
- Write unit tests: single message, multi-turn, empty messages, tools present

### Task 1.6: Router Logic
- Create `router/app/application/route_prompt.py`
- Implement `RoutePromptUseCase` (main orchestrator):
  - Step 1: Call `DetectBypassUseCase` → if match, skip to forward
  - Step 2: Call `ClassifyPromptUseCase` → get tier
  - Step 3: Resolve target model from tier (config lookup)
  - Step 4: Call `IForwarder.forward()` or `forward_stream()`
  - Step 5: On failure → retry (max 2) → fallback chain
  - Return response or stream
- Write unit tests with mocked classifier and forwarder

### Task 1.7: LiteLLM Forwarder
- Create `router/app/infrastructure/litellm_forwarder.py`
- Implement `LiteLLMForwarder(IForwarder)`:
  - `forward()`: call `litellm.acompletion(model, messages, **params)` → return response dict
  - `forward_stream()`: call `litellm.acompletion(model, messages, stream=True)` → yield chunks
  - Handle LiteLLM exceptions → raise `ForwardingError` with details
- Write unit tests with mocked litellm

### Task 1.8: Fallback Handler
- Implement fallback logic inside `RoutePromptUseCase`:
  - On `ForwardingError` → retry same model (up to 2 times)
  - After retries exhausted → pick next model from fallback chain
  - If all models fail → raise `AllModelsFailedError`
- Fallback chain loaded from config per tier
- Write unit tests: retry success, retry then fallback, all fail

### Task 1.9: API Endpoint — Completions
- Create `router/app/presentation/api/completions.py`
- Implement `POST /v1/chat/completions`:
  - Parse request body (Pydantic schema)
  - Call `RoutePromptUseCase`
  - Return OpenAI-compatible response
  - Handle streaming (StreamingResponse with SSE)
  - Add `X-Schitzo-*` headers to response
- Create Pydantic schemas in `presentation/schemas/`
- Write integration test: full request → response

### Task 1.10: API Endpoints — Models & Health
- Implement `GET /v1/models` — return configured models from registry
- Implement `GET /health` — return status + classifier readiness
- Write tests for both endpoints

### Task 1.11: Dependency Injection Container
- Create `router/app/container.py`
- Wire all implementations to interfaces:
  - `IClassifier` → `OllamaClassifier`
  - `IForwarder` → `LiteLLMForwarder`
  - `IEventEmitter` → (stub for now, real in Phase 2)
  - `ITracer` → (stub for now, real in Phase 2)
  - `IRepository` → (stub for now, real in Phase 2)
- Inject into use cases at app startup
- Verify: full flow works end-to-end with real Ollama + real provider

### Task 1.12: End-to-End Verification
- Start Ollama with Qwen 2.5 7B
- Start router
- Test with curl:
  - Simple prompt → routed to low tier model
  - Complex prompt → routed to high tier model
  - Bypass keyword → routed to specified model
  - Streaming request → SSE chunks returned
- Fix any issues found

---

## Phase 2: Observability

**Goal:** Full tracing, real-time events, metrics, and persistence.

### Task 2.1: Event Emitter
- Create `router/app/infrastructure/websocket_emitter.py`
- Implement `WebSocketEmitter(IEventEmitter)`:
  - Maintain list of connected WebSocket clients
  - `emit(event)` → broadcast JSON to all connected clients
  - Handle client disconnect gracefully
- Write unit tests

### Task 2.2: WebSocket Endpoint
- Create `router/app/presentation/api/websocket.py`
- Implement `WS /ws/events`:
  - Accept WebSocket connections
  - Register client with `WebSocketEmitter`
  - Keep connection alive (ping/pong)
  - Support optional query param filters (`session_id`, `events`)
  - Remove client on disconnect
- Write integration test: connect, send request, receive events

### Task 2.3: Emit Events in Pipeline
- Update `RoutePromptUseCase` to emit events at each stage:
  - `request_start` — when request arrives
  - `bypass_detected` — if bypass matched
  - `classify_start` / `classify_complete` — around classification
  - `route_decision` — after model resolved
  - `forward_start` / `forward_stream` / `forward_complete` — during forwarding
  - `fallback_triggered` — on fallback
  - `request_error` — on failure
- Write unit tests verifying correct events emitted

### Task 2.4: Langfuse Integration
- Create `router/app/infrastructure/langfuse_tracer.py`
- Implement `LangfuseTracer(ITracer)`:
  - Initialize Langfuse client with keys from config
  - `start_trace()` → create Langfuse trace with session_id
  - `add_span()` → add nested span (bypass_check, classify, route, llm_call)
  - `end_trace()` → flush trace
  - Include: model, tokens, cost, latency, tier, routing method
- Write unit tests with mocked Langfuse client

### Task 2.5: SQLite Repository
- Create `router/app/infrastructure/sqlite_repository.py`
- Implement `SQLiteRepository(IRepository)`:
  - Create tables on init: `requests`, `stats`
  - `log_request()` → insert request record
  - `get_stats()` → aggregate stats (total requests, cost, tier distribution)
  - `get_requests(session_id)` → fetch requests for a session
- Write unit tests with in-memory SQLite

### Task 2.6: Prometheus Metrics
- Create `router/app/infrastructure/metrics.py`
- Implement counters and histograms:
  - `schitzo_requests_total` (labels: model, tier, status)
  - `schitzo_classification_latency_ms` (histogram)
  - `schitzo_cost_usd_total` (labels: model)
  - `schitzo_tokens_total` (labels: model, type)
  - `schitzo_fallbacks_total` (labels: from_model, to_model)
- Implement `GET /metrics` endpoint (Prometheus text format)
- Write tests

### Task 2.7: Status Endpoint
- Extend `GET /status` to return:
  - Classifier status (ready/error, avg latency)
  - Request stats from SQLite (total, today, tier distribution)
  - Cost stats (today, estimated savings)
  - Configured models
  - Uptime
- Write tests

### Task 2.8: Wire Observability into Container
- Update `container.py`:
  - `IEventEmitter` → `WebSocketEmitter`
  - `ITracer` → `LangfuseTracer`
  - `IRepository` → `SQLiteRepository`
- Verify: send request → events appear on WebSocket → trace appears in Langfuse → stats in /status

### Task 2.9: End-to-End Verification
- Start all services (router + Ollama + Langfuse)
- Connect WebSocket client (e.g., `websocat ws://localhost:8000/ws/events`)
- Send request via curl
- Verify:
  - Events stream on WebSocket
  - Trace visible in Langfuse dashboard (localhost:3000)
  - `/status` shows updated stats
  - `/metrics` shows counters incremented

---

## Phase 3: Dashboard

**Goal:** React app with live graph, history replay, and analytics.

### Task 3.1: Project Setup & Layout
- Initialize Vite + React + TypeScript project (done in Phase 0)
- Install additional deps: `@xyflow/react`, `recharts`, `tailwindcss` (or minimal CSS)
- Create `Layout.tsx` — sidebar + main content area
- Create `Sidebar.tsx` — navigation (Live / History / Analytics)
- Create `Header.tsx` — project name + connection status indicator
- Set up React Router for view switching
- Verify: app renders with navigation between empty views

### Task 3.2: TypeScript Types
- Define `types/events.ts` — all WebSocket event types
- Define `types/traces.ts` — Langfuse trace/span types
- Define `types/models.ts` — model, config, stats types

### Task 3.3: WebSocket Hook
- Create `hooks/useWebSocket.ts`:
  - Connect to `ws://localhost:8000/ws/events`
  - Auto-reconnect on disconnect
  - Parse incoming events
  - Expose: `events[]`, `isConnected`, `lastEvent`
- Verify: hook connects and receives events when requests are made

### Task 3.4: Live View — Graph Component
- Create `components/live/LiveGraph.tsx`:
  - React Flow canvas with nodes: BYPASS → CLASSIFY → ROUTE → GENERATE
  - Nodes start in "idle" state (grey)
  - On WebSocket events, update node states:
    - `classify_start` → CLASSIFY node turns yellow (running)
    - `classify_complete` → CLASSIFY node turns green (done)
    - `forward_start` → GENERATE node turns yellow
    - `forward_complete` → GENERATE node turns green
  - Show latency and model name on completed nodes
  - Reset nodes on new request
- Create `components/live/GraphNode.tsx` — custom node with status indicator
- Verify: send request, see nodes light up in sequence

### Task 3.5: Live View — Detail Panel
- Create `components/live/NodeDetail.tsx`:
  - On node click, show detail panel
  - Display: input preview, output preview, model, tier, latency, cost, tokens
- Show active sessions count
- Show running cost total

### Task 3.6: Langfuse API Hook
- Create `hooks/useLangfuse.ts`:
  - Fetch sessions: `GET /api/public/sessions`
  - Fetch traces for session: `GET /api/public/traces?sessionId=X`
  - Fetch observations for trace: `GET /api/public/observations?traceId=X`
  - Handle loading/error states
- Create `utils/api.ts` — HTTP client configured with Langfuse host + keys
- Verify: hook fetches real data from Langfuse

### Task 3.7: History View — Session List
- Create `components/history/SessionList.tsx`:
  - Fetch sessions from Langfuse
  - Display list: session ID, date, turn count, total cost
  - Click session → load its timeline
- Verify: past sessions appear in list

### Task 3.8: History View — Timeline
- Create `components/history/HistoryView.tsx`:
  - Display selected session as horizontal timeline
  - Each turn = a node: show model used, cost, tier
  - Highlight model switches
  - Show Hermes tool executions between turns (from OTel spans)
- Create `components/history/TurnCard.tsx`:
  - On turn click, show full detail: prompt, response, model, tokens, cost, latency
- Verify: clicking a session shows its full timeline with details

### Task 3.9: Analytics View — Charts
- Create `components/analytics/Analytics.tsx` — main analytics layout
- Create `components/analytics/CostChart.tsx`:
  - Line chart: cost per day (last 7/30 days)
  - Breakdown by model (stacked)
- Create `components/analytics/TierPieChart.tsx`:
  - Pie chart: % low vs % high
- Create `components/analytics/LatencyChart.tsx`:
  - Histogram: classification latency distribution
- Data source: `/status` endpoint + Langfuse metrics API
- Verify: charts render with real data

### Task 3.10: Stats Hook
- Create `hooks/useStats.ts`:
  - Poll `GET /status` every 5 seconds
  - Expose: total requests, cost today, tier split, savings estimate
- Display key stats in header or sidebar

### Task 3.11: Polish & Responsiveness
- Ensure dashboard works at common screen sizes
- Add loading states and error boundaries
- Add "no data" empty states
- Connection status indicator (green = WS connected, red = disconnected)
- Verify: dashboard is usable and informative

---

## Phase 4: Integration & Deployment

**Goal:** Docker Compose deployment, Hermes integration, CLI, documentation.

### Task 4.1: Router Dockerfile
- Create `router/Dockerfile`:
  - Base: `python:3.12-slim`
  - Copy requirements, install deps
  - Copy app code
  - Expose port 8000
  - CMD: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Verify: `docker build` succeeds, container starts

### Task 4.2: Dashboard Dockerfile
- Create `dashboard/Dockerfile`:
  - Stage 1: `node:20-alpine` — build (`npm run build`)
  - Stage 2: `nginx:alpine` — serve static files
  - Expose port 3001
- Verify: `docker build` succeeds, dashboard accessible

### Task 4.3: Docker Compose (Full Stack)
- Update `docker-compose.yaml` with all services:
  - `schitzo-router` (build from ./router, port 8000)
  - `dashboard` (build from ./dashboard, port 3001)
  - `ollama` (image, port 11434, volume for models)
  - `langfuse` (image, port 3000)
  - `langfuse-db` (postgres, port 5432)
- Add health checks for each service
- Add `depends_on` with conditions
- Verify: `docker compose up` starts everything, all services healthy

### Task 4.4: Ollama Model Auto-Pull
- Add init script or entrypoint that pulls `qwen2.5:7b` if not present
- Or document manual step: `docker compose exec ollama ollama pull qwen2.5:7b`
- Verify: classifier works after fresh `docker compose up`

### Task 4.5: CLI Tool
- Create `router/app/cli.py` using `click` or `argparse`:
  - `schitzo setup` — interactive wizard (ask for API keys, select models, write config)
  - `schitzo serve` — start the router
  - `schitzo status` — show current config and stats
  - `schitzo test` — send test request to verify routing works
  - `schitzo classify "prompt"` — classify a prompt without routing
- Verify: each command works

### Task 4.6: Config Hot-Reload
- Implement file watcher on `config.yaml` using `watchfiles`
- On change: reload config, update model registry, log "Config reloaded"
- No restart needed
- Verify: change config.yaml → router picks up new values

### Task 4.7: Hermes Integration Guide
- Create `docs/hermes-setup.md`:
  - How to configure Hermes to point at Schitzo (`base_url: http://localhost:8000/v1`)
  - How to verify it's working
  - How to enable Hermes OTel → Langfuse (for unified traces)
  - Troubleshooting common issues
- Verify: follow the guide from scratch, Hermes routes through Schitzo

### Task 4.8: README & Documentation
- Write full `README.md`:
  - What it is (one paragraph)
  - Quick start (5 steps)
  - Architecture diagram
  - Configuration reference
  - CLI reference
  - Dashboard screenshots (or descriptions)
  - Contributing guide
- Create `CHANGELOG.md` with v1.0.0 entry
- Verify: a new user can follow README and get running

### Task 4.9: Final End-to-End Test
- Fresh machine simulation:
  1. Clone repo
  2. `cp .env.example .env` → fill in one API key
  3. `docker compose up`
  4. Wait for services to be healthy
  5. Configure Hermes → point at localhost:8000
  6. Send prompts via Hermes (terminal)
  7. Verify: routing works, dashboard shows live graph, Langfuse has traces
- Document any issues found and fix them

---

## Phase Summary

| Phase | Tasks | Estimated Effort | Depends On |
|-------|-------|-----------------|------------|
| Phase 0: Setup | 8 tasks | 1-2 days | Nothing |
| Phase 1: Core Router | 12 tasks | 3-4 days | Phase 0 |
| Phase 2: Observability | 9 tasks | 2-3 days | Phase 1 |
| Phase 3: Dashboard | 11 tasks | 4-5 days | Phase 2 |
| Phase 4: Integration | 9 tasks | 2-3 days | Phase 1 + 2 + 3 |
| **Total** | **49 tasks** | **12-17 days** | |
