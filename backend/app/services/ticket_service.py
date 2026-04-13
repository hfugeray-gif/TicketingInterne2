from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.ticket import Ticket
from app.repositories.ticket_repository import (
    create_ticket as repo_create_ticket,
    get_ticket as repo_get_ticket,
    get_tickets as repo_get_tickets,
    update_ticket as repo_update_ticket,
)

VALID_TYPES = {"Infra", "Numérique"}
VALID_STATUSES = {"Ouvert", "En cours", "Clôturé"}
VALID_PRIORITIES = {"Basse", "Normale", "Haute"}


def resolve_dispatcher(typage: str | None) -> str | None:
    if typage == "Infra":
        return "DIO"
    if typage == "Numérique":
        return "DSN"
    return None


def validate_ticket_creation_data(data: dict) -> dict:
    typage = data.get("typage")
    if typage not in VALID_TYPES:
        raise ValueError(f"Type non autorisé : {typage}")

    data["dispatcheur"] = resolve_dispatcher(typage)
    data["statut"] = "Ouvert"
    data.setdefault("priorite", "Normale")
    return data


def apply_ticket_updates(ticket: Ticket, updates: dict) -> Ticket:
    previous_status = ticket.statut

    if "typage" in updates and updates["typage"] is not None:
        if updates["typage"] not in VALID_TYPES:
            raise ValueError(f"Type non autorisé : {updates['typage']}")
        ticket.typage = updates["typage"]
        ticket.dispatcheur = resolve_dispatcher(ticket.typage)

    if "site" in updates:
        ticket.site = updates["site"]

    if "sous_type" in updates:
        ticket.sous_type = updates["sous_type"]

    if "titre" in updates and updates["titre"] is not None:
        ticket.titre = updates["titre"]

    if "commentaire" in updates:
        ticket.commentaire = updates["commentaire"]

    if "priorite" in updates and updates["priorite"] is not None:
        if updates["priorite"] not in VALID_PRIORITIES:
            raise ValueError(f"Priorité non autorisée : {updates['priorite']}")
        ticket.priorite = updates["priorite"]

    if "assigne_a" in updates:
        ticket.assigne_a = updates["assigne_a"]

    if "motif_resolution" in updates:
        ticket.motif_resolution = updates["motif_resolution"]

    if "ticket_maitre_id" in updates:
        ticket.ticket_maitre_id = updates["ticket_maitre_id"]

    if "statut" in updates and updates["statut"] is not None:
        new_status = updates["statut"]
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Statut non autorisé : {new_status}")

        if new_status == "Clôturé":
            motif = updates.get("motif_resolution", ticket.motif_resolution)
            if not motif or not str(motif).strip():
                raise ValueError("Le motif de résolution est obligatoire pour clôturer.")
            if previous_status != "Clôturé":
                ticket.closed_at = datetime.utcnow()
        elif previous_status == "Clôturé" and new_status != "Clôturé":
            ticket.closed_at = None

        ticket.statut = new_status

    ticket.updated_at = datetime.utcnow()
    return ticket


def create_ticket(db: Session, payload) -> Ticket:
    data = payload.model_dump() if hasattr(payload, "model_dump") else dict(payload)
    data = validate_ticket_creation_data(data)
    return repo_create_ticket(db, data)


def list_tickets(db: Session) -> list[Ticket]:
    return repo_get_tickets(db)


def get_ticket_by_id(db: Session, ticket_id: int) -> Ticket | None:
    return repo_get_ticket(db, ticket_id)


def update_ticket(db: Session, ticket_id: int, payload) -> Ticket:
    ticket = repo_get_ticket(db, ticket_id)
    if not ticket:
        raise ValueError("Ticket introuvable")

    updates = (
        payload.model_dump(exclude_unset=True)
        if hasattr(payload, "model_dump")
        else dict(payload)
    )

    ticket = apply_ticket_updates(ticket, updates)
    return repo_update_ticket(db, ticket)


def merge_tickets_into_master(
    db: Session,
    master_ticket: Ticket,
    child_tickets: list[Ticket],
    auteur: str,
):
    if master_ticket.statut == "Clôturé":
        raise ValueError("Impossible de fusionner vers un ticket maître clôturé.")

    merged = []

    for child in child_tickets:
        if child.id == master_ticket.id:
            continue

        if child.statut == "Clôturé":
            raise ValueError(f"Le ticket #{child.id} est clôturé et ne peut pas être fusionné.")

        if child.typage != master_ticket.typage:
            raise ValueError(
                f"Le ticket #{child.id} n'a pas le même type que le maître."
            )

        child.ticket_maitre_id = master_ticket.id
        child.statut = master_ticket.statut
        child.updated_at = datetime.utcnow()
        merged.append(child)

    return merged


def remove_ticket_from_master(ticket: Ticket):
    if not ticket.ticket_maitre_id:
        raise ValueError("Ce ticket n'est pas rattaché à un ticket maître.")

    ticket.ticket_maitre_id = None
    ticket.statut = "Ouvert"
    ticket.updated_at = datetime.utcnow()
    return ticket


def cascade_close_children(db: Session, master_ticket: Ticket):
    children = (
        db.query(Ticket)
        .filter(Ticket.ticket_maitre_id == master_ticket.id, Ticket.statut != "Clôturé")
        .all()
    )

    for child in children:
        child.statut = "Clôturé"
        child.motif_resolution = (
            f"Clôture automatique suite à la clôture du ticket maître #{master_ticket.id}"
        )
        child.closed_at = datetime.utcnow()
        child.updated_at = datetime.utcnow()

    return children