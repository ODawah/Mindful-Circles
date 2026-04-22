# app/services/questions.py
from datetime import date
from sqlalchemy.orm import Session
from app.models.circle import Circle
from app.models.question import Question
from app.models.membership import Membership
from app.schemas.question import QuestionUpdate

def _get_todays_member(db: Session, circle_id: int, today: date) -> Membership | None:
    circle = db.query(Circle).filter(Circle.id == circle_id).first()
    if not circle:
        return None

    members = db.query(Membership).filter(
        Membership.circle_id == circle_id
    ).order_by(Membership.order).all()

    if not members:
        return None

    days_since_created = (today - circle.created_at.date()).days
    index = days_since_created % len(members)
    return members[index]

def create_question_for_circle(db: Session, circle_id: int, today: date) -> Question | None:
    # Don't create if one already exists for today
    existing = db.query(Question).filter(
        Question.circle_id == circle_id,
        Question.asked_date == today
    ).first()
    if existing:
        return existing

    member = _get_todays_member(db, circle_id, today)
    if not member:
        return None

    question = Question(
        circle_id=circle_id,
        text=f"Hey {member.display_name}, what's on your mind today?",
        asked_date=today
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

def get_today_question(db: Session, circle_id: int, user_id: int) -> dict | None:
    today = date.today()

    # Verify membership
    membership = db.query(Membership).filter(
        Membership.circle_id == circle_id,
        Membership.user_id == user_id
    ).first()
    if not membership:
        raise ValueError("You are not a member of this circle")

    question = db.query(Question).filter(
        Question.circle_id == circle_id,
        Question.asked_date == today
    ).first()
    if not question:
        question = create_question_for_circle(db, circle_id, today)
    if not question:
        raise ValueError("No question for today yet")

    # Get today's member name
    member = _get_todays_member(db, circle_id, today)

    return {
        "question": question,
        "asked_member_display_name": member.display_name if member else None
    }

def update_today_question(db: Session, circle_id: int, user_id: int, data: QuestionUpdate) -> dict:
    today = date.today()

    membership = db.query(Membership).filter(
        Membership.circle_id == circle_id,
        Membership.user_id == user_id
    ).first()
    if not membership:
        raise ValueError("You are not a member of this circle")

    todays_member = _get_todays_member(db, circle_id, today)
    if not todays_member:
        raise ValueError("No member is assigned to ask today")
    if todays_member.user_id != user_id:
        raise ValueError("It is not your turn to ask today's question")

    question = db.query(Question).filter(
        Question.circle_id == circle_id,
        Question.asked_date == today
    ).first()
    if not question:
        question = create_question_for_circle(db, circle_id, today)
    if not question:
        raise ValueError("No question for today yet")

    text = data.text.strip()
    if not text:
        raise ValueError("Question text is required")

    question.text = text
    db.commit()
    db.refresh(question)

    return {
        "question": question,
        "asked_member_display_name": todays_member.display_name
    }

def get_questions(db: Session, circle_id: int, user_id: int) -> list[Question]:
    membership = db.query(Membership).filter(
        Membership.circle_id == circle_id,
        Membership.user_id == user_id
    ).first()
    if not membership:
        raise ValueError("You are not a member of this circle")

    return db.query(Question).filter(
        Question.circle_id == circle_id
    ).order_by(Question.asked_date.desc()).all()
