from sqlalchemy.orm import Session

from app.db.models.journal import Journal


def log_action(
    db: Session,
    ticket_id: int,
    action: str,
    auteur: str,
    details: str | None = None,
):
    entry = Journal(
        ticket_id=ticket_id,
        action=action,
        auteur=auteur,
        details=details,
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return entry