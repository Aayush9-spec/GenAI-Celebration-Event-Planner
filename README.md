# 🎉 GenAI Celebration & Event Planner

A production-grade, AI-powered event planning assistant for weddings, birthdays, and community events.
Built with **Google Gemini 1.5 Flash**, FastAPI, PostgreSQL, and Streamlit.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)

---

## ✨ Features

| Feature | Description |
|---|---|
| 💰 **Budget Planner** | AI-generated cost breakdown per category (venue, catering, decor, etc.) |
| 📅 **Smart Timeline** | Adaptive milestone timeline (daily/weekly/monthly based on lead time) |
| ✅ **Vendor Checklist** | Category-wise vendor tasks with booking deadlines and expert tips |
| 🤖 **AI Chat Assistant** | Conversational AI with full event context and plan history |
| 📄 **PDF Export** | Download your complete plan as a professionally formatted PDF |
| 🔐 **Auth** | Secure registration/login with bcrypt + JWT; plans persist across sessions |
| 📋 **Plan History** | Every regenerated plan is archived; view all versions |

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit (multi-page, Streamlit Cloud) |
| Backend | FastAPI + Uvicorn (Railway/Render) |
| Database | PostgreSQL via Supabase |
| AI | Google Gemini 1.5 Flash (`google-genai` SDK) |
| Auth | bcrypt + python-jose JWT |
| PDF | reportlab Platypus |
| Migrations | Alembic |

---

## 🚀 Local Development

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional but recommended)
- A Google AI Studio API key: https://aistudio.google.com

### Option A — Docker Compose (Recommended)

```bash
git clone <repo-url>
cd event-planner

# Configure environment
cp .env.example backend/.env
# Edit backend/.env — set GEMINI_API_KEY at minimum

# Start everything
docker-compose up --build
```

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: run separately (see below)

### Option B — Manual Setup

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp ../.env.example .env
# Edit .env with your values

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
pip install -r requirements.txt

# Create secrets file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml: set BACKEND_URL = "http://localhost:8000"

streamlit run Home.py
```

---

## 🌐 Production Deployment

### 1. Supabase (PostgreSQL)

1. Go to https://supabase.com and create a new project
2. In **Settings → Database**, copy the **Connection String** (URI format)
3. Format: `postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres`
4. Use this as `DATABASE_URL` in your backend environment

### 2. Railway (FastAPI Backend)

1. Go to https://railway.app → New Project → Deploy from GitHub repo
2. Select the root of this repo; set **Root Directory** to `backend`
3. Add environment variables in Railway dashboard:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Your Supabase connection string |
| `GEMINI_API_KEY` | Your Google AI Studio key |
| `SECRET_KEY` | Random 32+ character string |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` |
| `ALLOWED_ORIGINS` | Your Streamlit Cloud app URL (e.g. `https://yourapp.streamlit.app`) |

4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Note your Railway deployment URL (e.g. `https://yourapp.up.railway.app`)

### 3. Streamlit Cloud (Frontend)

1. Go to https://share.streamlit.io → New app → Connect GitHub repo
2. Set **Main file path** to `frontend/Home.py`
3. In **Advanced settings → Secrets**, add:

```toml
BACKEND_URL = "https://yourapp.up.railway.app"
```

4. Deploy — your app will be live at `https://yourapp.streamlit.app`

---

## 🔐 Environment Variables Reference

| Variable | Service | Required | Description |
|---|---|---|---|
| `DATABASE_URL` | Backend | ✅ | PostgreSQL connection string (Supabase) |
| `GEMINI_API_KEY` | Backend | ✅ | Google AI Studio API key |
| `SECRET_KEY` | Backend | ✅ | JWT signing secret (32+ random chars) |
| `ALGORITHM` | Backend | — | JWT algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Backend | — | Token TTL (default: `1440` = 24h) |
| `ALLOWED_ORIGINS` | Backend | — | CORS origins, comma-separated (default: `*`) |
| `BACKEND_URL` | Frontend | ✅ | Deployed FastAPI base URL |

---

## 📁 Project Structure

```
event-planner/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, router registration, startup
│   │   ├── api/
│   │   │   ├── deps.py          # JWT auth dependency
│   │   │   └── routes/          # auth, events, plans, chat, export
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic Settings
│   │   │   ├── database.py      # SQLAlchemy engine + session
│   │   │   ├── security.py      # bcrypt + JWT helpers
│   │   │   └── prompts.py       # Gemini prompt templates
│   │   ├── models/              # SQLAlchemy ORM (User, Event, Plan, ChatMessage)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   └── services/
│   │       ├── gemini_service.py  # Google Gemini API integration
│   │       ├── event_service.py   # Event CRUD
│   │       ├── plan_service.py    # Plan generation + storage
│   │       ├── chat_service.py    # Chat history + AI chat
│   │       └── pdf_service.py     # PDF generation (reportlab)
│   ├── alembic/                 # Database migrations
│   ├── requirements.txt
│   └── Procfile
├── frontend/
│   ├── Home.py                  # Dashboard
│   ├── pages/
│   │   ├── 1_Login.py           # Auth (login + register)
│   │   ├── 2_My_Events.py       # Event management
│   │   ├── 3_Plan_Generator.py  # AI plan + charts + export
│   │   └── 4_AI_Assistant.py    # Chat interface
│   ├── utils/
│   │   ├── api.py               # API client helpers
│   │   ├── auth_guard.py        # Auth redirect guard
│   │   ├── styles.py            # Global CSS + sidebar
│   │   └── constants.py         # Event type icons/colors
│   ├── .streamlit/
│   │   └── config.toml          # Theme config
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🛠️ API Reference

Once running, visit http://localhost:8000/docs for the full interactive API documentation.

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/auth/register` | POST | Create account, returns JWT |
| `/auth/login` | POST | Login, returns JWT |
| `/auth/profile` | GET | Get current user (protected) |
| `/events/` | GET/POST | List / create events |
| `/events/{id}` | GET/PUT/DELETE | Get / update / delete event |
| `/events/{id}/plans/` | GET/POST | List history / generate new plan |
| `/events/{id}/plans/latest` | GET | Get most recent plan |
| `/events/{id}/plans/export/pdf` | GET | Download plan as PDF |
| `/events/{id}/chat/` | GET/POST/DELETE | List / send / clear chat |

---

*Built for [Hack2Skill — Celebration & Event Planner Challenge](https://hack2skill.com/event/pwvirtual1/dashboard/challenges) · Powered by Google Gemini*
