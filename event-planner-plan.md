# GenAI Celebration & Event Planner — Production Plan

## Top-Level Overview

Build a production-grade, GenAI-powered event planning assistant that helps users organize
weddings, birthdays, and community events. The assistant generates personalized budgets,
timelines, vendor checklists, and creative theme ideas via Google Gemini (gemini-1.5-flash).

**Architecture:**
- **Frontend:** Streamlit (multi-page app, deployed on Streamlit Cloud)
- **Backend:** FastAPI (REST API, deployed on Railway/Render)
- **Database:** PostgreSQL via Supabase (persistent user data and plans)
- **AI Layer:** Google Gemini API (gemini-1.5-flash) via `google-generativeai` SDK
- **Export:** PDF generation via `reportlab` or `weasyprint`

**Auth:** Username/password stored in PostgreSQL with bcrypt hashing. JWT tokens for
API session management between Streamlit and FastAPI.

**Confirmed Decisions:**
- Gemini API Key: provided (AIzaSyAb8RN6JlbyE1BtX0ILNIPTYCbGGzXTrX4rCaocPgczHEXc1xqQ — store in backend `.env` as `GEMINI_API_KEY`, never commit)
- Timeline scope: supports events 1 week to 1+ year away (timeline granularity adapts — daily tasks for <4 weeks, weekly for 1–3 months, monthly for >3 months)
- Plan versioning: regenerating a plan archives the previous one; full history accessible via `GET /events/{event_id}/plans`

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffolding & Repo Structure

**Status:** [x] done

**Intent:**
Set up the monorepo folder structure, dependency files, environment config, and CI-ready
layout. This establishes the foundation every other sub-task builds on.

**Expected Outcomes:**
- `/backend` FastAPI app with correct package layout
- `/frontend` Streamlit app with page layout
- `requirements.txt` / `pyproject.toml` for each service
- `.env.example` with all required secrets documented
- `docker-compose.yml` for local development (backend + postgres)
- `README.md` with setup instructions

**Todo List:**
1. Create root directory with `/backend`, `/frontend`, `/docs` folders
2. Create `backend/requirements.txt` with: fastapi, uvicorn, sqlalchemy, psycopg2-binary,
   alembic, python-jose[cryptography], passlib[bcrypt], google-generativeai, reportlab,
   python-multipart, pydantic-settings
3. Create `frontend/requirements.txt` with: streamlit, requests, python-dotenv, pillow
4. Create `backend/app/__init__.py` and module structure:
   `app/main.py`, `app/api/`, `app/core/`, `app/models/`, `app/schemas/`, `app/services/`
5. Create `frontend/pages/` for Streamlit multi-page layout
6. Create `.env.example` with: DATABASE_URL, GEMINI_API_KEY, SECRET_KEY, ALGORITHM,
   ACCESS_TOKEN_EXPIRE_MINUTES, FRONTEND_URL
7. Create `docker-compose.yml` with postgres + backend services
8. Create root `README.md` with local setup instructions

**Relevant Context:**
- FastAPI best-practice layout: `app/api/routes/` for endpoint files, `app/services/`
  for business logic, `app/models/` for SQLAlchemy ORM models, `app/schemas/` for Pydantic
- Streamlit multi-page: each file in `frontend/pages/` becomes a sidebar page

---

### Sub-Task 2 — Database Models & Migrations (Supabase/PostgreSQL)

**Status:** [x] done

**Intent:**
Define all SQLAlchemy ORM models and Alembic migrations so every service has a stable,
versioned schema from day one.

**Expected Outcomes:**
- `users` table with hashed passwords
- `events` table with event type, date, guest count, budget, owner FK
- `plans` table (stores full AI-generated plan JSON per event)
- `chat_history` table (per-event conversation turns for chat assistant)
- Alembic migration scripts runnable against Supabase

**Todo List:**
1. Create `backend/app/core/database.py` — SQLAlchemy engine + SessionLocal + Base
2. Create `backend/app/models/user.py` — User model (id, username, email, hashed_password,
   created_at)
3. Create `backend/app/models/event.py` — Event model (id, user_id FK, event_type ENUM,
   title, event_date, guest_count, total_budget, city, description, created_at, updated_at)
4. Create `backend/app/models/plan.py` — Plan model (id, event_id FK, budget_breakdown JSON,
   timeline JSON, vendor_checklist JSON, theme_ideas JSON, raw_ai_response TEXT, created_at)
5. Create `backend/app/models/chat.py` — ChatMessage model (id, event_id FK, role, content,
   created_at)
6. Initialize Alembic: `alembic init alembic`, configure `alembic/env.py` to use DATABASE_URL
7. Generate and run initial migration
8. Create `backend/app/core/config.py` — Pydantic Settings class loading from .env

**Relevant Context:**
- event_type ENUM values: "wedding", "birthday", "community"
- Plan JSON columns store structured AI output; use SQLAlchemy's JSON type
- Alembic env.py must import all models so autogenerate works

---

### Sub-Task 3 — Auth System (Register / Login / JWT)

**Status:** [x] done

**Intent:**
Implement secure user registration and login with bcrypt password hashing and JWT token
issuance. The Streamlit frontend stores the JWT in session state to authenticate all
subsequent API calls.

**Expected Outcomes:**
- `POST /auth/register` — creates user, returns JWT
- `POST /auth/login` — validates credentials, returns JWT
- `GET /auth/me` — returns current user from JWT (protected)
- Reusable `get_current_user` FastAPI dependency
- Streamlit login/register page that stores token in `st.session_state`

**Todo List:**
1. Create `backend/app/core/security.py` — bcrypt hash/verify helpers, JWT
   create/decode functions using python-jose
2. Create `backend/app/schemas/auth.py` — Pydantic schemas: UserCreate, UserLogin,
   Token, TokenData, UserOut
3. Create `backend/app/api/routes/auth.py` — register + login endpoints
4. Create `backend/app/api/deps.py` — `get_current_user` dependency (parses Bearer token)
5. Register auth router in `backend/app/main.py` with prefix `/auth`
6. Create `frontend/pages/1_Login.py` — Streamlit login/register form, stores JWT + user
   info in `st.session_state["token"]` and `st.session_state["user"]`
7. Create `frontend/utils/api.py` — helper `get_headers()` returning Authorization header
   from session state; `authenticated_request()` wrapper

**Relevant Context:**
- All protected FastAPI routes use `Depends(get_current_user)`
- Streamlit pages must redirect to login page if `st.session_state.get("token")` is None
- JWT expiry should be configurable via env var (default 24h for hackathon)

---

### Sub-Task 4 — Event Management CRUD API

**Status:** [x] done

**Intent:**
Build the REST endpoints so users can create, list, update, and delete their events.
Events are the core entity that all plans, timelines, and checklists attach to.

**Expected Outcomes:**
- `POST /events/` — create event (returns event with id)
- `GET /events/` — list all events for current user
- `GET /events/{event_id}` — get single event (validates ownership)
- `PUT /events/{event_id}` — update event metadata
- `DELETE /events/{event_id}` — delete event and cascade plans/chats
- All endpoints protected by JWT

**Todo List:**
1. Create `backend/app/schemas/event.py` — EventCreate, EventUpdate, EventOut Pydantic
   schemas with field validators (budget > 0, guest_count > 0, event_date in future)
2. Create `backend/app/services/event_service.py` — CRUD functions operating on DB session
3. Create `backend/app/api/routes/events.py` — all 5 endpoints using event_service
4. Register events router in `main.py` with prefix `/events`
5. Add cascade delete to SQLAlchemy relationships (plans, chat messages)
6. Create `frontend/pages/2_My_Events.py` — list user events with cards showing title,
   type badge, date, budget; "New Event" button opens creation form

**Relevant Context:**
- Ownership check: `event.user_id == current_user.id`, else raise HTTP 403
- EventOut must include computed field `plan_count` (number of plans generated)

---

### Sub-Task 5 — Gemini AI Service Layer

**Status:** [x] done

**Intent:**
Build the central AI service that constructs prompts, calls Gemini, and parses structured
JSON responses. This service is the core intelligence of the app and must be robust,
with clear prompt templates and reliable output parsing.

**Expected Outcomes:**
- `GeminiService` class wrapping `google.generativeai`
- Prompt templates for: budget breakdown, timeline, vendor checklist, theme ideas
- Combined "full plan" prompt that returns all four sections in one structured JSON call
- Chat/conversation prompt that maintains message history context
- Graceful error handling if Gemini returns non-parseable output

**Todo List:**
1. Create `backend/app/services/gemini_service.py` — initialize `genai.GenerativeModel`
   with model name from config
2. Write `PLAN_SYSTEM_PROMPT` — instructs Gemini to act as an expert event planner and
   return ONLY valid JSON with keys: `budget_breakdown`, `timeline`, `vendor_checklist`,
   `theme_ideas`
3. Implement `generate_full_plan(event_details: dict) -> dict` — builds detailed prompt
   from event metadata, calls Gemini, parses JSON, returns structured plan dict
4. Implement `generate_budget_breakdown(event_details: dict) -> dict` — focused budget call
5. Implement `chat_with_assistant(event_id, history: list, user_message: str) -> str` —
   constructs context-aware chat using prior conversation turns
6. Implement `_safe_parse_json(raw: str) -> dict` — strips markdown code fences, attempts
   `json.loads`, falls back to partial extraction with regex if needed
7. Write prompt templates for each event type (wedding/birthday/community) with
   type-specific vendor categories and budget norms
8. Create `backend/app/core/prompts.py` — store all prompt template strings

**Relevant Context:**
- Gemini API: `google.generativeai.configure(api_key=...)`, use `generate_content()`
- For structured output reliability: instruct model explicitly to respond with JSON only,
  no prose, wrap in ```json ... ``` is acceptable (handled by `_safe_parse_json`)
- Chat history format for Gemini: list of `{"role": "user"|"model", "parts": [text]}`
- Rate limit awareness: gemini-1.5-flash free tier = 15 RPM; add retry with exponential
  backoff using `tenacity`

**Budget Breakdown Structure (per event type):**
```
wedding: venue, catering, photography, decoration, music/DJ, invitations,
         attire, transport, honeymoon_preview, miscellaneous
birthday: venue, catering, decoration, entertainment, cake, invitations, miscellaneous
community: venue, catering, sound_system, decoration, permits, volunteers,
           marketing, miscellaneous
```

---

### Sub-Task 6 — Plan Generation & Storage API

**Status:** [x] done

**Intent:**
Build the endpoint that triggers Gemini to generate a full event plan, persists the
structured output to PostgreSQL, and returns it to the frontend.

**Expected Outcomes:**
- `POST /events/{event_id}/plan` — generates and stores a new plan
- `GET /events/{event_id}/plan` — retrieves latest plan for an event
- `GET /events/{event_id}/plans` — lists all plan versions (regeneration history)
- Plan stored as structured JSON columns in the `plans` table
- Frontend "Generate Plan" page that displays each section in rich Streamlit UI

**Todo List:**
1. Create `backend/app/schemas/plan.py` — PlanOut schema with nested TypedDict-style
   structures for budget_breakdown, timeline, vendor_checklist, theme_ideas
2. Create `backend/app/services/plan_service.py` — orchestrates gemini_service call +
   plan persistence + retrieval
3. Create `backend/app/api/routes/plans.py` — generate, get latest, list history endpoints
4. Register plans router in `main.py` with prefix `/events/{event_id}/plans`
5. Create `frontend/pages/3_Plan_Generator.py`:
   - Event selector dropdown
   - "Generate Plan ✨" button triggers POST to backend
   - Display budget as interactive pie chart (`st.plotly_chart`)
   - Display timeline as vertical timeline component
   - Display vendor checklist as interactive checkboxes (state stored in session)
   - Display theme ideas as colorful cards with Streamlit `st.columns`
6. Add loading spinner and progress messages during AI generation

**Relevant Context:**
- Plan generation can take 5-15s; use `st.spinner("Generating your plan with AI...")`
- Budget breakdown values should be numeric (floats) so they can be charted directly
- Timeline items: `[{"week": -12, "task": "Book venue", "category": "venue"}, ...]`
  where week is relative to event date (negative = weeks before)

---

### Sub-Task 7 — Chat Assistant Feature

**Status:** [x] done

**Intent:**
Add a conversational AI chat interface tied to a specific event. Users ask follow-up
questions ("Can you suggest cheaper catering options?", "What decorations for a beach
wedding?") and the assistant responds with event-context-aware answers.

**Expected Outcomes:**
- `POST /events/{event_id}/chat` — sends user message, gets AI response, persists both
- `GET /events/{event_id}/chat` — retrieves full conversation history
- `DELETE /events/{event_id}/chat` — clears chat history
- Streamlit chat UI using `st.chat_message` and `st.chat_input`

**Todo List:**
1. Create `backend/app/schemas/chat.py` — ChatMessageIn, ChatMessageOut Pydantic schemas
2. Create `backend/app/services/chat_service.py` — saves message pairs, retrieves history,
   builds Gemini-compatible history list from DB records
3. Create `backend/app/api/routes/chat.py` — send, list, clear endpoints
4. Register chat router in `main.py`
5. Create `frontend/pages/4_AI_Assistant.py`:
   - Event selector at top
   - Render full chat history using `st.chat_message("user")` / `st.chat_message("assistant")`
   - `st.chat_input("Ask your event assistant...")` triggers POST to backend
   - Auto-scroll to latest message
   - "Clear Chat" button

**Relevant Context:**
- Chat context includes: event type, date, budget, guest count, and latest plan summary
  (injected as system context into every Gemini call)
- Keep chat history to last 20 turns to stay within Gemini context limits
- Gemini roles: "user" and "model" (NOT "assistant")

---

### Sub-Task 8 — PDF Export Feature

**Status:** [x] done

**Intent:**
Allow users to export their complete event plan (budget, timeline, vendor checklist,
theme ideas) as a downloadable, well-formatted PDF.

**Expected Outcomes:**
- `GET /events/{event_id}/plan/export/pdf` — returns PDF as binary stream
- Professional PDF layout with event title, sections, tables, and charts
- Streamlit download button on the Plan Generator page

**Todo List:**
1. Add `reportlab` to backend requirements (already listed in Sub-Task 1)
2. Create `backend/app/services/pdf_service.py` — `generate_plan_pdf(plan, event) -> bytes`
   using reportlab's Platypus (flowable layout): title, budget table, timeline list,
   vendor checklist table, theme ideas section
3. Create `backend/app/api/routes/export.py` — PDF export endpoint returning
   `StreamingResponse` with `application/pdf` content-type
4. Register export router in `main.py`
5. Add download button to `frontend/pages/3_Plan_Generator.py`:
   `st.download_button("📄 Export as PDF", data=pdf_bytes, file_name="event_plan.pdf")`
6. Style PDF with event-type-specific accent colors (wedding=rose, birthday=purple,
   community=teal)

**Relevant Context:**
- reportlab Platypus: `SimpleDocTemplate`, `Table`, `Paragraph`, `Spacer`, `styles`
- PDF generation happens server-side; frontend just receives bytes via requests response

---

### Sub-Task 9 — Frontend Polish & Dashboard

**Status:** [x] done

**Intent:**
Build the main dashboard landing page, apply consistent branding/theming, add navigation
guards, and make the UI production-quality.

**Expected Outcomes:**
- `frontend/Home.py` — main entry page with hero section, feature cards, CTA
- Consistent custom CSS theme (gradient header, card styles, color palette)
- All pages redirect to login if not authenticated
- Sidebar shows logged-in user name, active event, logout button
- Mobile-responsive layout using Streamlit columns

**Todo List:**
1. Create `frontend/Home.py` — hero section with app name + tagline, feature highlight
   cards (Budget, Timeline, Vendors, AI Chat), event type quick-start buttons
2. Create `frontend/utils/auth_guard.py` — `require_auth()` function that checks
   `st.session_state["token"]` and calls `st.switch_page("pages/1_Login.py")` if missing
3. Create `frontend/utils/styles.py` — inject custom CSS via `st.markdown` for card
   styles, gradient headers, button overrides, color variables
4. Add sidebar to all pages: user avatar (initials), username, current event selector,
   logout button that clears session state
5. Add `st.set_page_config` to each page with app title, favicon (🎉), wide layout
6. Create `frontend/utils/constants.py` — event type icons, color maps, display labels

**Relevant Context:**
- Streamlit custom CSS via `st.markdown("<style>...</style>", unsafe_allow_html=True)`
- Navigation: `st.switch_page()` for programmatic redirects (Streamlit >= 1.28)
- `st.session_state` keys: `token`, `user`, `current_event_id`, `current_event_title`

---

### Sub-Task 10 — Production Configuration & Deployment

**Status:** [x] done

**Intent:**
Prepare both services for production deployment — environment separation, CORS config,
health checks, Streamlit Cloud config, and deployment documentation.

**Expected Outcomes:**
- FastAPI deployed to Railway/Render with DATABASE_URL and GEMINI_API_KEY set
- Streamlit app deployed to Streamlit Cloud with backend URL in secrets
- Supabase PostgreSQL connection working from deployed backend
- `BACKEND_URL` env var used throughout frontend (no hardcoded URLs)
- Health check endpoint at `GET /health`
- Full deployment guide in README.md

**Todo List:**
1. Add `GET /health` endpoint to `main.py` returning `{"status": "ok", "version": "1.0.0"}`
2. Configure CORS in FastAPI `main.py`:
   - Allow origins from env var `ALLOWED_ORIGINS` (comma-separated)
   - Allow credentials, all methods, all headers
3. Create `backend/Procfile`: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Create `frontend/.streamlit/config.toml` — theme config (primaryColor, backgroundColor,
   font)
5. Create `frontend/.streamlit/secrets.toml.example` — template for BACKEND_URL,
   SECRET_KEY
6. Update all `frontend/utils/api.py` calls to use
   `st.secrets["BACKEND_URL"]` or env fallback
7. Update `README.md` with:
   - Supabase setup (create project, get DATABASE_URL)
   - Railway/Render deploy steps
   - Streamlit Cloud deploy steps
   - Required environment variables table
8. Add `backend/alembic_run.py` helper script that runs migrations on startup

**Relevant Context:**
- Supabase connection string format:
  `postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres`
- Railway: set START command to Procfile web command; add DATABASE_URL + GEMINI_API_KEY
  in Variables tab
- Streamlit Cloud: add secrets in app settings → Secrets (TOML format)

---

## Architecture Diagram (Reference)

```
User Browser
    │
    ▼
Streamlit Cloud (frontend/)
    │  HTTP + JWT Bearer
    ▼
Railway/Render (FastAPI backend/)
    ├── /auth      ← register, login
    ├── /events    ← CRUD
    ├── /events/{id}/plans  ← AI plan gen
    ├── /events/{id}/chat   ← AI chat
    └── /events/{id}/plan/export/pdf
    │
    ├── Supabase PostgreSQL
    │     users, events, plans, chat_history
    │
    └── Google Gemini API
          gemini-1.5-flash
```

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| AI Model | gemini-1.5-flash | Free tier, fast, sufficient for structured JSON output |
| Auth | JWT + bcrypt | Simple, stateless, no extra service needed |
| Plan storage | JSON columns in PostgreSQL | Flexible schema, queryable, no separate doc store |
| PDF generation | reportlab server-side | No browser dependency, portable |
| Frontend | Streamlit multi-page | Fastest to build production UI, hackathon-friendly |
| Chat persistence | PostgreSQL chat_history table | Survives page reloads, enables history view |

---

## Environment Variables Reference

| Variable | Service | Description |
|---|---|---|
| `DATABASE_URL` | Backend | Supabase PostgreSQL connection string |
| `GEMINI_API_KEY` | Backend | Google AI Studio API key |
| `SECRET_KEY` | Backend | JWT signing secret (random 32+ chars) |
| `ALGORITHM` | Backend | JWT algorithm (HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Backend | JWT TTL (default: 1440 = 24h) |
| `ALLOWED_ORIGINS` | Backend | Comma-separated CORS allowed origins |
| `BACKEND_URL` | Frontend | Deployed FastAPI base URL |
