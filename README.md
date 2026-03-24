# freesend-sdk

Python SDK and Django email backend for [Freesend](https://freesend.keybee.app).

## Installation

```bash
pip install git+https://github.com/hamptus/freesend-sdk.git
```

## Python SDK

```python
from freesend import Freesend

fs = Freesend("sk_live_...")

fs.send(
    from_="hello@yourdomain.com",
    to="user@example.com",
    subject="Hello",
    html="<p>Hello!</p>",
    text="Hello!",
)

# Context manager — closes the HTTP connection when done
with Freesend("sk_live_...") as fs:
    fs.send(...)
```

## Django

Add to `settings.py`:

```python
EMAIL_BACKEND = "freesend.django.FreesendEmailBackend"
FREESEND_API_KEY = env("FREESEND_API_KEY")  # sk_live_...
DEFAULT_FROM_EMAIL = "you@yourdomain.com"
```

Then use Django's standard email API unchanged:

```python
from django.core.mail import send_mail, EmailMultiAlternatives

# Plain text
send_mail("Subject", "Body", None, ["user@example.com"])

# HTML
msg = EmailMultiAlternatives("Subject", "Plain text", None, ["user@example.com"])
msg.attach_alternative("<p>HTML version</p>", "text/html")
msg.send()
```

`None` as the from address falls back to `DEFAULT_FROM_EMAIL`.
