from core.api_client import api_get, api_patch, api_post


def api_create_ticket(
    titre: str,
    typage: str,
    site: str | None,
    commentaire: str | None,
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


def api_get_tickets():
    return api_get("/tickets/")


def api_get_ticket(ticket_id: int):
    return api_get(f"/tickets/{ticket_id}")


def api_update_ticket(ticket_id: int, payload: dict):
    return api_patch(f"/tickets/{ticket_id}", payload)


def api_get_comments(ticket_id: int):
    return api_get(f"/tickets/{ticket_id}/comments/")


def api_add_comment(ticket_id: int, auteur: str, contenu: str):
    return api_post(
        f"/tickets/{ticket_id}/comments/",
        {
            "auteur": auteur,
            "contenu": contenu,
        },
    )


def api_get_journal(ticket_id: int):
    return api_get(f"/tickets/{ticket_id}/journal/")


def api_merge_tickets(master_ticket_id: int, child_ticket_ids: list[int], auteur: str):
    return api_post(
        f"/tickets/{master_ticket_id}/merge",
        {
            "child_ticket_ids": child_ticket_ids,
            "auteur": auteur,
        },
    )


def api_unmerge_ticket(ticket_id: int, auteur: str):
    return api_post(
        f"/tickets/{ticket_id}/unmerge",
        {
            "auteur": auteur,
        },
    )


def api_get_child_tickets(ticket_id: int):
    return api_get(f"/tickets/{ticket_id}/children")