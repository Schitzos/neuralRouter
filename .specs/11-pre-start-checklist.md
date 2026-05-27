# 11 — Pre-Start Checklist

## Before Autonomous Implementation

These are the only manual steps required from you. Everything else Kiro handles.

### Step 1: Docker Desktop (one-time)
- After Kiro installs Docker, **open Docker Desktop manually**
- Accept the license agreement
- Grant system permissions when prompted
- Wait until Docker icon shows "running" in menu bar

### Step 2: Langfuse Account (one-time)
- After Kiro starts Langfuse via Docker Compose
- Open `http://localhost:3000` in your browser
- Create an admin account (email + password)
- Create a project (e.g., "Schitzo Neural Router")
- Copy the **Public Key** and **Secret Key** from project settings
- Paste them to Kiro (will be saved in `.env`)

### Confirm Before Starting

- [ ] ~10 GB disk space free
- [ ] Ports 8000, 3000, 3001, 11434 are available
- [ ] Kimi API key is in `.env` ✅ (already done)

### What Kiro Does Autonomously

- Install Python, Node, Docker, Ollama via brew
- Pull Qwen 2.5 7B model
- Create all project files (backend + frontend)
- Set up Docker Compose (Langfuse + Postgres)
- Run tests
- Start all services
- Build and verify everything end-to-end

### Credentials Available

| Provider | Key | Status |
|----------|-----|--------|
| Kimi/Moonshot | `sk-Jpj...FZB` | ✅ Ready |
| OpenAI | — | ❌ Not provided |
| Anthropic | — | ❌ Not provided |
| Google Gemini | — | ❌ Not provided |
| Langfuse | — | ⏳ Created after Step 2 |
