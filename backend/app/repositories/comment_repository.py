from sqlalchemy.orm import Session

from app.db.models.comment import Comment


def create_comment(db: Session, data: dict) -> Comment:
    comment = Comment(**data)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comments_by_ticket(db: Session, ticket_id: int) -> list[Comment]:
    return (
        db.query(Comment)
        .filter(Comment.ticket_id == ticket_id)
        .order_by(Comment.created_at.asc())
        .all()
    )