import httpx


class FreesendError(Exception):
    """Raised when the Freesend API returns an error."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Freesend API error {status_code}: {message}")


class Freesend:
    """
    Minimal Freesend API client.

    Usage::

        from freesend import Freesend

        fs = Freesend("sk_live_...")
        fs.send(
            from_="hello@yourdomain.com",
            to="user@example.com",
            subject="Hello",
            html="<p>Hello!</p>",
            text="Hello!",
        )
    """

    def __init__(self, api_key: str, base_url: str = "https://freesend.keybee.app"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )

    def send(
        self,
        *,
        from_: str,
        to: str | list[str],
        subject: str,
        html: str | None = None,
        text: str | None = None,
    ) -> dict:
        """
        Send an email.

        :param from_: Sender address (must be from a verified domain).
        :param to: Recipient address or list of addresses.
        :param subject: Email subject.
        :param html: HTML body (optional if text is provided).
        :param text: Plain text body (optional if html is provided).
        :returns: Dict with ``message_id`` and ``status``.
        :raises FreesendError: If the API returns a non-2xx response.
        """
        if not html and not text:
            raise ValueError("At least one of html or text must be provided.")

        payload: dict = {
            "from": from_,
            "to": ", ".join(to) if isinstance(to, list) else to,
            "subject": subject,
        }
        if html:
            payload["html"] = html
        if text:
            payload["text"] = text

        r = self._client.post(f"{self.base_url}/v1/send", json=payload)
        if not r.is_success:
            try:
                detail = r.json().get("error", r.text)
            except Exception:
                detail = r.text
            raise FreesendError(r.status_code, detail)

        return r.json()

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
