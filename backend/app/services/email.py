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


async def send_email(
    to: str, subject: str, body_text: str, body_html: str | None = None
) -> None:
    """Send an email via SMTP. If body_html is provided, sends multipart
    with plain-text fallback; otherwise sends plain-text only."""
    if not _smtp_ready():
        log.warning("smtp_not_configured", to=to, subject=subject)
        return

    msg = email.message.EmailMessage()
    msg["From"] = settings.smtp_sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body_text)
    if body_html:
        msg.add_alternative(body_html, subtype="html")

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

    # Plain-text fallback
    body_text = (
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

    # HTML version with inline styles (brand colors from global.css)
    body_html = """\
<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#FAFAF8;font-family:'Public Sans',system-ui,-apple-system,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#FAFAF8;">
    <tr><td align="center" style="padding:40px 16px;">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#ffffff;border:1px solid #e5e0d8;border-radius:8px;">
        <!-- Logo -->
        <tr><td style="padding:32px 40px 24px 40px;text-align:center;">
          <span style="font-family:'Source Serif 4',Georgia,serif;font-size:28px;font-weight:700;color:#1a1a1a;">pre<span style="color:#8B2626;">.</span>voto</span>
        </td></tr>
        <!-- Body -->
        <tr><td style="padding:0 40px;">
          <p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#1a1a1a;">Hola,</p>
          <p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#1a1a1a;">Te suscribiste a pre.voto. Gracias.</p>
          <p style="margin:0 0 24px 0;font-size:16px;line-height:1.6;color:#4a4a4a;">Somos una br\u00fajula electoral independiente para Colombia 2026: sin medio detr\u00e1s, sin financiamiento de campa\u00f1as, sin pauta comercial.</p>
          <p style="margin:0 0 12px 0;font-size:16px;line-height:1.6;color:#1a1a1a;font-weight:600;">\u00bfQu\u00e9 vas a recibir?</p>
          <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 24px 0;">
            <tr><td style="padding:4px 0;font-size:16px;line-height:1.6;color:#4a4a4a;"><span style="color:#8B2626;margin-right:8px;">&#10003;</span> An\u00e1lisis de los candidatos con fuentes citadas.</td></tr>
            <tr><td style="padding:4px 0;font-size:16px;line-height:1.6;color:#4a4a4a;"><span style="color:#8B2626;margin-right:8px;">&#10003;</span> Actualizaciones de encuestas.</td></tr>
            <tr><td style="padding:4px 0;font-size:16px;line-height:1.6;color:#4a4a4a;"><span style="color:#8B2626;margin-right:8px;">&#10003;</span> Recordatorios electorales antes del 31 de mayo.</td></tr>
          </table>
          <p style="margin:0 0 24px 0;font-size:16px;line-height:1.6;color:#1a1a1a;">Si quer\u00e9s comparar tus posiciones con las de los 12 candidatos, el quiz toma 5 minutos:</p>
          <!-- CTA Button -->
          <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 auto 32px auto;">
            <tr><td align="center" style="background-color:#8B2626;border-radius:6px;">
              <a href="https://pre.voto/co/quiz" target="_blank" style="display:inline-block;padding:14px 32px;font-size:16px;font-weight:600;color:#ffffff;text-decoration:none;font-family:'Public Sans',system-ui,-apple-system,sans-serif;">Hacer el quiz</a>
            </td></tr>
          </table>
          <p style="margin:0 0 8px 0;font-size:16px;line-height:1.6;color:#1a1a1a;">\u2014 Equipo pre.voto</p>
        </td></tr>
        <!-- Footer -->
        <tr><td style="padding:24px 40px 32px 40px;">
          <hr style="border:none;border-top:1px solid #e5e0d8;margin:0 0 16px 0;">
          <p style="margin:0;font-size:13px;line-height:1.5;color:#737373;">Pre.voto es una iniciativa independiente, sin afiliaci\u00f3n partidaria, sin pauta comercial y sin contenido patrocinado. Para consultas: <a href="mailto:hola@pre.voto" style="color:#8B2626;text-decoration:underline;">hola@pre.voto</a>.</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    await send_email(recipient, subject, body_text, body_html=body_html)


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
