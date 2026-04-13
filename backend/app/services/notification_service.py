import logging
from html import escape

from app.core.config import settings
from app.services.email_service import send_email

logger = logging.getLogger(__name__)

USER_EMAIL_DOMAIN = "beam.local"

DISPATCH_EMAILS_BY_TYPE = {
    "Incident": "dio@beam.local",
    "Support": "dsn@beam.local",
}

TECH_EMAILS_BY_TYPE = {
    "Incident": "tech@beam.local",
    "Support": "tech@beam.local",
}


def _safe_notification_call(func, *args, **kwargs) -> bool:
    try:
        return bool(func(*args, **kwargs))
    except Exception as exc:
        logger.warning("Notification error in %s: %s", getattr(func, "__name__", "unknown"), exc)
        return False


def _user_email(username: str | None) -> str | None:
    if not username:
        return None

    username = username.strip()
    if not username:
        return None

    if "@" in username:
        return username

    return f"{username}@{USER_EMAIL_DOMAIN}"


def _dispatch_email_for(ticket_type: str | None) -> str | None:
    if not ticket_type:
        return None
    return DISPATCH_EMAILS_BY_TYPE.get(ticket_type)


def _tech_email_for(ticket_type: str | None) -> str | None:
    if not ticket_type:
        return None
    return TECH_EMAILS_BY_TYPE.get(ticket_type)


def get_ticket_url(ticket_id: int | None = None) -> str:
    base = settings.app_base_url.rstrip("/")
    if ticket_id is None:
        return base
    return f"{base}?ticket_id={ticket_id}"


def _ticket_subject_prefix(ticket) -> str:
    ticket_id = getattr(ticket, "id", "?")
    titre = getattr(ticket, "titre", "") or ""
    return f"Ticket #{ticket_id} - {titre}"


def notify_ticket_created(ticket) -> bool:
    to_email = _dispatch_email_for(getattr(ticket, "typage", None))
    if not to_email:
        return False

    subject = f"[Nouveau ticket] {_ticket_subject_prefix(ticket)}"
    ticket_url = get_ticket_url(getattr(ticket, "id", None))

    titre = escape(str(getattr(ticket, "titre", "") or ""))
    typage = escape(str(getattr(ticket, "typage", "") or ""))
    site = escape(str(getattr(ticket, "site", "") or ""))
    demandeur = escape(str(getattr(ticket, "demandeur", "") or ""))

    text_body = (
        f"Un nouveau ticket a été créé.\n\n"
        f"ID: {getattr(ticket, 'id', '?')}\n"
        f"Titre: {getattr(ticket, 'titre', '')}\n"
        f"Type: {getattr(ticket, 'typage', '')}\n"
        f"Site: {getattr(ticket, 'site', '')}\n"
        f"Demandeur: {getattr(ticket, 'demandeur', '')}\n\n"
        f"Ouvrir l'application: {ticket_url}"
    )

    html_body = f"""
    <html>
      <body>
        <h3>Nouveau ticket créé</h3>
        <p><strong>ID :</strong> {getattr(ticket, 'id', '?')}</p>
        <p><strong>Titre :</strong> {titre}</p>
        <p><strong>Type :</strong> {typage}</p>
        <p><strong>Site :</strong> {site}</p>
        <p><strong>Demandeur :</strong> {demandeur}</p>
        <p><a href="{ticket_url}">Ouvrir l'application</a></p>
      </body>
    </html>
    """

    return _safe_notification_call(
        send_email,
        to_email=to_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )


def notify_ticket_assigned(ticket) -> bool:
    assignee = getattr(ticket, "assigne_a", None)
    to_email = _user_email(assignee) or _tech_email_for(getattr(ticket, "typage", None))
    if not to_email:
        return False

    subject = f"[Assignation] {_ticket_subject_prefix(ticket)}"
    ticket_url = get_ticket_url(getattr(ticket, "id", None))

    text_body = (
        f"Un ticket vous a été assigné.\n\n"
        f"ID: {getattr(ticket, 'id', '?')}\n"
        f"Titre: {getattr(ticket, 'titre', '')}\n"
        f"Statut: {getattr(ticket, 'statut', '')}\n\n"
        f"Ouvrir l'application: {ticket_url}"
    )

    html_body = f"""
    <html>
      <body>
        <h3>Ticket assigné</h3>
        <p><strong>ID :</strong> {getattr(ticket, 'id', '?')}</p>
        <p><strong>Titre :</strong> {escape(str(getattr(ticket, 'titre', '') or ''))}</p>
        <p><strong>Statut :</strong> {escape(str(getattr(ticket, 'statut', '') or ''))}</p>
        <p><a href="{ticket_url}">Ouvrir l'application</a></p>
      </body>
    </html>
    """

    return _safe_notification_call(
        send_email,
        to_email=to_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )


def notify_ticket_closed(ticket) -> bool:
    to_email = _user_email(getattr(ticket, "demandeur", None))
    if not to_email:
        return False

    subject = f"[Clôture] {_ticket_subject_prefix(ticket)}"
    ticket_url = get_ticket_url(getattr(ticket, "id", None))

    text_body = (
        f"Votre ticket a été clôturé.\n\n"
        f"ID: {getattr(ticket, 'id', '?')}\n"
        f"Titre: {getattr(ticket, 'titre', '')}\n"
        f"Motif: {getattr(ticket, 'motif_resolution', '')}\n\n"
        f"Ouvrir l'application: {ticket_url}"
    )

    html_body = f"""
    <html>
      <body>
        <h3>Ticket clôturé</h3>
        <p><strong>ID :</strong> {getattr(ticket, 'id', '?')}</p>
        <p><strong>Titre :</strong> {escape(str(getattr(ticket, 'titre', '') or ''))}</p>
        <p><strong>Motif :</strong> {escape(str(getattr(ticket, 'motif_resolution', '') or ''))}</p>
        <p><a href="{ticket_url}">Ouvrir l'application</a></p>
      </body>
    </html>
    """

    return _safe_notification_call(
        send_email,
        to_email=to_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )


def notify_new_comment(ticket, comment) -> bool:
    demandeur_email = _user_email(getattr(ticket, "demandeur", None))
    assignee_email = _user_email(getattr(ticket, "assigne_a", None))
    comment_author = getattr(comment, "auteur", None)

    recipients = set()

    if demandeur_email and getattr(ticket, "demandeur", None) != comment_author:
        recipients.add(demandeur_email)

    if assignee_email and getattr(ticket, "assigne_a", None) != comment_author:
        recipients.add(assignee_email)

    if not recipients:
        return False

    subject = f"[Commentaire] {_ticket_subject_prefix(ticket)}"
    ticket_url = get_ticket_url(getattr(ticket, "id", None))
    contenu = escape(str(getattr(comment, "contenu", "") or ""))

    text_body = (
        f"Un nouveau commentaire a été ajouté.\n\n"
        f"Ticket: #{getattr(ticket, 'id', '?')} - {getattr(ticket, 'titre', '')}\n"
        f"Auteur: {getattr(comment, 'auteur', '')}\n"
        f"Commentaire: {getattr(comment, 'contenu', '')}\n\n"
        f"Ouvrir l'application: {ticket_url}"
    )

    html_body = f"""
    <html>
      <body>
        <h3>Nouveau commentaire</h3>
        <p><strong>Ticket :</strong> #{getattr(ticket, 'id', '?')} - {escape(str(getattr(ticket, 'titre', '') or ''))}</p>
        <p><strong>Auteur :</strong> {escape(str(getattr(comment, 'auteur', '') or ''))}</p>
        <p><strong>Commentaire :</strong><br>{contenu}</p>
        <p><a href="{ticket_url}">Ouvrir l'application</a></p>
      </body>
    </html>
    """

    success = False
    for recipient in recipients:
        sent = _safe_notification_call(
            send_email,
            to_email=recipient,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
        )
        success = success or sent

    return success


def notify_ticket_merged(ticket, master_ticket) -> bool:
    to_email = _user_email(getattr(ticket, "demandeur", None))
    if not to_email:
        return False

    subject = f"[Fusion] {_ticket_subject_prefix(ticket)}"
    ticket_url = get_ticket_url(getattr(master_ticket, "id", None))

    text_body = (
        f"Votre ticket a été rattaché à un ticket maître.\n\n"
        f"Ticket initial: #{getattr(ticket, 'id', '?')} - {getattr(ticket, 'titre', '')}\n"
        f"Ticket maître: #{getattr(master_ticket, 'id', '?')} - {getattr(master_ticket, 'titre', '')}\n\n"
        f"Ouvrir l'application: {ticket_url}"
    )

    html_body = f"""
    <html>
      <body>
        <h3>Ticket fusionné</h3>
        <p><strong>Ticket initial :</strong> #{getattr(ticket, 'id', '?')} - {escape(str(getattr(ticket, 'titre', '') or ''))}</p>
        <p><strong>Ticket maître :</strong> #{getattr(master_ticket, 'id', '?')} - {escape(str(getattr(master_ticket, 'titre', '') or ''))}</p>
        <p><a href="{ticket_url}">Ouvrir l'application</a></p>
      </body>
    </html>
    """

    return _safe_notification_call(
        send_email,
        to_email=to_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )