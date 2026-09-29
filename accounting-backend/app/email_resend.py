"""Resend email adapter implementing accounting EmailPort."""

from __future__ import annotations

import base64
import logging
import re
from typing import Any

from accounting_api.ports.email import (
    EmailConfigurationError,
    EmailDeliveryError,
    OutboundEmail,
)

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ResendEmailAdapter:
    """Deliver outbound accounting emails through the Resend HTTP API."""

    def __init__(
        self,
        *,
        api_key: str,
        from_email: str,
        from_name: str = "PVM Deal",
        always_bcc: tuple[str, ...] = (),
    ) -> None:
        self._api_key = (api_key or "").strip()
        self._from_email = (from_email or "").strip()
        self._from_name = (from_name or "").strip() or "PVM Deal"
        self._always_bcc = tuple(
            address.strip().lower()
            for address in always_bcc
            if address and address.strip() and _is_valid_email(address.strip())
        )
        self.last_message_id: str | None = None

    def is_configured(self) -> bool:
        return bool(self._api_key and self._from_email and _is_valid_email(self._from_email))

    def formatted_from(self) -> str:
        if self._from_name:
            return f"{self._from_name} <{self._from_email}>"
        return self._from_email

    def send(self, message: OutboundEmail) -> None:
        if not self._api_key:
            raise EmailConfigurationError("RESEND_API_KEY is not configured.")
        if not self._from_email:
            raise EmailConfigurationError("RESEND_FROM_EMAIL is not configured.")
        if not _is_valid_email(self._from_email):
            raise EmailConfigurationError("RESEND_FROM_EMAIL is not a valid email address.")
        if self._from_email.lower().endswith("@resend.dev"):
            raise EmailConfigurationError("Production Resend sender must not use resend.dev addresses.")

        recipients = [_require_recipient(item.address) for item in message.recipients]
        recipient_set = {item.lower() for item in recipients}
        bcc = [_require_recipient(item.address) for item in message.bcc]
        for forced in self._always_bcc:
            if forced not in recipient_set and forced not in {item.lower() for item in bcc}:
                bcc.append(forced)
        cc = [_require_recipient(item.address) for item in message.cc]

        payload: dict[str, Any] = {
            "from": self.formatted_from(),
            "to": recipients,
            "subject": message.subject,
            "html": message.html_body,
        }
        if message.text_body:
            payload["text"] = message.text_body
        if cc:
            payload["cc"] = cc
        if bcc:
            payload["bcc"] = bcc
        if message.reply_to is not None:
            payload["reply_to"] = _require_recipient(message.reply_to.address)
        if message.attachments:
            payload["attachments"] = [
                {
                    "filename": attachment.filename,
                    "content": base64.b64encode(attachment.content).decode("ascii"),
                    "content_type": attachment.content_type,
                }
                for attachment in message.attachments
            ]

        try:
            import resend
        except ImportError as exc:  # pragma: no cover - dependency wiring
            raise EmailConfigurationError("Python package 'resend' is not installed.") from exc

        resend.api_key = self._api_key
        try:
            response = resend.Emails.send(payload)
        except Exception as exc:  # noqa: BLE001 - Resend SDK raises varied errors
            logger.exception(
                "Resend email delivery failed to=%s subject=%r",
                ",".join(recipients),
                message.subject,
            )
            raise EmailDeliveryError(f"Resend API request failed: {exc}") from exc

        message_id = _extract_message_id(response)
        if not message_id:
            raise EmailDeliveryError("Resend API did not return an email message id.")
        self.last_message_id = message_id
        logger.info(
            "Resend email accepted id=%s to=%s bcc=%s subject=%r attachments=%d",
            message_id,
            ",".join(recipients),
            ",".join(bcc),
            message.subject,
            len(message.attachments),
        )


def _require_recipient(address: str) -> str:
    cleaned = (address or "").strip()
    if not cleaned or not _is_valid_email(cleaned):
        raise EmailDeliveryError("Recipient email address is invalid.")
    return cleaned


def _is_valid_email(address: str) -> bool:
    return bool(_EMAIL_RE.match(address.strip()))


def _extract_message_id(response: Any) -> str | None:
    if response is None:
        return None
    if isinstance(response, dict):
        value = response.get("id")
        return str(value).strip() if value else None
    value = getattr(response, "id", None)
    return str(value).strip() if value else None
