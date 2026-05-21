"""
Async transactional email service using aiosmtplib.

Dev: Mailpit (localhost:8025, no auth)
Prod: Gmail SMTP (smtp.gmail.com:587, STARTTLS + auth)
"""

import email.message

import aiosmtplib
import structlog

from app.config import settings

log = structlog.get_logger()


def _smtp_ready() -> bool:
    """Return True if SMTP host is configured."""
    return bool(settings.smtp_host)


async def send_email(to: str, subject: str, body_text: str) -> None:
    """Send a plain-text email via SMTP."""
    if not _smtp_ready():
        log.warning("smtp_not_configured", to=to, subject=subject)
        return

    msg = email.message.EmailMessage()
    msg["From"] = settings.smtp_sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body_text)

    kwargs: dict = {
        "hostname": settings.smtp_host,
        "port": settings.smtp_port,
    }

    if settings.smtp_use_tls:
        kwargs["start_tls"] = True

    if settings.smtp_username:
        kwargs["username"] = settings.smtp_username
        kwargs["password"] = settings.smtp_password

    try:
        await aiosmtplib.send(msg, **kwargs)
        log.info("email_sent", to=to, subject=subject)
    except Exception:
        log.error("email_send_failed", to=to, subject=subject, exc_info=True)


async def send_welcome_email(recipient: str) -> None:
    """TX1: Welcome email for new home-form subscribers."""
    subject = "Gracias por sumarte a pre.voto"
    body = (
        "Hola,\n"
        "\n"
        "Te suscribiste a pre.voto. Gracias.\n"
        "\n"
        "Somos una brújula electoral independiente para Colombia 2026: "
        "sin medio detrás, sin financiamiento de campañas, sin pauta comercial.\n"
        "\n"
        "¿Qué vas a recibir?\n"
        "\n"
        "- Análisis de los candidatos con fuentes citadas.\n"
        "- Actualizaciones de encuestas.\n"
        "- Recordatorios electorales antes del 31 de mayo.\n"
        "\n"
        "Si querés comparar tus posiciones con las de los 12 candidatos, "
        "el quiz toma 5 minutos:\n"
        "\n"
        "https://pre.voto/co/quiz\n"
        "\n"
        "— Equipo pre.voto\n"
        "\n"
        "---\n"
        "Pre.voto es una iniciativa independiente, sin afiliación partidaria, "
        "sin pauta comercial y sin contenido patrocinado. "
        "Para consultas: hola@pre.voto.\n"
    )
    await send_email(recipient, subject, body)


async def send_donation_email(recipient: str, amount_display: str) -> None:
    """TX2: Thank-you email after a successful donation."""
    subject = "Gracias por apoyar pre.voto"
    body = (
        "Hola,\n"
        "\n"
        f"Recibimos tu donación de {amount_display}. Gracias.\n"
        "\n"
        "Pre.voto no tiene pauta comercial, no recibe plata de campañas y no "
        "vende datos. Lo que acabás de aportar va directo a mantener la "
        "infraestructura y el trabajo editorial del proyecto.\n"
        "\n"
        "¿En qué se usa?\n"
        "\n"
        "- Servidores y dominio.\n"
        "- Investigación y codificación de posiciones de los 12 candidatos.\n"
        "- Mantenimiento del quiz, las fichas y el agregador de encuestas.\n"
        "\n"
        "Si tenés alguna pregunta sobre el uso de los fondos o querés saber "
        "más sobre el proyecto, escribinos a hola@pre.voto.\n"
        "\n"
        "— Equipo pre.voto\n"
        "\n"
        "---\n"
        "Pre.voto es una iniciativa independiente, sin afiliación partidaria, "
        "sin pauta comercial y sin contenido patrocinado. "
        "Para consultas: hola@pre.voto.\n"
    )
    await send_email(recipient, subject, body)
