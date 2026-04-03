import pytest

from app.db.models.ticket import Ticket
from app.services.ticket_service import (
    apply_ticket_updates,
    resolve_dispatcher,
    validate_ticket_creation_data,
)


def test_resolve_dispatcher_infra():
    assert resolve_dispatcher("Infra") == "DIO"


def test_resolve_dispatcher_numerique():
    assert resolve_dispatcher("Numérique") == "DSN"


def test_validate_creation_sets_dispatcher_and_status():
    data = {
        "titre": "Test",
        "typage": "Infra",
        "site": "Siège",
        "commentaire": "Test",
        "demandeur": "alice",
    }
    out = validate_ticket_creation_data(data)
    assert out["dispatcheur"] == "DIO"
    assert out["statut"] == "Ouvert"


def test_validate_creation_invalid_type():
    data = {
        "titre": "Test",
        "typage": "Autre",
        "site": "Siège",
        "commentaire": "Test",
        "demandeur": "alice",
    }
    with pytest.raises(ValueError):
        validate_ticket_creation_data(data)


def test_close_ticket_requires_resolution_reason():
    ticket = Ticket(
        titre="T1",
        typage="Infra",
        statut="Ouvert",
        demandeur="alice",
    )
    with pytest.raises(ValueError):
        apply_ticket_updates(ticket, {"statut": "Clôturé"})


def test_close_ticket_sets_closed_at():
    ticket = Ticket(
        titre="T1",
        typage="Infra",
        statut="Ouvert",
        demandeur="alice",
    )
    updated = apply_ticket_updates(
        ticket,
        {"statut": "Clôturé", "motif_resolution": "Corrigé définitivement"},
    )
    assert updated.statut == "Clôturé"
    assert updated.closed_at is not None