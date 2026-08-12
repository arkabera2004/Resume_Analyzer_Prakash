"""FastAPI application entrypoint."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import client, close_mongo_connection, connect_to_mongo
from app.routes import auth, job, match, resume

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="AI Resume Analyzer API",
    description="Backend for the AI Resume Analyzer & Job Match Platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(job.router)
app.include_router(match.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    """Never leak internal stack traces / API keys / DB errors to the client."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


@app.get("/")
def read_root():
    return {"status": "ok", "service": "resume-analyzer-api"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/health/db")
async def db_health_check():
    try:
        await client.admin.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}
