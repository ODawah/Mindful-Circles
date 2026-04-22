from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import Token, UserLogin, UserRegister
from app.database import get_db
from app.services.auth import register_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
def register(data: UserRegister, db: Session = Depends(get_db)):
    try:
        result = register_user(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"access_token": result["access_token"], "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    try:
        result = login_user(db, data.email, data.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"access_token": result["access_token"], "token_type": "bearer"}
