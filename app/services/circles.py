# app/services/circles.py
from datetime import date
from sqlalchemy.orm import Session
from app.models.circle import Circle
from app.models.membership import Membership
from app.schemas.circle import CircleCreate, CircleUpdate

def create_circle(db: Session, data: CircleCreate, owner_id: int, owner_display_name: str = "Owner") -> Circle:
    circle = Circle(
        name=data.name,
        description=data.description,
        is_anonymous=data.is_anonymous,
        owner_id=owner_id
    )
    db.add(circle)
    db.flush()  # gets us the circle.id without committing yet

    membership = Membership(
        user_id=owner_id,
        circle_id=circle.id,
        display_name=owner_display_name or "Owner",
        order=0
    )
    db.add(membership)
    from app.services.questions import create_question_for_circle
    create_question_for_circle(db, circle.id, date.today())
    db.commit()
    db.refresh(circle)
    return circle

def get_my_circles(db: Session, user_id: int) -> list[Circle]:
    return (
        db.query(Circle)
        .join(Membership, Membership.circle_id == Circle.id)
        .filter(Membership.user_id == user_id)
        .all()
    )

def get_circle(db: Session, circle_id: int, user_id: int) -> Circle:
    circle = db.query(Circle).filter(Circle.id == circle_id).first()
    if not circle:
        raise ValueError("Circle not found")

    is_member = db.query(Membership).filter(
        Membership.circle_id == circle_id,
        Membership.user_id == user_id
    ).first()
    if not is_member:
        raise ValueError("You are not a member of this circle")

    return circle

def update_circle(db: Session, circle_id: int, data: CircleUpdate, user_id: int) -> Circle:
    circle = db.query(Circle).filter(Circle.id == circle_id).first()
    if not circle:
        raise ValueError("Circle not found")
    if circle.owner_id != user_id:
        raise ValueError("Only the owner can update this circle")

    if data.name is not None:
        circle.name = data.name
    if data.description is not None:
        circle.description = data.description
    if data.is_anonymous is not None:
        circle.is_anonymous = data.is_anonymous

    db.commit()
    db.refresh(circle)
    return circle

def delete_circle(db: Session, circle_id: int, user_id: int) -> None:
    circle = db.query(Circle).filter(Circle.id == circle_id).first()
    if not circle:
        raise ValueError("Circle not found")
    if circle.owner_id != user_id:
        raise ValueError("Only the owner can delete this circle")

    db.delete(circle)
    db.commit()
