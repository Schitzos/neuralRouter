# 06 — Tech Stack & Dependencies

## Core Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Router Backend | Python 3.11+ / FastAPI | Main proxy server |
| Classifier | Qwen 2.5 7B via Ollama | Prompt complexity classification |
| Model Gateway | LiteLLM | Unified interface to all providers |
| Observability | Langfuse (self-hosted) | Traces, cost tracking, analytics |
| Real-time | WebSocket (FastAPI native) | Live event streaming |
| Dashboard Frontend | React + React Flow | Live graph visualization |
| Containerization | Docker Compose | Local deployment of all services |

## Python Dependencies

### Core
```
fastapi>=0.115.0
uvicorn>=0.30.0
litellm>=1.40.0
pyyaml>=6.0
python-dotenv>=1.0.0
httpx>=0.27.0
websockets>=12.0
```

### Observability
```
langfuse>=2.40.0
opentelemetry-api>=1.25.0
opentelemetry-sdk>=1.25.0
prometheus-client>=0.20.0
```

### Utilities
```
pydantic>=2.7.0
watchfiles>=0.22.0       # config hot-reload
```

### Dev
```
pytest>=8.0.0
pytest-asyncio>=0.23.0
ruff>=0.5.0              # linting
```

## Frontend Dependencies

### React Dashboard
```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@xyflow/react": "^12.0.0",
    "recharts": "^2.12.0"
  },
  "devDependencies": {
    "vite": "^5.4.0",
    "typescript": "^5.5.0"
  }
}
```

## External Services

### Ollama (local)
- Runs Qwen 2.5 7B for classification
- Default: `http://localhost:11434`
- ~4.5 GB VRAM / RAM required for 7B model
- Install: `ollama pull qwen2.5:7b`

### Langfuse (self-hosted)
- Docker Compose deployment
- Postgres + Langfuse server
- Default: `http://localhost:3000`
- Storage: Postgres (included in Docker Compose)

### Model Providers (external APIs)
- OpenAI: `https://api.openai.com/v1`
- Anthropic: `https://api.anthropic.com/v1`
- Google: `https://generativelanguage.googleapis.com/v1`
- Groq: `https://api.groq.com/openai/v1`
- Ollama (local models): `http://localhost:11434`

## Docker Compose Services

```yaml
services:
  schitzo-router:
    build: ./router
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - ollama
      - langfuse

  dashboard:
    build: ./dashboard
    ports:
      - "3001:3001"
    depends_on:
      - schitzo-router

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

  langfuse:
    image: langfuse/langfuse
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@langfuse-db:5432/langfuse
    depends_on:
      - langfuse-db

  langfuse-db:
    image: postgres:16
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=langfuse
    volumes:
      - langfuse_db_data:/var/lib/postgresql/data

volumes:
  ollama_data:
  langfuse_db_data:
```

## Project Structure

```
SchitzoNeuralRouter/
├── specs/                    # This documentation
├── router/                   # Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app entry
│   │   ├── api/
│   │   │   ├── completions.py   # /v1/chat/completions
│   │   │   ├── models.py        # /v1/models
│   │   │   ├── health.py        # /health, /status
│   │   │   └── websocket.py     # /ws/events
│   │   ├── core/
│   │   │   ├── classifier.py    # Qwen 2.5 7B classification
│   │   │   ├── router.py        # Tier → model resolution
│   │   │   ├── bypass.py        # Keyword bypass detection
│   │   │   ├── forwarder.py     # LiteLLM forwarding
│   │   │   └── fallback.py      # Fallback chain logic
│   │   ├── observability/
│   │   │   ├── events.py        # Event emitter
│   │   │   ├── langfuse.py      # Langfuse integration
│   │   │   └── metrics.py       # Prometheus metrics
│   │   └── config/
│   │       ├── settings.py      # Config loading
│   │       └── models.py        # Model registry
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── dashboard/                # React frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── LiveGraph.tsx     # React Flow live view
│   │   │   ├── HistoryView.tsx   # Session replay
│   │   │   └── Analytics.tsx     # Charts and metrics
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts   # WS connection
│   │   │   └── useLangfuse.ts    # Langfuse API queries
│   │   └── types/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yaml
├── config.yaml               # Default configuration
├── .env.example
└── README.md
```

## System Requirements

### Minimum
- CPU: 4 cores
- RAM: 8 GB (Ollama needs ~5 GB for 7B model)
- Disk: 10 GB (model weights + Langfuse DB)
- Python 3.11+
- Docker & Docker Compose

### Recommended
- CPU: 8 cores
- RAM: 16 GB
- GPU: Optional (speeds up Ollama classification)
- SSD for Ollama model loading
