<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/CrewAI-Multi--Agent-6366F1?logo=data:image/svg+xml;base64,&logoColor=white" alt="CrewAI"/>
  <img src="https://img.shields.io/badge/Gemini-AI%20Engine-4285F4?logo=google&logoColor=white" alt="Gemini"/>
  <img src="https://img.shields.io/badge/YouTube-Data%20API%20v3-FF0000?logo=youtube&logoColor=white" alt="YouTube API"/>
  <img src="https://img.shields.io/badge/Starlette-ASGI-2D3748?logo=starlette&logoColor=white" alt="Starlette"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
</p>

<h1 align="center">🎬 SEOVerse — YouTube Intelligence Studio</h1>

<p align="center">
  <strong>AI-Powered YouTube SEO & Channel Growth Platform</strong><br/>
  <em>Deploy a team of 6 specialized AI agents that research, analyze, and craft production-ready YouTube strategies — all from a single query.</em>
</p>

---

## 🌟 Overview

**SEOVerse** is a full-stack YouTube intelligence platform that combines **CrewAI multi-agent orchestration** with the **YouTube Data API v3** and **Google Gemini** to deliver comprehensive SEO strategy blueprints. Enter any topic or niche, and a coordinated team of AI agents will conduct audience analysis, competitor research, keyword mapping, metadata optimization, and produce an actionable content strategy — complete with title variations, thumbnail blueprints, and a 7-day launch calendar.

### What Makes SEOVerse Different

| Feature | Description |
|---------|-------------|
| 🤖 **6-Agent Pipeline** | Specialized agents for audience analysis, content research, competitor intelligence, SEO keywords, metadata optimization, and strategic reporting |
| 📊 **Live YouTube Data** | Real-time competitor benchmarks via YouTube Data API v3 — actual views, likes, and engagement metrics |
| 🧠 **Multi-LLM Support** | Google Gemini (default), OpenAI, Anthropic, Ollama (local), Groq, and 20+ providers via LiteLLM |
| 🔐 **Full Authentication** | JWT-based auth with email verification, password reset, and secure HttpOnly cookie sessions |
| 📈 **Analysis History** | Every analysis is saved per-user with structured data, searchable and re-viewable from the dashboard |
| 🎨 **Premium Dashboard** | Dark-mode glassmorphism UI with live competitor cards, keyword matrices, and downloadable reports |
| 🐳 **Docker Ready** | One-command containerized deployment with persistent data volumes |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (HTML/JS/CSS)                   │
│              Landing Page + Auth Modals + Research Dashboard     │
└──────────────────────────────┬──────────────────────────────────┘
                               │  REST API
┌──────────────────────────────▼──────────────────────────────────┐
│                     Starlette ASGI Server                       │
│         api_server.py — Routes, Auth, CORS, Static Files        │
├─────────────┬──────────────┬───────────────┬────────────────────┤
│  auth.py    │ email_svc.py │ youtube_data  │  report_parser.py  │
│  SQLite DB  │ SMTP / Sim   │ YT API v3     │  Structured JSON   │
└─────────────┴──────────────┴───────┬───────┴────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────┐
│                    CrewAI Sequential Pipeline                   │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  Audience &   │  │  Content     │  │  Competitor & Market  │  │
│  │  Opportunity  │─▶│  Research    │─▶│  Intelligence         │  │
│  │  Strategist   │  │  Director    │  │  Specialist           │  │
│  └──────────────┘  └──────────────┘  └───────────┬───────────┘  │
│                                                   │              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────▼───────────┐  │
│  │  Strategy     │  │  Metadata &  │  │  SEO & Search Intent  │  │
│  │  Report       │◀─│  CTR         │◀─│  Strategist           │  │
│  │  Editor       │  │  Specialist  │  │                       │  │
│  └──────────────┘  └──────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python** ≥ 3.10, < 3.14
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **YouTube Data API v3 key** — [Get one here](https://console.cloud.google.com/apis/credentials)
- **Gemini API key** — [Get one here](https://aistudio.google.com/apikey) *(or use Ollama for local inference)*

### 1. Clone the Repository

```bash
git clone https://github.com/vaishnaviG031/SEOVerse.git
cd SEOVerse
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
ENVIRONMENT=development
JWT_SECRET=your-random-secret-at-least-32-characters-long
COOKIE_SECURE=false

# AI Model (pick one)
MODEL=gemini/gemini-2.0-flash          # Google Gemini (recommended)
# MODEL=ollama/llama3.2:1b             # Local Ollama

# API Keys
YOUTUBE_API_KEY=your-youtube-api-key
GEMINI_API_KEY=your-gemini-api-key
# SERPER_API_KEY=your-serper-key       # Optional: enables web search tool

# Email (optional — dev mode returns codes in browser)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=you@gmail.com
# SMTP_PASS=your-app-password
# FROM_EMAIL=noreply@yourdomain.com
```

### 3. Install Dependencies

```bash
pip install uv          # if not already installed
uv sync
```

### 4. Start the Application

```bash
uv run uvicorn api_server:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000** in your browser.

> **Note:** Without SMTP settings configured, development mode returns verification/reset codes directly to the browser for frictionless local testing.

---

## 🤖 The 6-Agent Pipeline

Each analysis triggers a **sequential CrewAI pipeline** of 6 specialized agents:

| # | Agent | Role | What It Does |
|---|-------|------|--------------|
| 1 | **Audience & Opportunity Strategist** | YouTube Channel Analyst | Analyzes target audience demographics, viewer intent, pain points, and identifies high-growth content opportunities |
| 2 | **Content Research Director** | Video Concept Creator | Generates 5 high-retention video concepts with hooks, unique angles, and retention hypotheses |
| 3 | **Competitor & Market Intelligence** | Market Researcher | Benchmarks competitor content, identifies 3 exploitable content gaps, and maps differentiation tactics |
| 4 | **SEO & Search Intent Strategist** | Keyword Architect | Builds keyword clusters categorized by intent (Informational, Tutorial, Comparison, Troubleshooting) |
| 5 | **Metadata & CTR Specialist** | Packaging Expert | Crafts 3 title variations per concept, optimized descriptions, tags, and thumbnail blueprints |
| 6 | **Senior Strategy Report Editor** | Blueprint Compiler | Synthesizes all findings into a master YouTube SEO & Growth Blueprint with a 7-day launch calendar |

---

## 📡 API Reference

All endpoints are served by a **Starlette ASGI** application. Authentication uses JWT tokens via HttpOnly cookies.

### System

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/health` | ❌ | Server status, model info, API connectivity |
| `POST` | `/api/model` | ✅ | Switch the active LLM model at runtime |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | Register a new account |
| `POST` | `/api/auth/verify-email` | Verify email with 6-digit code |
| `POST` | `/api/auth/resend-verification` | Resend verification code |
| `POST` | `/api/auth/login` | Sign in with email & password |
| `POST` | `/api/auth/forgot-password` | Request password reset token |
| `POST` | `/api/auth/reset-password` | Reset password with token |
| `GET` | `/api/auth/me` | Get current user profile |
| `POST` | `/api/auth/logout` | Clear session cookie |

### YouTube SEO & Analysis

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/analyze` | ✅ | Run the full 6-agent CrewAI pipeline for a topic |
| `POST` | `/api/quick-predict` | ✅ | Quick competitor stats without running the full crew |
| `GET` | `/api/competitors?q=topic` | ✅ | Live YouTube competitor video data |
| `GET` | `/api/report` | ✅ | Retrieve latest saved analysis report |
| `GET` | `/api/history` | ✅ | List past analysis runs |
| `GET` | `/api/history/{item_id}` | ✅ | Get full detail of a specific analysis |

---

## 📂 Project Structure

```
SEOVerse/
├── api_server.py                   # Starlette ASGI server & all API routes
├── auth.py                         # JWT authentication, SQLite user/history DB
├── email_service.py                # SMTP email + local dev simulation
├── youtube_data.py                 # YouTube Data API v3 client
├── report_parser.py                # Extract structured JSON from agent reports
│
├── src/youtube_seo_agent/
│   ├── config/
│   │   ├── agents.yaml             # 6 agent role/goal/backstory definitions
│   │   └── tasks.yaml              # 6 task descriptions & dependencies
│   ├── crew.py                     # CrewAI @CrewBase crew orchestration
│   ├── main.py                     # CLI entry point (crewai run)
│   └── tools/
│       └── custom_tool.py          # Custom tool implementations
│
├── frontend/
│   ├── index.html                  # Single-page app (landing + dashboard)
│   ├── app.js                      # Frontend logic, API calls, UI state
│   └── style.css                   # Custom styles (Tailwind + overrides)
│
├── database/                       # SQLite databases (auto-created, gitignored)
├── reports/                        # Generated markdown reports
├── knowledge/                      # CrewAI knowledge base resources
├── tests/
│   └── test_crew_config.py         # Configuration validation tests
│
├── .env.example                    # Template for environment variables
├── Dockerfile                      # Production container configuration
├── pyproject.toml                  # Python project config & dependencies
└── uv.lock                        # Locked dependency versions
```

---

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t seoverse .

# Run with environment variables
docker run -d \
  --name seoverse \
  -p 8000:8000 \
  -e JWT_SECRET="your-strong-random-secret" \
  -e YOUTUBE_API_KEY="your-key" \
  -e GEMINI_API_KEY="your-key" \
  -e ENVIRONMENT=production \
  -e COOKIE_SECURE=true \
  -v seoverse_data:/app/database \
  -v seoverse_reports:/app/reports \
  seoverse
```

> **Important:** The container does **not** include Ollama. For local model inference, either deploy a reachable Ollama service or configure a hosted model provider (Gemini, OpenAI, etc.).

---

## 🔧 Supported AI Models

SEOVerse supports **20+ LLM providers** via LiteLLM routing. Set the `MODEL` environment variable or switch models at runtime from the dashboard.

| Provider | Example Model String | Notes |
|----------|---------------------|-------|
| Google Gemini | `gemini/gemini-2.0-flash` | Default; requires `GEMINI_API_KEY` |
| Ollama (Local) | `ollama/llama3.2:1b` | Free, private; requires local Ollama server |
| OpenAI | `openai/gpt-4o` | Requires `OPENAI_API_KEY` |
| Anthropic | `anthropic/claude-sonnet-4-20250514` | Requires `ANTHROPIC_API_KEY` |
| Groq | `groq/llama-3.3-70b-versatile` | Requires `GROQ_API_KEY` |
| AWS Bedrock | `bedrock/anthropic.claude-3-sonnet` | Requires AWS credentials |

---

## 🛡️ Security Notes

- **Passwords** are hashed with **bcrypt** (12 rounds)
- **Sessions** use signed **JWT tokens** stored in HttpOnly cookies
- **CSRF protection** via SameSite=Lax cookie policy
- Set `COOKIE_SECURE=true` when serving behind HTTPS
- Set a strong `JWT_SECRET` (≥ 32 characters) in production
- Configure `CORS_ORIGINS` only if the frontend is hosted on a separate origin
- Email verification codes expire after 24 hours; password reset tokens expire after 1 hour

---

## 🧪 Running Tests

```bash
uv run pytest tests/ -v
```

To test the CrewAI crew directly via CLI:

```bash
crewai run "your topic here"
```

---

## ⚠️ Data Disclaimer

YouTube counters displayed in SEOVerse are **observed public search results** from a small, changing sample. The YouTube public API does **not** provide:

- Keyword search volume
- Audience retention rates
- Click-through rates (CTR)
- Future view projections

All agent recommendations are **strategy suggestions based on available data**, not measured outcomes or guaranteed predictions.

---

## 🗺️ Roadmap

- [ ] Multi-channel comparative analysis
- [ ] Scheduled recurring analyses with email reports
- [ ] Export to Google Docs / Notion
- [ ] Thumbnail AI generation with DALL-E / Imagen
- [ ] YouTube Analytics API integration (authenticated channel data)
- [ ] Team collaboration & shared workspaces

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👩‍💻 Author

**Vaishnavi G**

- GitHub: [@vaishnaviG031](https://github.com/vaishnaviG031)

---

<p align="center">
  <em>Built with ❤️ using CrewAI, Google Gemini, and YouTube Data API v3</em>
</p>
