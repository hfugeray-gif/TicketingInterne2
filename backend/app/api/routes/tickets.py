from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.repositories.journal_repository import log_action
from app.services.notification_service import (
    notify_ticket_assigned,
    notify_ticket_closed,
    notify_ticket_created,
)
from app.services.ticket_service import (
    create_ticket,
    get_ticket_by_id,
    list_tickets,
    update_ticket,
)

router = APIRouter()


@router.post("/", response_model=TicketResponse)
def create_ticket_route(payload: TicketCreate, db: Session = Depends(get_db)):
    ticket = create_ticket(db, payload)

    log_action(
        db=db,
        ticket_id=ticket.id,
        action="ticket_created",
        auteur=ticket.demandeur,
        details=f"Ticket créé ({ticket.typage} - {ticket.site or '-'})",
    )

    notify_ticket_created(ticket)
    return ticket


@router.get("/", response_model=list[TicketResponse])
def list_tickets_route(db: Session = Depends(get_db)):
    return list_tickets(db)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket_route(ticket_id: int, db: Session = Depends(get_db)):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket_route(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
):
    existing_ticket = get_ticket_by_id(db, ticket_id)
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable")

    old_assignee = existing_ticket.assigne_a
    old_status = existing_ticket.statut

    try:
        ticket = update_ticket(db, ticket_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    changes = payload.model_dump(exclude_unset=True)
    if changes:
        details = ", ".join(f"{key}={value}" for key, value in changes.items())
        log_action(
            db=db,
            ticket_id=ticket.id,
            action="ticket_updated",
            auteur="system_api",
            details=details,
        )

    if "assigne_a" in changes and ticket.assigne_a != old_assignee:
        notify_ticket_assigned(ticket)

    if "statut" in changes and ticket.statut == "Clôturé" and old_status != "Clôturé":
        notify_ticket_closed(ticket)

    return ticket