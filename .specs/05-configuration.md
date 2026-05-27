# 05 — Configuration & Model Registry

## Overview

Schitzo Neural Router uses a YAML config file for model registry and routing rules, plus a `.env` file for secrets.

## File Locations

```
~/.schitzo/
├── config.yaml          # Main configuration
├── .env                 # API keys and secrets
└── logs/                # Request logs (optional)
```

Or project-local:
```
./schitzo.yaml           # Project-specific config (overrides global)
./.env                   # Project-specific secrets
```

Priority: project-local > global (`~/.schitzo/`)

---

## config.yaml

```yaml
# Schitzo Neural Router Configuration

server:
  host: "0.0.0.0"
  port: 8000
  auth_token: ""  # empty = no auth (use .env for secrets)

# Classifier settings
classifier:
  model: "qwen2.5:7b"
  ollama_url: "http://localhost:11434"
  timeout_ms: 2000
  default_on_failure: "high"  # if classifier fails, assume high

# Tier configuration
tiers:
  chat:
    models:
      - "ollama/qwen2.5:7b"
    description: "Casual conversation, greetings, small talk, confirmations"

  low:
    models:
      - "claude-haiku"
      - "gpt-4o-mini"
      - "gemini-2.5-flash"
    description: "Simple Q&A, formatting, translation, short answers"

  high:
    models:
      - "claude-opus-4"
      - "gpt-4o"
      - "gemini-2.5-pro"
    description: "Complex reasoning, architecture, code generation"

# Default model for each tier (first in the list)
routing:
  chat_default: "ollama/qwen2.5:7b"
  low_default: "claude-haiku"
  high_default: "claude-opus-4"

# Fallback chains (tried in order on failure)
fallback:
  low:
    - "claude-haiku"
    - "gpt-4o-mini"
    - "gemini-2.5-flash"
  high:
    - "claude-opus-4"
    - "gpt-4o"
    - "gemini-2.5-pro"

# Bypass keyword mappings
bypass:
  "use codex to": "openai-codex"
  "use claude to": "claude-opus-4"
  "use gemini to": "gemini-2.5-pro"
  "use gpt to": "gpt-4o"
  "use haiku to": "claude-haiku"
  "use sonnet to": "claude-sonnet-4"
  "use opus to": "claude-opus-4"
  "use ollama to": "ollama/qwen2.5:7b"

# Observability
observability:
  websocket: true
  langfuse:
    enabled: true
    host: "http://localhost:3000"
    public_key: ""   # use .env
    secret_key: ""   # use .env

# Timeouts
timeouts:
  classification_ms: 2000
  model_request_s: 30
  stream_idle_s: 60

# Logging
logging:
  level: "info"  # debug, info, warn, error
  log_prompts: false  # log full prompts (privacy concern)
  log_dir: "~/.schitzo/logs"
```

---

## .env

```bash
# Model Provider API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
GROQ_API_KEY=gsk_...

# Ollama (local, no key needed)
OLLAMA_BASE_URL=http://localhost:11434

# Langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://localhost:3000

# Router Auth (optional)
SCHITZO_AUTH_TOKEN=

# LiteLLM settings (optional overrides)
LITELLM_LOG_LEVEL=WARNING
```

---

## Model Registry

### Model Definition

Each model known to the router:

```yaml
# models section in config.yaml (or separate models.yaml)
models:
  claude-opus-4:
    provider: "anthropic"
    litellm_model: "claude-opus-4-20250514"
    tier: "high"
    max_tokens: 200000
    cost_per_1m_input: 15.00
    cost_per_1m_output: 75.00
    supports_streaming: true
    supports_tools: true
    supports_vision: true

  claude-haiku:
    provider: "anthropic"
    litellm_model: "claude-haiku-4-20250514"
    tier: "low"
    max_tokens: 200000
    cost_per_1m_input: 0.25
    cost_per_1m_output: 1.25
    supports_streaming: true
    supports_tools: true
    supports_vision: true

  gpt-4o:
    provider: "openai"
    litellm_model: "gpt-4o"
    tier: "high"
    max_tokens: 128000
    cost_per_1m_input: 2.50
    cost_per_1m_output: 10.00
    supports_streaming: true
    supports_tools: true
    supports_vision: true

  gpt-4o-mini:
    provider: "openai"
    litellm_model: "gpt-4o-mini"
    tier: "low"
    max_tokens: 128000
    cost_per_1m_input: 0.15
    cost_per_1m_output: 0.60
    supports_streaming: true
    supports_tools: true
    supports_vision: true

  gemini-2.5-pro:
    provider: "google"
    litellm_model: "gemini/gemini-2.5-pro"
    tier: "high"
    max_tokens: 1000000
    cost_per_1m_input: 1.25
    cost_per_1m_output: 10.00
    supports_streaming: true
    supports_tools: true
    supports_vision: true

  gemini-2.5-flash:
    provider: "google"
    litellm_model: "gemini/gemini-2.5-flash"
    tier: "low"
    max_tokens: 1000000
    cost_per_1m_input: 0.15
    cost_per_1m_output: 0.60
    supports_streaming: true
    supports_tools: true
    supports_vision: true

  openai-codex:
    provider: "openai"
    litellm_model: "openai-codex"
    tier: "high"
    max_tokens: 200000
    cost_per_1m_input: 3.00
    cost_per_1m_output: 15.00
    supports_streaming: true
    supports_tools: true
    supports_vision: false

  ollama/qwen2.5:7b:
    provider: "ollama"
    litellm_model: "ollama/qwen2.5:7b"
    tier: "low"
    max_tokens: 32768
    cost_per_1m_input: 0
    cost_per_1m_output: 0
    supports_streaming: true
    supports_tools: true
    supports_vision: false
```

### Hot Reload

- Config file changes are detected via file watcher
- Model registry updates without restarting the router
- Log message on reload: `"Config reloaded: 8 models registered"`

---

## Environment Variables (override config)

| Variable | Overrides | Example |
|----------|-----------|---------|
| `SCHITZO_PORT` | `server.port` | `8000` |
| `SCHITZO_LOW_MODEL` | `routing.low_default` | `claude-haiku` |
| `SCHITZO_HIGH_MODEL` | `routing.high_default` | `claude-opus-4` |
| `SCHITZO_CLASSIFIER_MODEL` | `classifier.model` | `qwen2.5:7b` |
| `SCHITZO_CLASSIFIER_TIMEOUT` | `classifier.timeout_ms` | `2000` |
| `SCHITZO_AUTH_TOKEN` | `server.auth_token` | `my-secret` |
| `SCHITZO_LOG_LEVEL` | `logging.level` | `debug` |

Environment variables take precedence over config file values.

---

## CLI Quick Config

```bash
# First-time setup wizard
schitzo setup

# Set models quickly
schitzo config set routing.low_default gpt-4o-mini
schitzo config set routing.high_default claude-opus-4

# Add API key
schitzo auth add openai sk-...
schitzo auth add anthropic sk-ant-...

# Test configuration
schitzo test

# Show current config
schitzo status
```
