"""
Django email backend for Freesend.

Settings::

    EMAIL_BACKEND = "freesend.django.FreesendEmailBackend"
    FREESEND_API_KEY = "sk_live_..."
    FREESEND_API_URL = "https://freesend.keybee.app"  # optional
    DEFAULT_FROM_EMAIL = "you@yourdomain.com"

Then use Django's standard email API unchanged::

    from django.core.mail import send_mail, EmailMultiAlternatives

    send_mail("Subject", "Body", None, ["user@example.com"])
"""

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

from .client import Freesend, FreesendError


class FreesendEmailBackend(BaseEmailBackend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        api_key = getattr(settings, "FREESEND_API_KEY", None)
        if not api_key:
            raise ValueError("FREESEND_API_KEY is not set in Django settings.")
        base_url = getattr(settings, "FREESEND_API_URL", "https://freesend.keybee.app")
        self._freesend = Freesend(api_key=api_key, base_url=base_url)

    def send_messages(self, email_messages):
        sent = 0
        for message in email_messages:
            try:
                self._send(message)
                sent += 1
            except FreesendError:
                if not self.fail_silently:
                    raise
            except Exception:
                if not self.fail_silently:
                    raise
        return sent

    def _send(self, message):
        recipients = message.to + message.cc + message.bcc
        if not recipients:
            return

        payload = {
            "from_": message.from_email,
            "to": recipients,
            "subject": message.subject,
            "text": message.body or None,
        }

        for content, mimetype in getattr(message, "alternatives", []):
            if mimetype == "text/html":
                payload["html"] = content
                break

        self._freesend.send(**payload)

    def close(self):
        self._freesend.close()
