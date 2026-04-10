from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.repositories.ticket_repository import (
    create_ticket,
    get_ticket,
    get_tickets,
    update_ticket,
)
from app.services.journal_service import log_action
from app.services.ticket_service import (
    apply_ticket_updates,
    cascade_close_children,
    validate_ticket_creation_data,
)

from app.services.notification_service import (
    notify_dispatch_new_ticket,
    notify_technician_assignment,
    notify_user_closure,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=TicketResponse)
def create_ticket_route(payload: TicketCreate, db: Session = Depends(get_db)):
    try:
        data = validate_ticket_creation_data(payload.model_dump())
        ticket = create_ticket(db, data)
        log_action(
            db,
            ticket_id=ticket.id,
            action="Création",
            details=f"Ticket créé ({ticket.typage} - {ticket.site or '-'})",
            auteur=ticket.demandeur,
        )
        notify_dispatch_new_ticket(ticket)
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    return get_tickets(db)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket_route(ticket_id: int, db: Session = Depends(get_db)):
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket_route(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)):
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")

    previous_status = ticket.statut
    previous_assignee = ticket.assigne_a

    try:
        updates = payload.model_dump(exclude_unset=True)
        ticket = apply_ticket_updates(ticket, updates)
        ticket = update_ticket(db, ticket)

        log_action(
            db,
            ticket_id=ticket.id,
            action="Mise à jour",
            details="Mise à jour du ticket via API",
            auteur="system_api",
        )

        if previous_assignee != ticket.assigne_a and ticket.assigne_a:
            notify_technician_assignment(ticket)

        if previous_status != "Clôturé" and ticket.statut == "Clôturé":
            notify_user_closure(ticket)

        return ticket
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e