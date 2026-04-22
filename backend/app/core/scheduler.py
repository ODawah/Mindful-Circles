# app/core/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
from app.database import SessionLocal
from app.models.circle import Circle
from app.services.questions import create_question_for_circle

def create_daily_questions():
    db = SessionLocal()
    try:
        circles = db.query(Circle).all()
        for circle in circles:
            create_question_for_circle(db, circle.id, date.today())
    finally:
        db.close()

def start_scheduler():
    create_daily_questions()
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        create_daily_questions,
        trigger="cron",
        hour=0,
        minute=0,
        id="daily_questions"
    )
    scheduler.start()
    return scheduler
