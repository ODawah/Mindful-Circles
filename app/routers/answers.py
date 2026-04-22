# app/routers/answers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.answer import AnswerCreate, AnswerOut
from app.services import answers as answer_service

router = APIRouter(prefix="/questions", tags=["answers"])

@router.post("/{question_id}/answers", response_model=AnswerOut)
def submit_answer(
    question_id: int,
    data: AnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        answer = answer_service.submit_answer(db, question_id, current_user.id, data)
        return AnswerOut(
            id=answer.id,
            question_id=answer.question_id,
            text=answer.text,
            created_at=answer.created_at,
            display_name=None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{question_id}/answers")
def get_answers(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        results, _ = answer_service.get_answers(db, question_id, current_user.id)
        return results
    except ValueError as e:
        status_code = 403 if "Answer the question first" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))