"""One-shot Resend smoke: send invoice-style email with forced BCC copy."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

# Ensure host + accounting-api imports resolve.
sys.path.insert(0, str(ROOT / "accounting-backend"))
sys.path.insert(
    0,
    str(ROOT / "admin" / ".accounting-ui" / "cz-accounting-module" / "packages" / "accounting-api" / "src"),
)

from accounting_api.ports.email import EmailAddress, EmailAttachment, OutboundEmail
from app.email_resend import ResendEmailAdapter


def main() -> int:
    api_key = os.getenv("RESEND_API_KEY", "").strip()
    from_email = os.getenv("RESEND_FROM_EMAIL", "").strip()
    from_name = os.getenv("RESEND_FROM_NAME", "PVM Deal").strip()
    copy_email = os.getenv("ACCOUNTING_INVOICE_COPY_EMAIL", "robin.strejcek@centrum.cz").strip()
    to_email = os.getenv("RESEND_SMOKE_TO", "lukas.krumpach@gmail.com").strip()

    if not api_key:
        print("SMOKE_FAIL missing RESEND_API_KEY")
        return 1
    if not from_email:
        print("SMOKE_FAIL missing RESEND_FROM_EMAIL")
        return 1

    adapter = ResendEmailAdapter(
        api_key=api_key,
        from_email=from_email,
        from_name=from_name,
        always_bcc=(copy_email,),
    )
    adapter.send(
        OutboundEmail(
            recipients=(EmailAddress(to_email),),
            subject="PVM Deal – smoke test faktury (Resend)",
            html_body=(
                "<p>Dobrý den,</p>"
                "<p>toto je produkční smoke test odesílání faktury přes Resend.</p>"
                f"<p>Příjemce: {to_email}</p>"
                f"<p>Kopie (BCC): {copy_email}</p>"
                f"<p>Odesílatel: {from_name} &lt;{from_email}&gt;</p>"
            ),
            attachments=(
                EmailAttachment(
                    filename="smoke-invoice.pdf",
                    content_type="application/pdf",
                    content=b"%PDF-1.4\n%smoke\n",
                ),
            ),
        )
    )
    print(f"SMOKE_PASS message_id={adapter.last_message_id} to={to_email} bcc={copy_email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
