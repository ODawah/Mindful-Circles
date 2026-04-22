# app/routers/memberships.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.membership import JoinCircle, MemberOut, MemberOutAnonymous
from app.services import memberships as membership_service

router = APIRouter(prefix="/circles", tags=["memberships"])

@router.post("/{circle_id}/join", response_model=MemberOut)
def join_circle(
    circle_id: int,
    data: JoinCircle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return membership_service.join_circle(db, circle_id, current_user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{circle_id}/leave", status_code=204)
def leave_circle(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        membership_service.leave_circle(db, circle_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{circle_id}/members")
def get_members(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        members, is_anonymous = membership_service.get_members(db, circle_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    schema = MemberOutAnonymous if is_anonymous else MemberOut
    return [schema.model_validate(m) for m in members]

@router.delete("/{circle_id}/members/{membership_id}", status_code=204)
def remove_member(
    circle_id: int,
    membership_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        membership_service.remove_member(db, circle_id, membership_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))