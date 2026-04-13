from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.ticket import Ticket
from app.db.session import SessionLocal
from app.repositories.ticket_repository import get_ticket, update_ticket
from app.schemas.merge import MergeRequest, UnmergeRequest
from app.schemas.ticket import TicketResponse
from app.services.journal_service import log_action
from app.services.ticket_service import merge_tickets_into_master, remove_ticket_from_master
from app.services.notification_service import notify_ticket_merged

router = APIRouter(prefix="/tickets", tags=["merge"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{ticket_id}/children", response_model=list[TicketResponse])
def get_children(ticket_id: int, db: Session = Depends(get_db)):
    master = get_ticket(db, ticket_id)
    if not master:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")

    children = db.query(Ticket).filter(Ticket.ticket_maitre_id == ticket_id).all()
    return children


@router.post("/{ticket_id}/merge", response_model=list[TicketResponse])
def merge_into_master(ticket_id: int, payload: MergeRequest, db: Session = Depends(get_db)):
    master = get_ticket(db, ticket_id)
    if not master:
        raise HTTPException(status_code=404, detail="Ticket maître introuvable.")

    children = []
    for child_id in payload.child_ticket_ids:
        child = get_ticket(db, child_id)
        if not child:
            raise HTTPException(status_code=404, detail=f"Ticket enfant introuvable : {child_id}")
        children.append(child)

    try:
        merged = merge_tickets_into_master(db, master, children, payload.auteur)

        db.commit()
        for child in merged:
            db.refresh(child)
            log_action(
                db,
                ticket_id=child.id,
                action="Fusion",
                details=f"Ticket fusionné vers le maître #{master.id}",
                auteur=payload.auteur,
            )
            log_action(
                db,
                ticket_id=master.id,
                action="Fusion",
                details=f"Ticket esclave rattaché : #{child.id}",
                auteur=payload.auteur,
            )
            notify_ticket_merged(child, master)
        return merged
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{ticket_id}/unmerge", response_model=TicketResponse)
def unmerge_ticket(ticket_id: int, payload: UnmergeRequest, db: Session = Depends(get_db)):
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")

    old_master_id = ticket.ticket_maitre_id

    try:
        ticket = remove_ticket_from_master(ticket)
        ticket = update_ticket(db, ticket)

        log_action(
            db,
            ticket_id=ticket.id,
            action="Sortie de doublon",
            details=f"Ticket retiré du maître #{old_master_id}",
            auteur=payload.auteur,
        )
        if old_master_id:
            log_action(
                db,
                ticket_id=old_master_id,
                action="Sortie de doublon",
                details=f"Ticket esclave retiré : #{ticket.id}",
                auteur=payload.auteur,
            )

        return ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e