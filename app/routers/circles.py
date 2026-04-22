# app/routers/circles.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.circle import CircleCreate, CircleUpdate, CircleOut
from app.services import circles as circle_service

router = APIRouter(prefix="/circles", tags=["circles"])

@router.post("", response_model=CircleOut)
def create_circle(
    data: CircleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return circle_service.create_circle(db, data, current_user.id, current_user.full_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[CircleOut])
def get_my_circles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return circle_service.get_my_circles(db, current_user.id)

@router.get("/{circle_id}", response_model=CircleOut)
def get_circle(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return circle_service.get_circle(db, circle_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{circle_id}", response_model=CircleOut)
def update_circle(
    circle_id: int,
    data: CircleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return circle_service.update_circle(db, circle_id, data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{circle_id}", status_code=204)
def delete_circle(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        circle_service.delete_circle(db, circle_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
