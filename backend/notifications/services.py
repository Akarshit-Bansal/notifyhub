import json
import requests
import smtplib

from email.message import EmailMessage

from django.conf import settings
from pywebpush import webpush, WebPushException

from .models import PushSubscription


def render(s, ctx):
    for k, v in ctx.items():
        s = s.replace("{{" + k + "}}", str(v))
    return s


def twilio_whatsapp(template, recipient, ctx):
    if not settings.KAPSO_API_KEY:
        raise RuntimeError("Kapso API key is not configured.")

    if not settings.KAPSO_PHONE_NUMBER_ID:
        raise RuntimeError("Kapso phone number ID is not configured.")

    to = "".join(c for c in str(recipient) if c.isdigit())

    if not to:
        raise RuntimeError("WhatsApp recipient is required.")

    message = render(template.body, ctx)

    url = (
        "https://api.kapso.ai/meta/whatsapp/v24.0/"
        f"{settings.KAPSO_PHONE_NUMBER_ID}/messages"
    )

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(
        url,
        json=payload,
        headers={
            "X-API-Key": settings.KAPSO_API_KEY,
            "Content-Type": "application/json",
        },
        timeout=20,
    )

    if not response.ok:
        raise RuntimeError(
            f"Kapso WhatsApp: {response.status_code} {response.text}"
        )

    result = response.json()

    return (
        result.get("messages", [{}])[0].get("id", "")
        if result.get("messages")
        else ""
    )


def email_smtp(template, recipient, ctx):
    if not settings.EMAIL_HOST_USER:
        raise RuntimeError("Email SMTP username is not configured.")

    if not settings.EMAIL_HOST_PASSWORD:
        raise RuntimeError("Email SMTP password is not configured.")

    msg = EmailMessage()

    msg["From"] = settings.DEFAULT_FROM_EMAIL
    msg["To"] = recipient
    msg["Subject"] = render(
        template.subject or template.name,
        ctx,
    )

    msg.set_content(
        render(template.body, ctx)
    )

    try:
        with smtplib.SMTP(
            settings.EMAIL_HOST,
            settings.EMAIL_PORT,
            timeout=20,
        ) as server:

            if settings.EMAIL_USE_TLS:
                server.starttls()

            server.login(
                settings.EMAIL_HOST_USER,
                settings.EMAIL_HOST_PASSWORD,
            )

            server.send_message(msg)

    except Exception as e:
        raise RuntimeError(f"Email SMTP: {e}")

    return "ethereal-sent"


def browser_push(template, ctx):
    if not settings.ONESIGNAL_APP_ID:
        raise RuntimeError("OneSignal App ID is not configured.")

    if not settings.ONESIGNAL_REST_API_KEY:
        raise RuntimeError("OneSignal REST API key is not configured.")

    payload = {
        "app_id": settings.ONESIGNAL_APP_ID,
        "target_channel": "push",
        "included_segments": ["Subscribed Users"],
        "headings": {
            "en": render(
                template.subject or template.name,
                ctx,
            )
        },
        "contents": {
            "en": render(
                template.body,
                ctx,
            )
        },
    }

    response = requests.post(
        "https://api.onesignal.com/notifications",
        json=payload,
        headers={
            "Authorization": (
                "Key "
                + settings.ONESIGNAL_REST_API_KEY
            ),
            "Content-Type": "application/json",
        },
        timeout=20,
    )

    if not response.ok:
        raise RuntimeError(
            f"OneSignal: {response.text}"
        )

    result = response.json()

    return result.get("id", "")

def send(template, recipient, ctx):
    if template.channel == "whatsapp":
        return twilio_whatsapp(
            template,
            recipient,
            ctx,
        )

    if template.channel == "email":
        return email_smtp(
            template,
            recipient,
            ctx,
        )

    if template.channel == "web_push":
        return browser_push(
            template,
            ctx,
        )

    raise RuntimeError(
        f"Unsupported channel: {template.channel}"
    )