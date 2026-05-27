# Task Assignments - Schitzo Neural Router

## Phase 0: Project Setup (8 tasks)

- **Task 0.1**: Install System Dependencies → @DevOpsInfra
- **Task 0.2**: Setup Ollama & Pull Classifier Model → @DevOpsInfra  
- **Task 0.3**: Initialize Python Backend → @BackendArch
- **Task 0.4**: Initialize React Frontend → @FrontendReact
- **Task 0.5**: Docker Compose Setup → @DevOpsInfra
- **Task 0.6**: Project Scaffolding → @BackendArch
- **Task 0.7**: Configuration Files → @BackendArch
- **Task 0.8**: Dev Tooling → @DevOpsInfra

## Phase 1: Core Router (12 tasks)

- **Task 1.1**: Domain Layer — Entities → @BackendArch
- **Task 1.2**: Domain Layer — Interfaces → @BackendArch
- **Task 1.3**: Bypass Detection → @BackendArch
- **Task 1.4**: Classifier Implementation → @BackendArch
- **Task 1.5**: Prompt Extraction → @BackendArch
- **Task 1.6**: Router Logic → @BackendArch
- **Task 1.7**: LiteLLM Forwarder → @BackendArch
- **Task 1.8**: Fallback Handler → @BackendArch
- **Task 1.9**: API Endpoint — Completions → @BackendArch
- **Task 1.10**: API Endpoints — Models & Health → @BackendArch
- **Task 1.11**: Dependency Injection Container → @BackendArch
- **Task 1.12**: End-to-End Verification → @IntegrationQA

## Phase 2: Observability (9 tasks)

- **Task 2.1**: Event Emitter → @ObservabilityEng
- **Task 2.2**: WebSocket Endpoint → @ObservabilityEng
- **Task 2.3**: Emit Events in Pipeline → @ObservabilityEng
- **Task 2.4**: Langfuse Integration → @ObservabilityEng
- **Task 2.5**: SQLite Repository → @BackendArch
- **Task 2.6**: Prometheus Metrics → @ObservabilityEng
- **Task 2.7**: Status Endpoint → @BackendArch
- **Task 2.8**: Wire Observability into Container → @ObservabilityEng
- **Task 2.9**: End-to-End Verification → @IntegrationQA

## Phase 3: Dashboard (11 tasks)

- **Task 3.1**: Project Setup & Layout → @FrontendReact
- **Task 3.2**: TypeScript Types → @FrontendReact
- **Task 3.3**: WebSocket Hook → @FrontendReact
- **Task 3.4**: Live View — Graph Component → @FrontendReact
- **Task 3.5**: Live View — Detail Panel → @FrontendReact
- **Task 3.6**: Langfuse API Hook → @FrontendReact
- **Task 3.7**: History View — Session List → @FrontendReact
- **Task 3.8**: History View — Timeline → @FrontendReact
- **Task 3.9**: Analytics View — Charts → @FrontendReact
- **Task 3.10**: Stats Hook → @FrontendReact
- **Task 3.11**: Polish & Responsiveness → @FrontendReact

## Phase 4: Integration & Deployment (9 tasks)

- **Task 4.1**: Router Dockerfile → @DevOpsInfra
- **Task 4.2**: Dashboard Dockerfile → @DevOpsInfra
- **Task 4.3**: Docker Compose (Full Stack) → @DevOpsInfra
- **Task 4.4**: Ollama Model Auto-Pull → @DevOpsInfra
- **Task 4.5**: CLI Tool → @BackendArch
- **Task 4.6**: Config Hot-Reload → @BackendArch
- **Task 4.7**: Hermes Integration Guide → @IntegrationQA
- **Task 4.8**: README & Documentation → @IntegrationQA
- **Task 4.9**: Final End-to-End Test → @IntegrationQA

## Agent Workload Distribution

| Agent | Tasks | Phases |
|-------|-------|--------|
| @BackendArch | 17 tasks | 0,1,2,4 |
| @FrontendReact | 12 tasks | 0,3 |
| @DevOpsInfra | 8 tasks | 0,4 |
| @ObservabilityEng | 6 tasks | 2 |
| @IntegrationQA | 5 tasks | 1,2,4 |
| @PerfLatency | 0 tasks | Cross-cutting (performance review) |
| @PM | 0 tasks | Coordination & oversight |
| @PO | 0 tasks | Product decisions & approval |

## Cross-Cutting Responsibilities

- **@PerfLatency**: Reviews all tasks for performance impact, especially Tasks 1.4, 1.6, 2.3
- **@PM**: Coordinates task dependencies and phase transitions
- **@PO**: Approves product decisions and validates requirements alignment