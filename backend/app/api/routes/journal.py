from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.ticket import Ticket
from app.db.models.journal import Journal
from app.db.session import get_db

router = APIRouter()


@router.get("/")
def get_journal(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable")

    entries = (
        db.query(Journal)
        .filter(Journal.ticket_id == ticket_id)
        .order_by(Journal.id.desc())
        .all()
    )

    return entries