# Schitzo Neural Router

A high-performance AI model routing proxy with real-time observability and intelligent request classification.

## Features

- **Intelligent Routing**: Automatically routes requests to optimal models based on content analysis
- **Real-time Dashboard**: Live visualization of routing pipeline and performance metrics
- **Observability**: Complete tracing with Langfuse integration and Prometheus metrics
- **OpenAI Compatible**: Drop-in replacement for OpenAI API endpoints
- **Cost Optimization**: Smart model selection to minimize costs while maintaining quality

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Dashboard  │    │    Router    │    │  Langfuse   │
│   (React)   │◄──►│  (FastAPI)   │◄──►│ (Postgres)  │
└─────────────┘    └──────────────┘    └─────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │   Models     │
                   │ (Ollama/API) │
                   └──────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for development)
- Node.js 18+ (for dashboard development)
- Ollama with Qwen 2.5 7B model (for classification)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd SchitzoNeuralRouter
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file:
```bash
# Required: Moonshot API key for model access
MOONSHOT_API_KEY=your_moonshot_api_key_here

# Optional: Langfuse keys (will be generated if not provided)
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=

# Optional: Ollama configuration
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### 3. Start Services

```bash
# Using CLI tool (recommended)
python schitzo-cli.py start

# Or using Docker Compose directly
docker compose up -d
```

### 4. Access Services

- **Dashboard**: http://localhost (main interface)
- **Router API**: http://localhost:8000 (OpenAI-compatible endpoints)
- **Langfuse**: http://localhost:3000 (observability platform)

## Usage

### API Endpoints

The router provides OpenAI-compatible endpoints:

```bash
# Chat completions
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# List available models
curl http://localhost:8000/v1/models

# Health check
curl http://localhost:8000/health
```

### Model Configuration

Edit `config.yaml` to configure available models and routing rules:

```yaml
models:
  tiers:
    tier1:  # High-performance models
      - provider: moonshot
        model: moonshot-v1-128k
        cost_per_1k_tokens: 0.012
    tier2:  # Balanced models
      - provider: ollama
        model: qwen2.5:7b
        cost_per_1k_tokens: 0.0

routing:
  bypass_keywords:
    - "ollama"
    - "local"
  
  classification:
    provider: ollama
    model: qwen2.5:7b
    endpoint: http://localhost:11434
```

### CLI Management

```bash
# Start all services
python schitzo-cli.py start

# Check service status
python schitzo-cli.py status

# View logs
python schitzo-cli.py logs

# Test the router
python schitzo-cli.py test

# Stop services
python schitzo-cli.py stop
```

## Development

### Backend Development

```bash
cd router
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd dashboard
npm install
npm run dev
```

### Architecture Overview

The system follows Clean Architecture principles:

```
router/
├── app/
│   ├── domain/          # Business entities and interfaces
│   ├── application/     # Use cases and business logic
│   ├── infrastructure/  # External integrations
│   └── presentation/    # API endpoints and schemas
```

Key components:

- **RoutePromptUseCase**: Main orchestrator for request routing
- **OllamaClassifier**: Qwen 2.5 7B model for content classification
- **LiteLLMForwarder**: Multi-provider model request forwarding
- **WebSocketEmitter**: Real-time event streaming
- **LangfuseTracer**: Request tracing and observability

## Monitoring

### Metrics

Prometheus metrics available at `/metrics`:

- `router_requests_total`: Total requests processed
- `router_request_duration_seconds`: Request processing time
- `router_model_usage_total`: Model usage by provider/model
- `router_cost_total_usd`: Total cost in USD

### Tracing

All requests are traced in Langfuse with:

- Request/response payloads
- Model selection reasoning
- Performance metrics
- Cost tracking

### Real-time Events

WebSocket events at `/ws/events`:

- `request_received`: New request arrived
- `bypass_detected`: Bypass keyword detected
- `classification_complete`: Content classification finished
- `model_selected`: Target model chosen
- `request_forwarded`: Request sent to model
- `response_received`: Model response received

## Deployment

### Production Deployment

1. **Configure Environment**:
   ```bash
   # Production environment variables
   LANGFUSE_PUBLIC_KEY=pk_prod_...
   LANGFUSE_SECRET_KEY=sk_prod_...
   MOONSHOT_API_KEY=your_production_key
   ```

2. **Deploy with Docker Compose**:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

3. **Set up Reverse Proxy** (nginx/traefik) for HTTPS and load balancing

4. **Configure Monitoring** with Prometheus and Grafana

### Scaling

- **Horizontal**: Run multiple router instances behind a load balancer
- **Vertical**: Increase container resources for higher throughput
- **Database**: Use external PostgreSQL for Langfuse in production

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**:
   ```bash
   # Check Ollama is running
   curl http://localhost:11434/api/tags
   
   # Pull required model
   ollama pull qwen2.5:7b
   ```

2. **Langfuse Not Accessible**:
   ```bash
   # Check database connection
   docker compose logs langfuse-db
   
   # Restart services
   python schitzo-cli.py restart
   ```

3. **Dashboard Not Loading**:
   ```bash
   # Check router API is accessible
   curl http://localhost:8000/health
   
   # Check WebSocket connection
   python schitzo-cli.py logs dashboard
   ```

### Logs

```bash
# All services
python schitzo-cli.py logs

# Specific service
python schitzo-cli.py logs router
python schitzo-cli.py logs dashboard
python schitzo-cli.py logs langfuse
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the existing architecture
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: GitHub Issues
- **Documentation**: See `/docs` directory
- **Community**: Discord/Slack (links TBD)