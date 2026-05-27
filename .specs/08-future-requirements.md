# 08 — Future Requirements (Post-MVP)

## Overview

Features planned for after MVP is stable. These are scoped but not prioritized for initial implementation.

---

## Multi-User Support

### User Management
- User registration and login (email + password or OAuth)
- Each user has their own profile, API keys, and budget
- Admin role can manage all users
- User isolation — one user's requests/data are invisible to others

### Per-User API Keys
- Users add their own provider API keys via dashboard UI
- Keys stored encrypted in database (SQLite → Postgres migration)
- Router resolves which key to use based on the requesting user
- If user has no key for a provider → that provider's models are unavailable to them

### Dashboard: Provider Management UI
```
┌─────────────────────────────────────────┐
│  My Providers                            │
│                                          │
│  [+ Add Provider]                        │
│                                          │
│  Provider     Key              Status    │
│  ─────────────────────────────────────── │
│  OpenAI       sk-...abc        ✅ Valid  │
│  Anthropic    sk-ant...xy      ✅ Valid  │
│  Google       Not configured   ❌ [Add]  │
│  Groq         gsk_...ef        ⚠️ Expired│
│                                          │
│  Available models (based on your keys):  │
│  • gpt-4o, gpt-4o-mini        ✅        │
│  • claude-opus-4, claude-haiku ✅        │
│  • gemini-2.5-pro             ❌ no key  │
└─────────────────────────────────────────┘
```

### Features
- Validate API key on input (test call to provider)
- Show which models become available after adding a key
- Mask stored keys in UI (show last 4 chars only)
- Allow key rotation without downtime

---

## Budget & Spending Controls

### Per-User Budgets
- Daily spending limit (e.g., $5/day)
- Monthly spending limit (e.g., $50/month)
- Per-model limits (e.g., max $20/month on Opus)

### Behavior on Budget Exceeded
- **Soft limit (warning):** notify user, continue routing
- **Hard limit (block):** refuse expensive model, downgrade to cheaper tier
- **Fallback mode:** when budget hit, route everything to low tier until reset

### Dashboard: Budget UI
```
┌─────────────────────────────────────────┐
│  Budget & Spending                       │
│                                          │
│  Daily:   $3.42 / $10.00  [████░░] 34%  │
│  Monthly: $28.50 / $100.00 [██░░░░] 28% │
│                                          │
│  ⚠️ Alert at 80% of limit               │
│  🛑 Hard stop at 100%                   │
│                                          │
│  [Edit Limits]                           │
│                                          │
│  Spending by model (this month):         │
│  • claude-opus-4:  $18.20                │
│  • gpt-4o:         $6.30                 │
│  • claude-haiku:   $2.10                 │
│  • gpt-4o-mini:    $1.90                 │
└─────────────────────────────────────────┘
```

### Notifications
- Email/webhook when approaching limit
- Dashboard banner when near budget
- Telegram notification (via Hermes) when limit hit

---

## Authentication & Authorization

### Dashboard Auth
- Login page (email + password)
- Session-based auth (JWT tokens)
- OAuth providers (Google, GitHub) — optional
- Role-based access:
  - **Admin:** manage users, view all data, configure system
  - **User:** manage own keys, view own data, set own budget

### API Auth (multi-user)
- Each user gets a unique router API token
- Hermes configured with user's token: `Authorization: Bearer <user-token>`
- Router identifies user from token → loads their keys, budget, preferences

---

## Team Features

### Shared Workspace
- Team members share a pool of API keys
- Shared budget with per-member sub-limits
- Team-wide analytics (who's spending what)

### Audit Log
- Who made what request, when, which model, how much
- Exportable for billing/compliance

---

## Advanced Routing

### Three-Tier Routing
- Add `medium` tier between low and high
- Classifier outputs: `low`, `medium`, `high`
- More granular cost optimization

### Custom Routing Rules
- User-defined rules: "if prompt contains 'code' → always use Sonnet"
- Time-based rules: "after 10pm, use only cheap models"
- Context-based: "if conversation > 20 turns, use model with largest context window"

### Model Preferences
- Per-user model preferences: "I prefer Claude over GPT for code"
- Tier overrides: "my low tier should be Gemini Flash, not Haiku"
- Configurable via dashboard

---

## Enhanced Observability

### Comparison View
- Side-by-side: same prompt sent to two models, compare quality
- A/B testing: randomly route X% to model A, Y% to model B

### Quality Feedback Loop
- User rates responses (👍/👎) in dashboard
- Feedback stored in Langfuse as scores
- Over time: adjust routing based on quality data

### Alerts
- Slack/Telegram notification on anomalies (sudden cost spike, high error rate)
- Configurable alert rules

---

## Database Migration

### SQLite → Postgres
- When multi-user is needed, migrate from SQLite to Postgres
- Langfuse already uses Postgres — could share the instance
- Migration script provided

### Schema (future)

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT DEFAULT 'user',
  created_at TIMESTAMP DEFAULT NOW()
);

-- API Keys (per user, per provider)
CREATE TABLE provider_keys (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  provider TEXT NOT NULL,
  api_key_encrypted TEXT NOT NULL,
  is_valid BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Budgets
CREATE TABLE budgets (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  daily_limit_usd DECIMAL,
  monthly_limit_usd DECIMAL,
  hard_stop BOOLEAN DEFAULT true
);

-- Spending log
CREATE TABLE spending (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  request_id TEXT,
  model TEXT,
  tokens_in INTEGER,
  tokens_out INTEGER,
  cost_usd DECIMAL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Platform Expansion

### Additional Input Channels
- Discord bot (direct, not via Hermes)
- Slack app
- Web chat widget (embeddable)
- REST API for programmatic access (non-chat use cases)

### Model Marketplace
- Browse all LiteLLM-supported models in dashboard
- One-click enable (if user has the provider key)
- Community-rated models (which model is best for what)

### Plugin System
- Custom classifiers (swap Qwen for another model)
- Custom routing logic (user-defined Python functions)
- Pre/post processing hooks (modify prompts before sending, modify responses before returning)

---

## Priority Order (suggested)

1. Multi-user + per-user API keys (enables sharing the tool)
2. Budget controls (prevents bill shock)
3. Dashboard auth (required for multi-user)
4. Three-tier routing (better cost optimization)
5. Quality feedback loop (improves routing over time)
6. Team features (if demand exists)
7. Platform expansion (based on user needs)
