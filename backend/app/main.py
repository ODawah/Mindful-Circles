# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, circles, memberships, questions, answers
from app.core.config import settings
from app.core.scheduler import start_scheduler

app = FastAPI(title="Mindful Circles")

origins = [origin.strip() for origin in settings.FRONTEND_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def include_api_routes(prefix: str = "") -> None:
    app.include_router(auth.router, prefix=prefix)
    app.include_router(circles.router, prefix=prefix)
    app.include_router(memberships.router, prefix=prefix)
    app.include_router(questions.router, prefix=prefix)
    app.include_router(answers.router, prefix=prefix)


include_api_routes()
include_api_routes("/api")

@app.on_event("startup")
def startup():
    if settings.ENABLE_SCHEDULER and not os.getenv("VERCEL"):
        start_scheduler()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/health")
def prefixed_health():
    return health()
