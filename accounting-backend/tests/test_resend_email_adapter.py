from __future__ import annotations

from pathlib import Path

import pytest

from accounting_api.ports.email import (
    EmailAddress,
    EmailAttachment,
    EmailConfigurationError,
    EmailDeliveryError,
    OutboundEmail,
)

from app.email_resend import ResendEmailAdapter


def _message(*, to: str = "customer@example.com") -> OutboundEmail:
    return OutboundEmail(
        recipients=(EmailAddress(to),),
        subject="Faktura 001 – Test",
        html_body="<p>Test</p>",
        attachments=(
            EmailAttachment(filename="invoice-001.pdf", content_type="application/pdf", content=b"%PDF-1.4"),
        ),
    )


def test_resend_requires_api_key() -> None:
    adapter = ResendEmailAdapter(api_key="", from_email="faktury@pvm-deal.cz", from_name="PVM Deal")
    assert adapter.is_configured() is False
    with pytest.raises(EmailConfigurationError, match="RESEND_API_KEY"):
        adapter.send(_message())


def test_resend_requires_from_email() -> None:
    adapter = ResendEmailAdapter(api_key="re_test", from_email="", from_name="PVM Deal")
    assert adapter.is_configured() is False
    with pytest.raises(EmailConfigurationError, match="RESEND_FROM_EMAIL"):
        adapter.send(_message())


def test_resend_rejects_resend_dev_from() -> None:
    adapter = ResendEmailAdapter(
        api_key="re_test",
        from_email="onboarding@resend.dev",
        from_name="PVM Deal",
    )
    with pytest.raises(EmailConfigurationError, match="resend.dev"):
        adapter.send(_message())


def test_resend_rejects_invalid_recipient(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = ResendEmailAdapter(
        api_key="re_test",
        from_email="faktury@pvm-deal.cz",
        from_name="PVM Deal",
    )

    def _should_not_call(*_args, **_kwargs):
        raise AssertionError("Resend SDK must not be called for invalid recipient")

    monkeypatch.setattr("resend.Emails.send", _should_not_call, raising=False)
    with pytest.raises(EmailDeliveryError, match="invalid"):
        adapter.send(_message(to="not-an-email"))


def test_resend_send_success_sets_message_id(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeEmails:
        @staticmethod
        def send(payload):
            captured["payload"] = payload
            return {"id": "re_msg_123"}

    import resend as resend_mod

    monkeypatch.setattr(resend_mod, "Emails", FakeEmails)

    adapter = ResendEmailAdapter(
        api_key="re_test_key",
        from_email="faktury@pvm-deal.cz",
        from_name="PVM Deal",
        always_bcc=("robin.strejcek@centrum.cz",),
    )
    adapter.send(_message(to="lukas.krumpach@gmail.com"))

    assert adapter.last_message_id == "re_msg_123"
    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert payload["from"] == "PVM Deal <faktury@pvm-deal.cz>"
    assert payload["to"] == ["lukas.krumpach@gmail.com"]
    assert payload["bcc"] == ["robin.strejcek@centrum.cz"]
    assert payload["subject"].startswith("Faktura")
    assert payload["attachments"][0]["filename"] == "invoice-001.pdf"
    assert "re_test_key" not in str(payload)


def test_resend_always_bcc_skips_when_recipient_is_copy(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeEmails:
        @staticmethod
        def send(payload):
            captured["payload"] = payload
            return {"id": "re_msg_456"}

    import resend as resend_mod

    monkeypatch.setattr(resend_mod, "Emails", FakeEmails)
    adapter = ResendEmailAdapter(
        api_key="re_test_key",
        from_email="faktury@pvm-deal.cz",
        from_name="PVM Deal",
        always_bcc=("robin.strejcek@centrum.cz",),
    )
    adapter.send(_message(to="robin.strejcek@centrum.cz"))
    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert "bcc" not in payload


def test_resend_api_failure_is_wrapped(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeEmails:
        @staticmethod
        def send(_payload):
            raise RuntimeError("boom")

    import resend as resend_mod

    monkeypatch.setattr(resend_mod, "Emails", FakeEmails)
    adapter = ResendEmailAdapter(
        api_key="re_test_key",
        from_email="faktury@pvm-deal.cz",
        from_name="PVM Deal",
    )
    with pytest.raises(EmailDeliveryError, match="Resend API request failed"):
        adapter.send(_message())
