import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def send_email(subject: str, html_body: str, to_email: str, text_body: str | None = None) -> bool:
    try:
        if not settings.emails_enabled:
            print(f"[INFO] Email skipped because EMAILS_ENABLED=false | to={to_email} | subject={subject}")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from
        msg["To"] = to_email

        if text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))

        msg.attach(MIMEText(html_body, "html", "utf-8"))

        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15)

        if settings.smtp_use_tls:
            server.starttls()

        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)

        server.sendmail(settings.smtp_from, [to_email], msg.as_string())
        server.quit()
        return True

    except Exception as e:
        print(f"[WARN] send_email failed | to={to_email} | subject={subject} | error={e}")
        return False