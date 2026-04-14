from core.api_client import api_get, api_patch, api_post


def api_get_tickets():
    return api_get("/tickets/")


def api_get_ticket(ticket_id: int):
    return api_get(f"/tickets/{ticket_id}")


def api_update_ticket(ticket_id: int, payload: dict):
    return api_patch(f"/tickets/{ticket_id}", payload)


def api_create_ticket(
    titre: str,
    typage: str,
    site: str,
    commentaire: str,
    demandeur: str,
):
    payload = {
        "titre": titre,
        "typage": typage,
        "site": site,
        "commentaire": commentaire,
        "demandeur": demandeur,
    }
    return api_post("/tickets/", payload)


def api_get_comments(ticket_id: int):
    return api_get("/comments/", params={"ticket_id": ticket_id})


def api_add_comment(ticket_id: int, auteur: str, contenu: str):
    return api_post(
        f"/comments/?ticket_id={ticket_id}",
        {
            "auteur": auteur,
            "contenu": contenu,
        },
    )


def api_get_journal(ticket_id: int):
    return api_get("/journal/", params={"ticket_id": ticket_id})


def api_get_child_tickets(ticket_id: int):
    return api_get(f"/merge/{ticket_id}/children")


def api_merge_ticket(ticket_id: int, child_ids: list[int], auteur: str):
    return api_post(
        f"/merge/{ticket_id}/merge",
        {
            "child_ids": child_ids,
            "auteur": auteur,
        },
    )


def api_unmerge_ticket(ticket_id: int, auteur: str):
    return api_post(
        f"/merge/{ticket_id}/unmerge",
        {
            "auteur": auteur,
        },
    )


