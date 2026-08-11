# AI Resume Analyzer & Job Match Platform

A full-stack platform that parses resumes, scores them against ATS-style criteria, and
matches them against job descriptions — built with React + FastAPI + MongoDB, with a
configurable LLM provider (Gemini/OpenAI) for recommendations.

> 🚧 **Status:** Under active development. This README will grow with each phase.
> Currently complete: **Phase 1 — Project setup & folder structure.**

## Tech Stack

**Frontend:** React, Vite, Tailwind CSS, React Router, Axios, Recharts, Lucide React
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
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── context/
│   │   └── utils/
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

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_URL if backend isn't on localhost:8000
npm run dev
```

App runs at `http://localhost:5173`.

## Environment Variables

See `backend/.env.example` and `frontend/.env.example`. Never commit `.env` files —
they're already excluded via `.gitignore`.

## Roadmap

This project is built in phases (auth → upload/parsing → ATS scoring → JD matching →
AI recommendations → dashboard/history → PDF reports → deployment). See commit history
for progress; each phase lands as its own commit(s).

## License

Personal portfolio project.
