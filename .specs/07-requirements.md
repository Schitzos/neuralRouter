# 07 — Requirements & Implementation Design

## Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | macOS / Linux | macOS (Apple Silicon for Ollama) |
| Python | 3.11+ | 3.12 |
| Node.js | 18+ | 20 LTS |
| Docker | 24+ | Latest |
| Docker Compose | v2+ | Latest |
| RAM | 8 GB | 16 GB |
| Disk | 10 GB free | 20 GB free |
| GPU | Not required | Apple Silicon / NVIDIA (speeds up Ollama) |

### Software to Install

1. **Python 3.11+** — router backend
2. **Node.js 18+** — dashboard frontend
3. **Docker & Docker Compose** — Langfuse, Postgres, (optionally Ollama)
4. **Ollama** — native install recommended on macOS for Metal GPU acceleration
5. **Qwen 2.5 7B model** — `ollama pull qwen2.5:7b` (~4.5 GB download)

### API Keys (at least one required)

| Provider | Required? | Get it at |
|----------|-----------|-----------|
| OpenAI | Recommended | https://platform.openai.com/api-keys |
| Anthropic | Recommended | https://console.anthropic.com/ |
| Google Gemini | Optional | https://aistudio.google.com/apikey |
| Groq | Optional | https://console.groq.com/ |

### External Services (self-hosted via Docker)

| Service | Purpose | Port |
|---------|---------|------|
| Langfuse | Observability, traces, analytics | 3000 |
| Postgres | Langfuse database | 5432 |
| Ollama | Classifier model (or native install) | 11434 |

---

## Implementation Phases

### Phase 1: Core Router (MVP)

**Goal:** Proxy that classifies and routes. Testable via curl.

**Deliverables:**
1. FastAPI server with `/v1/chat/completions` endpoint
2. Bypass detection (keyword matching)
3. Classifier integration (Qwen 2.5 7B via Ollama)
4. LiteLLM forwarding (to real providers)
5. Streaming support (SSE passthrough)
6. Fallback on failure
7. Basic config loading (YAML + .env)
8. `/health` and `/v1/models` endpoints

**Test:** Point any OpenAI client at `localhost:8000` and verify routing works.

```bash
# Test classification + routing
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"what is 2+2"}]}'

# Test bypass
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"use claude to design an auth system"}]}'
```

**Estimated effort:** 2-3 days

---

### Phase 2: Observability

**Goal:** Full tracing and real-time events.

**Deliverables:**
1. Langfuse integration (traces per request with nested spans)
2. WebSocket endpoint (`/ws/events`)
3. Event emission at each pipeline stage
4. Prometheus `/metrics` endpoint
5. `/status` endpoint with stats
6. Session ID tracking (correlate multi-turn conversations)

**Test:** Open WebSocket connection, send a request, see events stream in real-time. Check Langfuse dashboard for traces.

**Estimated effort:** 2-3 days

---

### Phase 3: Dashboard

**Goal:** React app with live graph, history, and analytics.

**Deliverables:**
1. React + Vite project setup
2. Live View — React Flow graph with WebSocket updates
3. History View — query Langfuse API, render session timeline
4. Analytics View — cost charts, tier distribution, latency graphs
5. Session list sidebar
6. Node click → detail panel (prompt, response, cost, model)

**Test:** Open dashboard in browser, send requests via terminal, see live graph update.

**Estimated effort:** 4-5 days

---

### Phase 4: Integration & Polish

**Goal:** Connect with Hermes, Docker Compose deployment, documentation.

**Deliverables:**
1. Docker Compose for full stack (router + dashboard + Langfuse + Postgres + Ollama)
2. Hermes configuration guide
3. Setup wizard CLI (`schitzo setup`)
4. Config hot-reload (file watcher)
5. README with installation instructions
6. `.env.example` with all variables documented

**Test:** `docker compose up` → everything works. Configure Hermes → full flow operational.

**Estimated effort:** 2-3 days

---

## Implementation Order (file by file)

### Phase 1 — Core Router

```
Step 1: Project scaffolding
  - pyproject.toml / requirements.txt
  - app/__init__.py
  - app/main.py (FastAPI app)

Step 2: Configuration
  - app/config/settings.py (load YAML + .env)
  - config.yaml (default config)
  - .env.example

Step 3: Bypass detection
  - app/core/bypass.py

Step 4: Classifier
  - app/core/classifier.py (call Ollama)

Step 5: Router logic
  - app/core/router.py (tier → model resolution)

Step 6: Forwarder
  - app/core/forwarder.py (LiteLLM call + streaming)

Step 7: Fallback
  - app/core/fallback.py

Step 8: API endpoints
  - app/api/completions.py (main endpoint, wires everything together)
  - app/api/models.py
  - app/api/health.py

Step 9: Tests
  - tests/test_bypass.py
  - tests/test_classifier.py
  - tests/test_router.py
  - tests/test_completions.py
```

### Phase 2 — Observability

```
Step 10: Event system
  - app/observability/events.py (event emitter + WebSocket broadcast)

Step 11: Langfuse
  - app/observability/langfuse.py (trace creation, span management)

Step 12: Metrics
  - app/observability/metrics.py (Prometheus counters/histograms)

Step 13: WebSocket endpoint
  - app/api/websocket.py

Step 14: Status endpoint
  - app/api/health.py (extend with /status)
```

### Phase 3 — Dashboard

```
Step 15: React project setup
  - dashboard/package.json
  - dashboard/vite.config.ts
  - dashboard/src/App.tsx

Step 16: WebSocket hook
  - dashboard/src/hooks/useWebSocket.ts

Step 17: Live graph
  - dashboard/src/components/LiveGraph.tsx

Step 18: History view
  - dashboard/src/hooks/useLangfuse.ts
  - dashboard/src/components/HistoryView.tsx

Step 19: Analytics
  - dashboard/src/components/Analytics.tsx

Step 20: Layout and navigation
  - dashboard/src/components/Layout.tsx
```

### Phase 4 — Integration

```
Step 21: Docker
  - router/Dockerfile
  - dashboard/Dockerfile
  - docker-compose.yaml

Step 22: CLI
  - app/cli.py (setup wizard, status, test commands)

Step 23: Documentation
  - README.md (full)
  - docs/hermes-setup.md
  - .env.example
```

---

## Dependency Graph

```
Phase 1 (Core Router)
  │
  ├── Phase 2 (Observability) ── depends on Phase 1
  │       │
  │       └── Phase 3 (Dashboard) ── depends on Phase 2
  │
  └── Phase 4 (Integration) ── depends on Phase 1 + 2 + 3
```

---

## Definition of Done (per phase)

### Phase 1 ✓ when:
- [ ] `curl` to `/v1/chat/completions` returns a routed response
- [ ] Bypass keywords route to correct model
- [ ] Classification returns low/high tier
- [ ] Streaming works end-to-end
- [ ] Fallback triggers on simulated failure
- [ ] Config loads from YAML + .env

### Phase 2 ✓ when:
- [ ] Langfuse shows traces with nested spans
- [ ] WebSocket streams events in real-time
- [ ] `/metrics` returns Prometheus format
- [ ] `/status` shows live stats
- [ ] Session IDs group related requests

### Phase 3 ✓ when:
- [ ] Live graph shows nodes lighting up during a request
- [ ] History view replays a past session as a timeline
- [ ] Analytics shows cost/latency charts
- [ ] Clicking a node shows details

### Phase 4 ✓ when:
- [ ] `docker compose up` starts everything
- [ ] Hermes configured and routing through Schitzo
- [ ] README covers full setup
- [ ] Setup wizard works
