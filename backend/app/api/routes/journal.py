from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.ticket_repository import get_ticket
from app.repositories.journal_repository import get_journal_by_ticket
from app.schemas.journal import JournalResponse

router = APIRouter(prefix="/tickets/{ticket_id}/journal", tags=["journal"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[JournalResponse])
def list_journal(ticket_id: int, db: Session = Depends(get_db)):
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")
    return get_journal_by_ticket(db, ticket_id)