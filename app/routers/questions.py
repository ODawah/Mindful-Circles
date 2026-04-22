# app/routers/questions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.question import QuestionOut, QuestionUpdate
from app.services import questions as question_service

router = APIRouter(prefix="/circles", tags=["questions"])

@router.get("/{circle_id}/questions", response_model=list[QuestionOut])
def get_questions(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return question_service.get_questions(db, circle_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{circle_id}/questions/today")
def update_today_question(
    circle_id: int,
    data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = question_service.update_today_question(db, circle_id, current_user.id, data)
        question = result["question"]
        return {
            **QuestionOut.model_validate(question).model_dump(),
            "asked_member_display_name": result["asked_member_display_name"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{circle_id}/questions/today")
def get_today_question(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = question_service.get_today_question(db, circle_id, current_user.id)
        question = result["question"]
        return {
            **QuestionOut.model_validate(question).model_dump(),
            "asked_member_display_name": result["asked_member_display_name"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
