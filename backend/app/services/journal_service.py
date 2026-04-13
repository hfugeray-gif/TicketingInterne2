from sqlalchemy.orm import Session

from app.repositories.journal_repository import log_action


def log_action_service(
    db: Session,
    ticket_id: int,
    action: str,
    auteur: str,
    details: str | None = None,
):
    return log_action(
        db=db,
        ticket_id=ticket_id,
        action=action,
        auteur=auteur,
        details=details,
    )