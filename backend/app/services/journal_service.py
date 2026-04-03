from app.repositories.journal_repository import create_journal_entry


def log_action(db, ticket_id: int, action: str, details: str | None, auteur: str):
    return create_journal_entry(
        db,
        {
            "ticket_id": ticket_id,
            "action": action,
            "details": details,
            "auteur": auteur,
        },
    )