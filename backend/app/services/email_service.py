import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_email(
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
) -> bool:
    """
    Envoie un email simple.
    Retourne True si l'envoi est réussi, False sinon.
    Ne lève pas d'exception pour éviter de casser les workflows métier.
    """

    if not settings.emails_enabled:
        return False

    if not to_email:
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg.set_content(text_body or "")

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        if settings.smtp_use_tls:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                server.starttls()
                if settings.smtp_username:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if settings.smtp_username:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)

        return True

    except Exception:
        return False