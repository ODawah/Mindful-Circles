# app/services/answers.py
from sqlalchemy.orm import Session
from app.models.answer import Answer
from app.models.question import Question
from app.models.membership import Membership
from app.models.circle import Circle
from app.schemas.answer import AnswerCreate

def submit_answer(db: Session, question_id: int, user_id: int, data: AnswerCreate) -> Answer:
    question = db.query(Question).first() if False else \
        db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise ValueError("Question not found")

    membership = db.query(Membership).filter(
        Membership.circle_id == question.circle_id,
        Membership.user_id == user_id
    ).first()
    if not membership:
        raise ValueError("You are not a member of this circle")

    already_answered = db.query(Answer).filter(
        Answer.question_id == question_id,
        Answer.membership_id == membership.id
    ).first()
    if already_answered:
        raise ValueError("You have already answered this question")

    answer = Answer(
        question_id=question_id,
        membership_id=membership.id,
        text=data.text
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer

def get_answers(db: Session, question_id: int, user_id: int) -> tuple[list[dict], bool]:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise ValueError("Question not found")

    membership = db.query(Membership).filter(
        Membership.circle_id == question.circle_id,
        Membership.user_id == user_id
    ).first()
    if not membership:
        raise ValueError("You are not a member of this circle")

    # Hide answers until user has answered
    already_answered = db.query(Answer).filter(
        Answer.question_id == question_id,
        Answer.membership_id == membership.id
    ).first()
    if not already_answered:
        raise ValueError("Answer the question first to see others' responses")

    circle = db.query(Circle).filter(Circle.id == question.circle_id).first()
    answers = db.query(Answer).filter(Answer.question_id == question_id).all()

    result = []
    for answer in answers:
        member = db.query(Membership).filter(
            Membership.id == answer.membership_id
        ).first()
        result.append({
            "id": answer.id,
            "question_id": answer.question_id,
            "text": answer.text,
            "created_at": answer.created_at,
            "display_name": None if circle.is_anonymous else member.display_name
        })

    return result, circle.is_anonymous