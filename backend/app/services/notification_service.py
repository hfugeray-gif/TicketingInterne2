from app.core.config import settings
from app.services.email_service import send_email


DISPATCH_EMAILS = {
    "Infra": "dio@beam.local",
    "Numérique": "dsn@beam.local",
}

TECH_EMAILS = {
    "tech_infra_1": "tech_infra_1@beam.local",
    "tech_dsn_1": "tech_dsn_1@beam.local",
}

USER_EMAIL_DOMAIN = "beam.local"

def _safe_notification_call(func_name: str, fn):
    try:
        return fn()
    except Exception as e:
        print(f"[WARN] Notification '{func_name}' failed: {e}")
        return False


def get_ticket_url(ticket_id: int) -> str:
    return settings.app_base_url


def get_dispatch_email(typage: str | None) -> str | None:
    return DISPATCH_EMAILS.get(typage)


def get_tech_email(username: str | None) -> str | None:
    if not username:
        return None
    return TECH_EMAILS.get(username, f"{username}@{USER_EMAIL_DOMAIN}")


def get_user_email(username: str | None) -> str | None:
    if not username:
        return None
    return f"{username}@{USER_EMAIL_DOMAIN}"


def _build_email_html(
    title: str,
    intro: str,
    fields: list[tuple[str, str | None]],
    footer_note: str = "",
    cta_label: str = "Ouvrir l'application",
    cta_url: str | None = None,
) -> str:
    fields_html = "".join(
        f"""
        <tr>
            <td style="padding:8px 12px;border:1px solid #d9e2f2;font-weight:600;color:#12344d;">{label}</td>
            <td style="padding:8px 12px;border:1px solid #d9e2f2;color:#12344d;">{value or "-"}</td>
        </tr>
        """
        for label, value in fields
    )

    cta_html = ""
    if cta_url:
        cta_html = f"""
        <div style="margin-top:24px;">
            <a href="{cta_url}" style="
                background:#111111;
                color:#ffffff;
                text-decoration:none;
                padding:12px 18px;
                border-radius:10px;
                display:inline-block;
                font-weight:600;
            ">
                {cta_label}
            </a>
        </div>
        """

    return f"""
    <html>
      <body style="font-family:Arial,sans-serif;background:#f7f9fc;padding:24px;color:#12344d;">
        <div style="max-width:760px;margin:auto;background:#ffffff;border:1px solid #d9e2f2;border-radius:16px;padding:24px;">
          <h2 style="margin-top:0;color:#004034;">{title}</h2>
          <p>{intro}</p>
          <table style="border-collapse:collapse;width:100%;margin-top:16px;">
            {fields_html}
          </table>
          {cta_html}
          <p style="margin-top:24px;color:#5f6c7b;">{footer_note}</p>
        </div>
      </body>
    </html>
    """


def _build_email_text(
    title: str,
    fields: list[tuple[str, str | None]],
    footer_note: str = "",
) -> str:
    lines = [title, ""]
    lines.extend([f"{label}: {value or '-'}" for label, value in fields])
    if footer_note:
        lines.extend(["", footer_note])
    return "\n".join(lines)


def notify_dispatch_new_ticket(ticket) -> bool:
    def _run():
        to_email = get_dispatch_email(ticket.typage)
        if not to_email:
            return False

        subject = f"[Ticketing] Nouveau ticket #{ticket.id}"
        fields = [
            ("ID", f"#{ticket.id}"),
            ("Titre", ticket.titre),
            ("Type", ticket.typage),
            ("Site", ticket.site),
            ("Demandeur", ticket.demandeur),
        ]

        html_body = _build_email_html(
            title="Nouveau ticket créé",
            intro="Un nouveau ticket a été créé et nécessite une prise en charge.",
            fields=fields,
            footer_note="Connectez-vous au ticketing pour consulter le détail du ticket.",
            cta_label="Ouvrir le ticketing",
            cta_url=get_ticket_url(ticket.id),
        )

        text_body = _build_email_text(
            title="Nouveau ticket créé",
            fields=fields,
            footer_note="Connectez-vous au ticketing pour consulter le détail du ticket.",
        )

        return send_email(subject, html_body, to_email, text_body)

    return _safe_notification_call("notify_dispatch_new_ticket", _run)

def notify_technician_assignment(ticket) -> bool:
    def _run():
        to_email = get_tech_email(ticket.assigne_a)
        if not to_email:
            return False

        subject = f"[Ticketing] Ticket assigné #{ticket.id}"
        fields = [
            ("ID", f"#{ticket.id}"),
            ("Titre", ticket.titre),
            ("Type", ticket.typage),
            ("Site", ticket.site),
            ("Assigné à", ticket.assigne_a),
        ]

        html_body = _build_email_html(
            title="Un ticket vous a été assigné",
            intro="Un ticket vient de vous être attribué pour traitement.",
            fields=fields,
            footer_note="Consultez le ticketing pour le prendre en charge.",
            cta_label="Ouvrir le ticketing",
            cta_url=get_ticket_url(ticket.id),
        )

        text_body = _build_email_text(
            title="Un ticket vous a été assigné",
            fields=fields,
            footer_note="Consultez le ticketing pour le prendre en charge.",
        )

        return send_email(subject, html_body, to_email, text_body)
    return _safe_notification_call("notify_technician_assignment", _run)

def notify_user_closure(ticket) -> bool:
    def _run():
        to_email = get_user_email(ticket.demandeur)
        if not to_email:
            return False

        subject = f"[Ticketing] Ticket clôturé #{ticket.id}"
        fields = [
            ("ID", f"#{ticket.id}"),
            ("Titre", ticket.titre),
            ("Motif de résolution", ticket.motif_resolution),
        ]

        html_body = _build_email_html(
            title="Votre ticket a été clôturé",
            intro="Le traitement de votre ticket est terminé.",
            fields=fields,
            footer_note="Vous pouvez consulter le ticketing pour le détail.",
            cta_label="Ouvrir le ticketing",
            cta_url=get_ticket_url(ticket.id),
        )

        text_body = _build_email_text(
            title="Votre ticket a été clôturé",
            fields=fields,
            footer_note="Vous pouvez consulter le ticketing pour le détail.",
        )

        return send_email(subject, html_body, to_email, text_body)
    return _safe_notification_call("notify_user_closure", _run)

def notify_new_comment(ticket, auteur: str, contenu: str) -> bool:
        def _run():
            if auteur == ticket.demandeur:
                to_email = get_tech_email(ticket.assigne_a) or get_dispatch_email(ticket.typage)
            else:
                to_email = get_user_email(ticket.demandeur)

            if not to_email:
                return False

            subject = f"[Ticketing] Nouveau commentaire - Ticket #{ticket.id}"
            fields = [
                ("ID", f"#{ticket.id}"),
                ("Titre", ticket.titre),
                ("Auteur", auteur),
                ("Commentaire", contenu),
            ]

            html_body = _build_email_html(
                title="Nouveau commentaire sur un ticket",
                intro="Un nouveau commentaire a été ajouté sur un ticket que vous suivez.",
                fields=fields,
                footer_note="Consultez le ticketing pour voir le détail du ticket.",
                cta_label="Ouvrir le ticketing",
                cta_url=get_ticket_url(ticket.id),
            )

            text_body = _build_email_text(
                title="Nouveau commentaire sur un ticket",
                fields=fields,
                footer_note="Consultez le ticketing pour voir le détail du ticket.",
            )

            return send_email(subject, html_body, to_email, text_body)
        return _safe_notification_call("notify_new_comment", _run)

def notify_user_ticket_merged(child_ticket, master_ticket) -> bool:
    def _run():
        to_email = get_user_email(child_ticket.demandeur)
        if not to_email:
            return False

        subject = f"[Ticketing] Ticket fusionné #{child_ticket.id} vers #{master_ticket.id}"
        fields = [
            ("Ticket initial", f"#{child_ticket.id}"),
            ("Ticket maître", f"#{master_ticket.id}"),
            ("Titre du ticket maître", master_ticket.titre),
            ("Demandeur", child_ticket.demandeur),
        ]

        html_body = _build_email_html(
            title="Votre ticket a été fusionné",
            intro="Votre ticket a été rattaché à un ticket maître déjà existant afin de centraliser le traitement.",
            fields=fields,
            footer_note="Vous pouvez désormais suivre le ticket maître dans le ticketing.",
            cta_label="Ouvrir le ticketing",
            cta_url=get_ticket_url(master_ticket.id),
        )

        text_body = _build_email_text(
            title="Votre ticket a été fusionné",
            fields=fields,
            footer_note="Vous pouvez désormais suivre le ticket maître dans le ticketing.",
        )

        return send_email(subject, html_body, to_email, text_body)
    return _safe_notification_call("notify_user_ticket_merged", _run)
