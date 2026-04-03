from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.ticket_repository import get_ticket
from app.repositories.comment_repository import get_comments_by_ticket
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.comment_service import add_comment_to_ticket

router = APIRouter(prefix="/tickets/{ticket_id}/comments", tags=["comments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[CommentResponse])
def list_comments(ticket_id: int, db: Session = Depends(get_db)):
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")
    return get_comments_by_ticket(db, ticket_id)


@router.post("/", response_model=CommentResponse)
def create_comment_route(ticket_id: int, payload: CommentCreate, db: Session = Depends(get_db)):
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")

    try:
        return add_comment_to_ticket(db, ticket, payload.auteur, payload.contenu)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e