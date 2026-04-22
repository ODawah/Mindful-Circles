# app/services/memberships.py
from sqlalchemy.orm import Session
from app.models.membership import Membership
from app.models.circle import Circle
from app.schemas.membership import JoinCircle

def _get_circle_or_raise(db: Session, circle_id: int) -> Circle:
    circle = db.query(Circle).filter(Circle.id == circle_id).first()
    if not circle:
        raise ValueError("Circle not found")
    return circle

def _get_membership_or_raise(db: Session, circle_id: int, user_id: int) -> Membership:
    membership = db.query(Membership).filter(
        Membership.circle_id == circle_id,
        Membership.user_id == user_id
    ).first()
    if not membership:
        raise ValueError("You are not a member of this circle")
    return membership

def join_circle(db: Session, circle_id: int, user_id: int, data: JoinCircle) -> Membership:
    _get_circle_or_raise(db, circle_id)

    already_member = db.query(Membership).filter(
        Membership.circle_id == circle_id,
        Membership.user_id == user_id
    ).first()
    if already_member:
        raise ValueError("You are already a member of this circle")

    # Place at end of queue
    max_order = db.query(Membership).filter(
        Membership.circle_id == circle_id
    ).count()

    membership = Membership(
        user_id=user_id,
        circle_id=circle_id,
        display_name=data.display_name,
        order=max_order  # 0-indexed, so count = next slot
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership

def leave_circle(db: Session, circle_id: int, user_id: int) -> None:
    circle = _get_circle_or_raise(db, circle_id)

    if circle.owner_id == user_id:
        raise ValueError("Owner cannot leave their own circle — transfer ownership or delete it")

    membership = _get_membership_or_raise(db, circle_id, user_id)
    leaving_order = membership.order

    db.delete(membership)

    # Close the gap in order sequence
    remaining = db.query(Membership).filter(
        Membership.circle_id == circle_id,
        Membership.order > leaving_order
    ).all()
    for m in remaining:
        m.order -= 1

    db.commit()

def get_members(db: Session, circle_id: int, user_id: int) -> tuple[list[Membership], bool]:
    circle = _get_circle_or_raise(db, circle_id)
    _get_membership_or_raise(db, circle_id, user_id)

    members = db.query(Membership).filter(
        Membership.circle_id == circle_id
    ).order_by(Membership.order).all()

    return members, circle.is_anonymous

def remove_member(db: Session, circle_id: int, membership_id: int, user_id: int) -> None:
    circle = _get_circle_or_raise(db, circle_id)

    if circle.owner_id != user_id:
        raise ValueError("Only the owner can remove members")

    membership = db.query(Membership).filter(
        Membership.id == membership_id,
        Membership.circle_id == circle_id
    ).first()
    if not membership:
        raise ValueError("Member not found")
    if membership.user_id == user_id:
        raise ValueError("Owner cannot remove themselves")

    leaving_order = membership.order
    db.delete(membership)

    # Close the gap in order sequence
    remaining = db.query(Membership).filter(
        Membership.circle_id == circle_id,
        Membership.order > leaving_order
    ).all()
    for m in remaining:
        m.order -= 1

    db.commit()