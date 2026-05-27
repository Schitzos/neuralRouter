# 01 — System Overview & Architecture

## Purpose

Schitzo Neural Router is a transparent AI routing proxy that sits between Hermes Agent and model providers. It classifies prompt complexity using a local 7B model and routes to the optimal model (cheap or expensive) to minimize cost without sacrificing quality.

## System Context

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                                   │
│         Terminal          Telegram          Web Dashboard                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         HERMES AGENT                                      │
│                                                                          │
│  • Receives user input from all channels                                 │
│  • Manages conversation memory (persistent across sessions)              │
│  • Executes tools (70+ built-in)                                         │
│  • Creates and reuses skills (self-improving)                            │
│  • Builds full LLM payload (system prompt + tools + memory + history)    │
│  • Sends OpenAI-compatible requests to configured endpoint               │
│                                                                          │
│  Config: base_url = http://localhost:8000/v1                             │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ POST /v1/chat/completions
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SCHITZO NEURAL ROUTER                                  │
│                    (localhost:8000)                                        │
│                                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────┐    │
│  │  BYPASS    │  │ CLASSIFIER │  │   ROUTER   │  │   FORWARDER    │    │
│  │  DETECTOR  │→ │ (Qwen 7B)  │→ │            │→ │  (LiteLLM)     │    │
│  └────────────┘  └────────────┘  └────────────┘  └────────────────┘    │
│         │                                                │               │
│         └────────────────────────────────────────────────┘               │
│                              │                                            │
│                    ┌─────────┴──────────┐                                │
│                    │   EVENT EMITTER    │                                 │
│                    └─────────┬──────────┘                                │
│                              │                                            │
└──────────────────────────────┼────────────────────────────────────────────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
                 ▼             ▼             ▼
          ┌──────────┐  ┌──────────┐  ┌──────────────┐
          │WebSocket │  │ Langfuse │  │Model Provider│
          │(live UI) │  │(history) │  │(actual LLM)  │
          └──────────┘  └──────────┘  └──────────────┘
```

## Component Responsibilities

### Hermes Agent (external, not built by us)
- Entry point for all user interactions
- Handles Terminal, Telegram, Discord, and other messaging platforms
- Manages persistent memory and skills
- Builds LLM request payloads
- Configured to point at Schitzo as its model endpoint

### Schitzo Neural Router (our system)
- Receives OpenAI-compatible requests from Hermes
- Detects bypass keywords (direct model routing)
- Classifies prompt complexity (low/high) using Qwen 2.5 7B
- Routes to appropriate model via LiteLLM
- Emits real-time events for observability
- Sends traces to Langfuse for historical analytics

### Langfuse (external, self-hosted)
- Stores all LLM traces (prompts, responses, cost, latency)
- Receives Hermes OTel spans (tool executions, memory ops)
- Provides REST API for history queries
- Built-in dashboard for cost/latency analytics
- Self-hosted via Docker Compose

### Live Dashboard (our system)
- React + React Flow frontend
- Connects to router via WebSocket for real-time updates
- Queries Langfuse API for history replay
- Three views: Live, History, Analytics

## Design Principles

1. **Transparent proxy** — Hermes doesn't know routing exists. One config change enables/disables it.
2. **Stateless router** — No conversation state in the router. Hermes manages all context.
3. **Zero-cost classification** — Qwen 2.5 7B runs locally via Ollama. No API cost.
4. **Unified observability** — Router events + Hermes OTel → same Langfuse → complete picture.
5. **Bypass escape hatch** — Users can force a specific model when needed.

## Deployment Topology

```
┌─────────────────────────────────────────┐
│  Docker Compose                          │
│                                          │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Schitzo      │  │ Ollama       │    │
│  │ Router       │  │ (Qwen 2.5 7B)│    │
│  │ :8000        │  │ :11434       │    │
│  └──────────────┘  └──────────────┘    │
│                                          │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Langfuse     │  │ Dashboard    │    │
│  │ :3000        │  │ :3001        │    │
│  └──────────────┘  └──────────────┘    │
│                                          │
└─────────────────────────────────────────┘

External:
  - Hermes Agent (runs on host, configured to hit localhost:8000)
  - Model Providers (OpenAI, Anthropic, Gemini — internet)
```
