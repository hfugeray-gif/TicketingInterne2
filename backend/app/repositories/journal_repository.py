from sqlalchemy.orm import Session

from app.db.models.journal import Journal


def create_journal_entry(db: Session, data: dict) -> Journal:
    entry = Journal(**data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_journal_by_ticket(db: Session, ticket_id: int) -> list[Journal]:
    return (
        db.query(Journal)
        .filter(Journal.ticket_id == ticket_id)
        .order_by(Journal.created_at.desc())
        .all()
    )