import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_FROM,
    SMTP_USE_TLS,
    SMTP_USE_AUTH,
    DEMO_EMAIL,
    DISPATCH_EMAILS,
    TECH_EMAILS,
    APP_BASE_URL,
)


# --------------------------------------------------
# 🎨 Helpers de rendu email
# --------------------------------------------------
def _build_email_html(
    title: str,
    intro: str,
    fields: list[tuple[str, str]],
    footer_note: str,
    cta_label: str | None = None,
    cta_url: str | None = None,
) -> str:
    """
    Construit un email HTML homogène au style Ticketing Beam.
    """
    fields_html = "".join(
        f"""
        <tr>
            <td style="padding:10px 0; color:#5f6c7b; font-size:14px; width:160px; vertical-align:top;">
                <strong>{label}</strong>
            </td>
            <td style="padding:10px 0; color:#12344d; font-size:14px;">
                {value}
            </td>
        </tr>
        """
        for label, value in fields
    )

    cta_html = ""
    if cta_label and cta_url:
        cta_html = f"""
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin-top:24px;">
            <tr>
                <td align="left">
                    <a href="{cta_url}" target="_blank"
                    style="
                            background-color:#111111;
                            color:#ffffff;
                            text-decoration:none;
                            padding:12px 20px;
                            font-size:14px;
                            font-weight:600;
                            border-radius:8px;
                            display:inline-block;
                    ">
                        {cta_label}
                    </a>
                </td>
            </tr>
        </table>
        """

    return f"""
    <html>
        <body style="margin:0; padding:0; background:#f4f6f8; font-family:Arial, Helvetica, sans-serif;">
            <div style="padding:32px 16px;">
                <div style="
                    max-width:640px;
                    margin:0 auto;
                    background:#ffffff;
                    border-radius:14px;
                    overflow:hidden;
                    box-shadow:0 6px 24px rgba(0,0,0,0.08);
                    border:1px solid #e5e7eb;
                ">
                    <!-- Header -->
                    <div style="background:#004034; padding:22px 24px;">
                        <div style="color:#ffffff; font-size:13px; letter-spacing:0.4px; opacity:0.9; margin-bottom:8px;">
                            TICKETING BEAM
                        </div>
                        <h1 style="margin:0; color:#ffffff; font-size:24px; line-height:1.2;">
                            {title}
                        </h1>
                    </div>

                    <!-- Content -->
                    <div style="padding:24px;">
                        <p style="margin:0 0 20px; color:#12344d; font-size:15px; line-height:1.6;">
                            {intro}
                        </p>

                        <table style="width:100%; border-collapse:collapse;">
                            {fields_html}
                        </table>

                        {cta_html}

                        <div style="
                            margin-top:24px;
                            padding:14px 16px;
                            background:#f8fafc;
                            border:1px solid #e5e7eb;
                            border-radius:10px;
                            color:#5f6c7b;
                            font-size:13px;
                            line-height:1.5;
                        ">
                            {footer_note}
                        </div>
                    </div>

                    <!-- Footer -->
                    <div style="
                        background:#f4f6f8;
                        padding:14px 18px;
                        color:#6b7280;
                        font-size:12px;
                        text-align:center;
                        border-top:1px solid #e5e7eb;
                    ">
                        Notification automatique — Ticketing Beam
                    </div>
                </div>
            </div>
        </body>
    </html>
    """


def _build_email_text(title: str, fields: list[tuple[str, str]], footer_note: str) -> str:
    """
    Construit une version texte simple du mail.
    """
    lines = [title, ""]
    for label, value in fields:
        lines.append(f"{label}: {value}")
    lines.append("")
    lines.append(footer_note)
    lines.append("")
    lines.append("Notification automatique - Ticketing Beam")
    return "\n".join(lines)


def get_ticket_url(ticket_id: int) -> str:
    """
    Retourne l'URL de redirection vers l'application.
    En Streamlit multipage, on ne peut pas toujours deep-linker proprement
    sur un ticket précis sans logique dédiée, donc on renvoie vers l'app.
    """
    return APP_BASE_URL

# --------------------------------------------------
# 📧 Envoi email
# --------------------------------------------------
def send_email(subject: str, html_body: str, to_email: str, text_body: str | None = None) -> bool:
    """
    Envoie un email HTML avec fallback texte.
    Compatible avec un SMTP de test sans authentification.
    """
    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject

    if text_body:
        msg.attach(MIMEText(text_body, "plain", "utf-8"))

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            if SMTP_USE_TLS:
                server.starttls()

            if SMTP_USE_AUTH:
                raise NotImplementedError("SMTP auth non configuré pour ce mode.")

            server.sendmail(SMTP_FROM, [to_email], msg.as_string())

        return True

    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


# --------------------------------------------------
# 👥 Résolution des destinataires
# --------------------------------------------------
def get_dispatch_email(typage: str) -> str:
    """
    Retourne l'email du dispatcheur selon le type.
    En démo, tout renvoie vers DEMO_EMAIL.
    """
    return DISPATCH_EMAILS.get(typage, DEMO_EMAIL)


def get_tech_email(tech_username: str | None) -> str:
    """
    Retourne l'email du technicien assigné.
    En démo, tout renvoie vers DEMO_EMAIL.
    """
    if not tech_username:
        return DEMO_EMAIL
    return TECH_EMAILS.get(tech_username, DEMO_EMAIL)


def get_user_email(username: str | None) -> str:
    """
    Retourne l'email de l'utilisateur.
    En démo, tout renvoie vers DEMO_EMAIL.
    """
    return DEMO_EMAIL if username else DEMO_EMAIL


# --------------------------------------------------
# 🔔 Notifications métier
# --------------------------------------------------
def notify_dispatch_new_ticket(ticket_id: int, titre: str, typage: str, demandeur: str) -> bool:
    to_email = get_dispatch_email(typage)
    subject = f"[Ticketing] Nouveau ticket #{ticket_id} - {titre}"

    fields = [
        ("ID", f"#{ticket_id}"),
        ("Titre", titre),
        ("Type", typage),
        ("Demandeur", demandeur),
    ]

    html_body = _build_email_html(
        title="Nouveau ticket à dispatcher",
        intro="Un nouveau ticket vient d’être créé et nécessite une affectation.",
        fields=fields,
        footer_note="Merci de procéder au dispatch vers le bon technicien ou la bonne équipe de traitement.",
        cta_label="Ouvrir le ticketing",
        cta_url=get_ticket_url(ticket_id),
    )

    text_body = _build_email_text(
        title="Nouveau ticket à dispatcher",
        fields=fields,
        footer_note="Merci de procéder à l'affectation.",
    )

    return send_email(subject, html_body, to_email, text_body)


def notify_technician_assignment(
    ticket_id: int,
    titre: str,
    technicien: str,
    statut: str,
    priorite: str | None,
) -> bool:
    to_email = get_tech_email(technicien)
    subject = f"[Ticketing] Ticket assigné #{ticket_id} - {titre}"

    fields = [
        ("ID", f"#{ticket_id}"),
        ("Titre", titre),
        ("Assigné à", technicien),
        ("Statut", statut),
        ("Priorité", priorite or "-"),
    ]

    html_body = _build_email_html(
        title="Un ticket vous a été assigné",
        intro="Un ticket vient de vous être attribué dans le portail Ticketing Beam.",
        fields=fields,
        footer_note="Merci de prendre en charge ce ticket dans les meilleurs délais.",
        cta_label="Ouvrir le ticketing",
        cta_url=get_ticket_url(ticket_id),
    )

    text_body = _build_email_text(
        title="Un ticket vous a été assigné",
        fields=fields,
        footer_note="Merci de prendre ce ticket en charge.",
    )

    return send_email(subject, html_body, to_email, text_body)

def notify_new_comment(
    ticket_id: int,
    titre: str,
    auteur: str,
    destinataire_email: str,
    contenu: str,
) -> bool:
    subject = f"[Ticketing] Nouveau commentaire - Ticket #{ticket_id}"

    fields = [
        ("ID", f"#{ticket_id}"),
        ("Titre", titre),
        ("Auteur", auteur),
        ("Commentaire", contenu.replace("\n", "<br>")),
    ]

    html_body = _build_email_html(
        title="Nouveau commentaire sur un ticket",
        intro="Un nouveau commentaire a été ajouté sur un ticket que vous suivez.",
        fields=fields,
        footer_note="Connectez-vous au portail Ticketing Beam pour consulter le détail du ticket et poursuivre les échanges.",
        cta_label="Ouvrir le ticketing",
        cta_url=get_ticket_url(ticket_id),
    )

    text_body = _build_email_text(
        title="Nouveau commentaire sur un ticket",
        fields=[
            ("ID", f"#{ticket_id}"),
            ("Titre", titre),
            ("Auteur", auteur),
            ("Commentaire", contenu),
        ],
        footer_note="Connectez-vous au portail Ticketing Beam pour consulter le détail du ticket.",
    )

    return send_email(subject, html_body, destinataire_email, text_body)

def notify_user_closure(
    ticket_id: int,
    titre: str,
    demandeur: str,
    motif_resolution: str | None,
) -> bool:
    to_email = get_user_email(demandeur)
    subject = f"[Ticketing] Ticket clôturé #{ticket_id} - {titre}"

    fields = [
        ("ID", f"#{ticket_id}"),
        ("Titre", titre),
        ("Demandeur", demandeur),
        ("Motif de résolution", motif_resolution or "-"),
    ]

    html_body = _build_email_html(
        title="Votre ticket a été clôturé",
        intro="Le traitement de votre demande est terminé.",
        fields=fields,
        footer_note="Si le problème persiste, vous pourrez créer un nouveau ticket ou revenir vers le support.",
        cta_label="Accéder au portail",
        cta_url=get_ticket_url(ticket_id),
    )

    text_body = _build_email_text(
        title="Votre ticket a été clôturé",
        fields=fields,
        footer_note="Le traitement est terminé.",
    )

    return send_email(subject, html_body, to_email, text_body)

def notify_user_ticket_merged(
    child_ticket_id: int,
    master_ticket_id: int,
    master_title: str,
    demandeur: str,
) -> bool:
    to_email = get_user_email(demandeur)
    subject = f"[Ticketing] Ticket fusionné #{child_ticket_id} vers #{master_ticket_id}"

    fields = [
        ("Ticket initial", f"#{child_ticket_id}"),
        ("Ticket maître", f"#{master_ticket_id}"),
        ("Titre du ticket maître", master_title),
        ("Demandeur", demandeur),
    ]

    html_body = _build_email_html(
        title="Votre ticket a été fusionné",
        intro="Votre ticket a été rattaché à un ticket maître déjà existant afin de centraliser le traitement.",
        fields=fields,
        footer_note="Vous pourrez désormais suivre l’avancement du ticket maître, qui regroupe le traitement de la demande.",
        cta_label="Ouvrir le ticketing",
        cta_url=get_ticket_url(master_ticket_id),
    )

    text_body = _build_email_text(
        title="Votre ticket a été fusionné",
        fields=fields,
        footer_note="Vous pouvez désormais suivre le ticket maître dans le portail.",
    )

    return send_email(subject, html_body, to_email, text_body)