# Agent Protocol - Schitzo Neural Router

## Auto-Spawn Protocol

### Core Management Agents

#### @PO (Product Owner) Agent
**Trigger:** When user mentions `@PO` in any message
**Action:** Immediately spawn PO subagent with:
- Current project context
- Specific question/topic from user message
- Full access to .specs/ requirements
- Product decision-making authority

**Role:** 
- Validate requirements alignment
- Make product decisions
- Ensure business value delivery
- Approve feature changes

#### @PM (Project Manager) Agent  
**Trigger:** When user mentions `@PM` in any message
**Action:** Immediately spawn PM subagent with:
- Current implementation progress
- Phase status and dependencies
- Specific question/topic from user message
- Timeline and quality gate context

**Role:**
- Track 49-task progress
- Manage phase dependencies
- Coordinate timeline
- Enforce quality gates

### Technical Specialist Agents

#### @BackendArch (Backend Architecture)
**Trigger:** When user mentions `@BackendArch` in any message
**Role:** Clean Architecture, async Python, FastAPI, domain-driven design, LiteLLM integration
**Critical For:** Phase 1 (Core Router), Phase 2 (Observability)

#### @FrontendReact (Frontend React)
**Trigger:** When user mentions `@FrontendReact` in any message  
**Role:** React, TypeScript, React Flow, WebSocket integration, real-time dashboards
**Critical For:** Phase 3 (Dashboard)

#### @DevOpsInfra (DevOps Infrastructure)
**Trigger:** When user mentions `@DevOpsInfra` in any message
**Role:** Docker Compose, Ollama deployment, service orchestration, health checks
**Critical For:** Phase 0 (Setup), Phase 4 (Integration)

#### @ObservabilityEng (Observability Engineering)
**Trigger:** When user mentions `@ObservabilityEng` in any message
**Role:** Langfuse integration, trace correlation, WebSocket events, Prometheus metrics
**Critical For:** Phase 2 (Observability)

#### @IntegrationQA (Integration Quality Assurance)
**Trigger:** When user mentions `@IntegrationQA` in any message
**Role:** End-to-end testing, API compatibility, Hermes integration, system validation
**Critical For:** All phases (continuous testing)

#### @PerfLatency (Performance & Latency)
**Trigger:** When user mentions `@PerfLatency` in any message
**Role:** <500ms routing targets, classification optimization, async performance
**Critical For:** Phase 1 (Core Router), Phase 2 (Observability)

## Implementation
```
User message contains "@PO" → spawn_subagent(role="kiro_planner", context="PO duties + user question")
User message contains "@PM" → spawn_subagent(role="kiro_planner", context="PM duties + user question")
User message contains "@BackendArch" → spawn_subagent(role="trustall", context="Backend Architecture + user question")
User message contains "@FrontendReact" → spawn_subagent(role="trustall", context="Frontend React + user question")
User message contains "@DevOpsInfra" → spawn_subagent(role="trustall", context="DevOps Infrastructure + user question")
User message contains "@ObservabilityEng" → spawn_subagent(role="trustall", context="Observability Engineering + user question")
User message contains "@IntegrationQA" → spawn_subagent(role="trustall", context="Integration QA + user question")
User message contains "@PerfLatency" → spawn_subagent(role="trustall", context="Performance & Latency + user question")
```

## Examples
```
User: "@PO should we add caching to the router?"
→ Spawns PO to evaluate caching against MVP requirements

User: "@PM are we ready for Phase 2?"  
→ Spawns PM to assess Phase 1 completion and dependencies

User: "@BackendArch how should we structure the domain layer?"
→ Spawns Backend Architecture specialist for Clean Architecture guidance

User: "@FrontendReact what's the best way to handle WebSocket reconnection?"
→ Spawns Frontend React specialist for real-time dashboard expertise

User: "@DevOpsInfra Docker Compose isn't starting Langfuse"
→ Spawns DevOps Infrastructure specialist for container orchestration

User: "@ObservabilityEng how do we correlate Langfuse traces?"
→ Spawns Observability Engineering specialist for tracing setup

User: "@IntegrationQA test the full routing pipeline"
→ Spawns Integration QA specialist for end-to-end validation

User: "@PerfLatency classification is taking 800ms"
→ Spawns Performance & Latency specialist for optimization
```

## Agent Team Structure
```
Management Layer:    @PO, @PM
Technical Layer:     @BackendArch, @FrontendReact, @DevOpsInfra
Quality Layer:       @ObservabilityEng, @IntegrationQA, @PerfLatency
```

## Status: ACTIVE
All 8 agents are created and ready. This protocol is active for the Schitzo Neural Router project implementation.

## Task Assignments
See `task-assignments.md` for complete mapping of all 49 tasks to responsible agents:
- **@BackendArch**: 17 tasks (Core router, domain logic, APIs)
- **@FrontendReact**: 12 tasks (Dashboard, React components, WebSocket)
- **@DevOpsInfra**: 8 tasks (Docker, deployment, infrastructure)
- **@ObservabilityEng**: 6 tasks (Langfuse, metrics, events)
- **@IntegrationQA**: 5 tasks (Testing, validation, documentation)
- **@PerfLatency**: Cross-cutting performance reviews
- **@PM**: Coordination and phase management
- **@PO**: Product decisions and approvals

## Execution Protocol
When executing any task:
1. Mention the responsible agent (e.g., "@BackendArch implement Task 1.1")
2. Agent spawns with task context and expertise
3. Agent provides implementation guidance or executes the task
4. @PM tracks progress and dependencies
5. @PO validates alignment with requirements