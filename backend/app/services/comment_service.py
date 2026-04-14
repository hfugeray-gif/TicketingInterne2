from datetime import datetime

from app.repositories.comment_repository import create_comment
from app.services.journal_service import log_action_service
from app.services.notification_service import notify_new_comment


def add_comment_to_ticket(db, ticket, auteur: str, contenu: str):
    if not contenu or not contenu.strip():
        raise ValueError("Le commentaire ne peut pas être vide.")

    comment = create_comment(
        db,
        {
            "ticket_id": ticket.id,
            "auteur": auteur,
            "contenu": contenu.strip(),
        },
    )

    ticket.updated_at = datetime.utcnow()
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    log_action_service(
        db,
        ticket_id=ticket.id,
        action="Commentaire",
        details=contenu.strip()[:200],
        auteur=auteur,
    )

    notify_new_comment(ticket, comment)

    return comment