from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_list_ticket():
    payload = {
        "titre": "Ticket API test",
        "typage": "Infra",
        "site": "Siège",
        "commentaire": "Test intégration",
        "demandeur": "hugo",
    }

    create_response = client.post("/tickets/", json=payload)
    assert create_response.status_code == 200

    created = create_response.json()
    assert created["titre"] == "Ticket API test"
    assert created["typage"] == "Infra"
    assert created["site"] == "Siège"
    assert created["statut"] == "Ouvert"

    list_response = client.get("/tickets/")
    assert list_response.status_code == 200

    tickets = list_response.json()
    assert any(ticket["id"] == created["id"] for ticket in tickets)