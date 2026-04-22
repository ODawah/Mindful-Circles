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

app.include_router(auth.router)
app.include_router(circles.router)
app.include_router(memberships.router)
app.include_router(questions.router)
app.include_router(answers.router)

@app.on_event("startup")
def startup():
    if settings.ENABLE_SCHEDULER and not os.getenv("VERCEL"):
        start_scheduler()

@app.get("/health")
def health():
    return {"status": "ok"}
