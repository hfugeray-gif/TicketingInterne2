import pytest

from app.db.models.ticket import Ticket
from app.services.ticket_service import merge_tickets_into_master, remove_ticket_from_master


def test_merge_ticket_into_master():
    master = Ticket(id=1, titre="Master", typage="Infra", statut="Ouvert", demandeur="alice")
    child = Ticket(id=2, titre="Child", typage="Infra", statut="Ouvert", demandeur="bob")

    merged = merge_tickets_into_master(None, master, [child], "admin")

    assert len(merged) == 1
    assert child.ticket_maitre_id == 1
    assert child.statut == master.statut


def test_merge_rejects_different_type():
    master = Ticket(id=1, titre="Master", typage="Infra", statut="Ouvert", demandeur="alice")
    child = Ticket(id=2, titre="Child", typage="Numérique", statut="Ouvert", demandeur="bob")

    with pytest.raises(ValueError):
        merge_tickets_into_master(None, master, [child], "admin")


def test_unmerge_ticket():
    child = Ticket(
        id=2,
        titre="Child",
        typage="Infra",
        statut="En cours",
        demandeur="bob",
        ticket_maitre_id=1,
    )

    updated = remove_ticket_from_master(child)

    assert updated.ticket_maitre_id is None
    assert updated.statut == "Ouvert"