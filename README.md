# AI Resume Analyzer & Job Match Platform

A full-stack platform that parses resumes, scores them against ATS-style criteria, and
matches them against job descriptions — built with React + FastAPI + MongoDB, with a
configurable LLM provider (Gemini/OpenAI) for recommendations.

> 🚧 **Status:** Under active development. This README will grow with each phase.
> Currently complete: **Phase 1 (project setup)**, **Phase 2 (backend + MongoDB)**,
> **Phase 3 (authentication)**, **Phase 4 (frontend + routing)**.

## Tech Stack

**Frontend:** React 19, TanStack Start (file-based routing + SSR), TypeScript, Tailwind CSS v4,
shadcn/ui, TanStack Query, Lucide React. Generated with [Lovable](https://lovable.dev) and wired
to this repo's own FastAPI backend (no Supabase/Lovable Cloud — plain `fetch` over HTTP, JWT in
localStorage).
**Backend:** Python, FastAPI, Pydantic, Uvicorn, JWT auth, Passlib/bcrypt
**Database:** MongoDB (MongoDB Atlas), Motor (async PyMongo)
**AI:** Configurable provider (Gemini or OpenAI) via environment variables
**Resume parsing:** PyMuPDF, python-docx

## Project Structure

```
Resume_Analyzer_Prakash/
├── backend/
│   ├── app/
│   │   ├── main.py            # (entrypoint lives at backend/main.py)
│   │   ├── config.py          # env-driven settings
│   │   ├── database.py        # MongoDB connection
│   │   ├── routes/            # API route handlers
│   │   ├── services/          # business logic (parsing, scoring, matching, AI)
│   │   ├── models/            # MongoDB document models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   └── utils/             # security, validators
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── routes/            # file-based routes (TanStack Start) — index, login,
│   │   │                        register, _authenticated.{dashboard,profile}
│   │   ├── components/        # navbar, footer, protected-route, ui/ (shadcn)
│   │   ├── lib/                # api.ts (fetch wrapper), auth.tsx (auth context), utils
│   │   └── hooks/
│   └── .env.example
└── README.md
```

## Running Locally

### Backend

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in MongoDB URI, JWT secret, AI API key
uvicorn main:app --reload --port 8000
```

Health checks:
- `GET http://localhost:8000/api/health` — API is up
- `GET http://localhost:8000/api/health/db` — MongoDB connection is reachable

**Local MongoDB (no Atlas account needed for development):**

```bash
docker run -d --name resume-analyzer-mongo -p 27017:27017 mongo:7
# then set in backend/.env:
# MONGODB_URI=mongodb://localhost:27017
```

For production, point `MONGODB_URI` at a MongoDB Atlas cluster instead.

`FRONTEND_URL` in `backend/.env` is a **comma-separated list** of allowed CORS origins — the
frontend dev server's port isn't fixed (TanStack Start takes the first free port starting at
8080), so the default covers `5173`, `8080`, and `8081`. Add your actual dev port if it picks a
different one, and your deployed frontend URL in production.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_URL if backend isn't on localhost:8000
npm run dev
```

Runs on the first free port starting at `8080` (printed in the terminal on startup).

## Environment Variables

See `backend/.env.example` and `frontend/.env.example`. Never commit `.env` files —
they're already excluded via `.gitignore`.

## API Overview (so far)

| Method | Path | Auth required | Description |
|---|---|---|---|
| POST | `/api/auth/register` | No | Create an account, returns a JWT |
| POST | `/api/auth/login` | No | Exchange email/password for a JWT |
| GET | `/api/auth/me` | Yes | Current user's profile |
| POST | `/api/auth/logout` | Yes | Client-side token discard (JWT is stateless) |

Send `Authorization: Bearer <token>` on authenticated requests.

## Backend Tests

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
# needs a reachable MongoDB (see "Local MongoDB" above) — tests use a
# separate `resume_analyzer_test` database, never your dev data
pytest -v
```

## Note on the frontend's deployment target

The frontend build (`npm run build`) uses Nitro with a **Cloudflare Workers** preset by default
(inherited from the Lovable/TanStack Start template), not the Vercel/Render split described in
the original project plan. It still runs as a normal Vite dev server locally and builds fine;
the deployment target just needs to be decided in Phase 17 — either adjust the Nitro preset for
Vercel/Node hosting, or deploy the frontend to Cloudflare Pages/Workers instead. Not blocking for
now since the backend (FastAPI on Render/Railway) is unaffected either way.

## Roadmap

This project is built in phases (auth → upload/parsing → ATS scoring → JD matching →
AI recommendations → dashboard/history → PDF reports → deployment). See commit history
for progress; each phase lands as its own commit(s).

## License

Personal portfolio project.
