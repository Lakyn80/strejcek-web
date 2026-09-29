"""Standalone FastAPI host for the accounting module."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from accounting_api.database import (
    create_accounting_engine,
    create_accounting_session_factory,
    upgrade_database,
)
from accounting_api.fastapi import create_accounting_router
from accounting_api.ports.settings import CompanySettingsUnavailableError

from app.auth import (
    ACCOUNTING_UI_AUTH_HEADER,
    AdminPrincipalResponse,
    AdminTokenAuthenticationPort,
    LoginRequest,
    LoginResponse,
    authenticate_admin,
    create_access_token,
    pop_request_context,
    principal_response,
    push_request_context,
    require_admin_from_request,
)
from app.config import Settings, get_settings

EMPTY_INVOICE_SETTINGS_RESPONSE = {
    "owner_email": "",
    "issuer_name": "",
    "issuer_address": "",
    "issuer_city": "",
    "issuer_zip": "",
    "issuer_ico": "",
    "issuer_dic": "",
    "issuer_data_box": None,
    "issuer_email": None,
    "issuer_phone": None,
    "default_currency": "CZK",
    "default_due_days": 14,
    "default_note": None,
    "vat_enabled": False,
    "payment_method": "Převodem",
    "bank_account_number": "",
    "bank_account_prefix": None,
    "bank_code": "",
    "bank_iban": "",
    "account_label": "",
}


def create_app(settings: Settings | None = None, *, run_migrations: bool = True) -> FastAPI:
    host_settings = settings or get_settings()

    _ensure_sqlite_parent(host_settings.accounting_database_url)
    if run_migrations:
        upgrade_database(host_settings.accounting_database_url)

    engine = create_accounting_engine(host_settings.accounting_database_url)
    session_factory = create_accounting_session_factory(engine)
    _configure_integrations(host_settings)

    def get_db() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app = FastAPI(
        title="PVM-Deal Accounting API",
        description="Strejcek standalone accounting backend backed by cz-accounting-module.",
        version="0.1.0",
    )
    app.state.accounting_engine = engine
    app.state.settings = host_settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=host_settings.parsed_admin_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", ACCOUNTING_UI_AUTH_HEADER],
        expose_headers=["Content-Type"],
    )

    @app.middleware("http")
    async def attach_request_context(request, call_next):
        token = push_request_context(request)
        try:
            return await call_next(request)
        finally:
            pop_request_context(token)

    @app.exception_handler(CompanySettingsUnavailableError)
    async def company_settings_unavailable_handler(
        request: Request,
        exc: CompanySettingsUnavailableError,
    ) -> JSONResponse:
        # Fresh DB: Settings UI must load empty form instead of opaque 500.
        if request.method == "GET" and request.url.path.rstrip("/").endswith("/settings"):
            return JSONResponse(status_code=200, content=EMPTY_INVOICE_SETTINGS_RESPONSE)
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "service": "pvm-accounting-api",
            "api_prefix": host_settings.accounting_api_prefix,
            "auth_configured": host_settings.auth_configured(),
        }

    @app.post("/api/admin/login", response_model=LoginResponse)
    def login(payload: LoginRequest) -> LoginResponse:
        principal = authenticate_admin(host_settings, payload.username, payload.password)
        return create_access_token(host_settings, principal)

    @app.get("/api/admin/me", response_model=AdminPrincipalResponse)
    def me() -> AdminPrincipalResponse:
        principal = require_admin_from_request(host_settings)
        return principal_response(principal, host_settings)

    @app.post("/api/admin/logout")
    def logout(_: AdminPrincipalResponse = Depends(me)) -> dict[str, bool]:
        return {"ok": True}

    app.include_router(
        create_accounting_router(
            get_db=get_db,
            auth_port=AdminTokenAuthenticationPort(host_settings),
        ),
        prefix=host_settings.accounting_api_prefix,
    )

    return app


def _configure_integrations(settings: Settings) -> None:
    from accounting_api.adapters.email.console import ConsoleEmailAdapter
    from accounting_api.adapters.email.smtp import SmtpEmailAdapter
    from accounting_api.integrations.ares.provider import MockAresProvider, configure_ares_provider
    from accounting_api.integrations.email import configure_email_port
    from accounting_api.integrations.pdf import configure_pdf_generator
    from accounting_api.integrations.storage import set_storage_root

    from app.pdf_invoice import InvoicePdfBranding, ReportLabInvoicePdfGenerator

    storage_root = settings.ensure_storage_directory()
    set_storage_root(storage_root)

    if settings.accounting_email_provider == "console":
        configure_email_port(ConsoleEmailAdapter(from_address=settings.accounting_email_from))
    elif settings.accounting_email_provider == "smtp":
        configure_email_port(
            SmtpEmailAdapter(
                host=settings.accounting_smtp_host,
                port=settings.accounting_smtp_port,
                username=settings.accounting_smtp_user,
                password=settings.accounting_smtp_password,
                from_address=settings.accounting_email_from,
                use_tls=settings.accounting_smtp_use_tls,
            )
        )
    elif settings.accounting_email_provider == "resend":
        from app.email_resend import ResendEmailAdapter

        configure_email_port(
            ResendEmailAdapter(
                api_key=settings.resend_api_key,
                from_email=settings.resend_from_email,
                from_name=settings.resend_from_name,
                always_bcc=(settings.accounting_invoice_copy_email,),
            )
        )
    else:
        configure_email_port(None)

    if settings.accounting_ares_provider == "mock":
        configure_ares_provider(MockAresProvider())
    elif settings.accounting_ares_provider == "real":
        from app.ares_real import RealAresProvider

        configure_ares_provider(RealAresProvider())

    logo_path = settings.accounting_logo_path.expanduser()
    configure_pdf_generator(
        ReportLabInvoicePdfGenerator(
            branding=InvoicePdfBranding(
                issuer_email=(
                    settings.resend_from_email.strip()
                    or settings.accounting_email_from.strip()
                    or settings.admin_email.strip()
                ),
                issuer_phone=settings.accounting_issuer_phone_fallback.strip(),
                issuer_bic=settings.accounting_issuer_bic.strip(),
                issuer_website=settings.accounting_issuer_website.strip(),
                logo_path=logo_path if logo_path.is_file() else None,
            ),
            storage_root=storage_root,
            persist=True,
        )
    )


def _ensure_sqlite_parent(database_url: str) -> None:
    url = make_url(database_url)
    if url.drivername.startswith("sqlite") and url.database and url.database != ":memory:":
        Path(url.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
