from sqlalchemy.orm import Session

from app.db.models.ticket import Ticket


def create_ticket(db: Session, data: dict) -> Ticket:
    ticket = Ticket(**data)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_tickets(db: Session) -> list[Ticket]:
    return db.query(Ticket).order_by(Ticket.created_at.desc()).all()


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def update_ticket(db: Session, ticket: Ticket) -> Ticket:
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket