# EVA AI Assistant

A production-ready AI chatbot with a warm, emotionally intelligent personality. Built with Flask (backend) and vanilla HTML/CSS/JavaScript (frontend).

## Architecture

```
eva/
├── backend/                # Flask API server
│   ├── app/                # Application package
│   │   ├── __init__.py     # App factory with CORS & middleware
│   │   ├── config.py       # Centralized environment config
│   │   ├── middleware.py   # JWT auth, rate limiting, security headers
│   │   ├── routes/         # API route blueprints
│   │   │   ├── health.py   # GET /health - service status
│   │   │   ├── chat.py     # POST /chat - main chat endpoint
│   │   │   ├── auth.py     # GET /auth/me - verify JWT session
│   │   │   └── conversations.py  # CRUD conversations
│   │   ├── services/       # Business logic layer
│   │   │   ├── ai.py       # Groq AI client with key rotation & retry
│   │   │   ├── database.py # Supabase client (users, conversations, messages)
│   │   │   ├── memory.py   # Mood detection, time context, memory merging
│   │   │   └── search.py   # DuckDuckGo web search
│   │   └── utils/          # Helpers & validation
│   │       ├── helpers.py  # Sanitization, JSON parsing, response builders
│   │       └── validators.py # Request validation decorators
│   ├── run.py              # Development entry point
│   ├── app.py              # Production entry point (Render)
│   ├── requirements.txt    # Pinned dependencies
│   └── .env.example        # Environment variable template
├── frontend/               # Static files (Vercel)
│   ├── index.html          # Main chat interface
│   ├── login.html          # Login page
│   ├── signup.html         # Sign-up page
│   ├── style.css           # Full responsive stylesheet
│   └── js/                 # Modular JavaScript
│       ├── api.js          # API client with JWT auth
│       ├── auth.js         # Supabase authentication
│       ├── ui.js           # Markdown, syntax highlighting, toasts, modals
│       ├── chat.js         # Chat message rendering & management
│       └── app.js          # Main app orchestrator
└── .github/workflows/      # CI/CD
    └── lint.yml            # Python & JS linting
```

## Features

- **Conversational AI** with Groq (Llama 3.1, Mixtral, Gemma 2, Llama 3.3)
- **Multi-model selector** - switch AI models on the fly
- **Persistent chat history** stored in Supabase
- **Conversation management** - sidebar, search, rename, delete, export
- **User memory** - the AI remembers user preferences, emotions, and relationships
- **Web search** - automatic DuckDuckGo integration for real-time information
- **Token usage display** - see how many tokens each response uses
- **Markdown rendering** with syntax-highlighted code blocks and copy buttons
- **Typing indicators** and loading animations
- **Toast notifications** for user feedback
- **Fully responsive** - desktop, tablet, and mobile
- **Dark theme** with modern glassmorphism design
- **Secure** - JWT verification, rate limiting, CSP headers, input sanitization
- **Groq API key rotation** with automatic failover and temporary key disabling

## Prerequisites

- Python 3.10+
- Supabase project (free tier works)
- Groq API key(s)

## Setup

### 1. Clone & Install

```bash
git clone <repo-url>
cd eva

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `GROQ_KEYS` - comma-separated Groq API keys
- `SUPABASE_URL` - your Supabase project URL
- `SUPABASE_KEY` - your Supabase service role key (not the anon key)
- `SUPABASE_JWT_SECRET` - JWT secret from Supabase Auth settings

### 3. Database Setup

Run the SQL in `backend/app/supabase_schema.sql` in your Supabase SQL Editor to create the required tables.

### 4. Run Backend

```bash
python run.py
```

The API will be available at `http://localhost:10000`.

### 5. Serve Frontend

Use any static file server:

```bash
# Python
cd frontend
python -m http.server 3000

# Or npx serve
npx serve frontend
```

Open `http://localhost:3000` and sign in.

## Deployment

### Backend (Render)

1. Push the repository to GitHub
2. Create a new Web Service on Render
3. Set:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn app:app`
   - **Root Directory**: Leave blank (Render will use the repo root)
4. Add all environment variables from `.env.example`

### Frontend (Vercel)

1. Install Vercel CLI: `npm i -g vercel`
2. Deploy: `cd frontend && vercel --prod`
3. Or connect the GitHub repo to Vercel with:
   - **Root Directory**: `frontend`
   - **Build Command**: None (static files)
   - **Output Directory**: `.` (root)

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | No | Service health & key stats |
| POST | `/chat` | JWT | Send a chat message |
| GET | `/conversations` | JWT | List conversations (?q=search) |
| POST | `/conversations` | JWT | Create conversation |
| GET | `/conversations/:id` | JWT | Get conversation with messages |
| PATCH | `/conversations/:id/rename` | JWT | Rename conversation |
| DELETE | `/conversations/:id` | JWT | Delete conversation |
| GET | `/conversations/:id/export` | JWT | Export as JSON |
| GET | `/auth/me` | JWT | Verify session |

## Security

- JWT tokens verified on every protected endpoint
- Rate limiting: 30 requests per 60 seconds per IP
- CORS restricted to known frontend domains
- Content Security Policy headers
- Input validation and sanitization
- All AI-generated HTML sanitized with DOMPurify
- Secrets never exposed to the client

## Tech Stack

- **Backend**: Python, Flask, Groq SDK, Supabase SDK, PyJWT
- **Frontend**: Vanilla HTML/CSS/JS, Marked.js, Highlight.js, DOMPurify
- **Auth**: Supabase Auth (email/password)
- **Database**: Supabase (PostgreSQL)
- **Search**: DuckDuckGo
- **Deployment**: Render (API), Vercel (Frontend)
