"""Admin authentication adapter for accounting-api."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import secrets
import time
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel
from starlette.requests import Request

from accounting_api.ports.auth import (
    ACCOUNTING_ADMIN_PERMISSION,
    AccountingPrincipal,
    AuthenticationPort,
    AuthenticationRequiredError,
)

from app.config import Settings

ACCOUNTING_UI_AUTH_HEADER = "X-Accounting-Demo-Token"
PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 600_000

_request_context: ContextVar[Request | None] = ContextVar("_request_context", default=None)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: int
    username: str
    display_name: str
    email: str | None = None


class AdminPrincipalResponse(BaseModel):
    username: str
    display_name: str
    email: str | None = None
    permissions: list[str]


@dataclass(frozen=True)
class TokenPayload:
    subject: str
    username: str
    email: str | None
    display_name: str
    expires_at: int


def push_request_context(request: Request) -> object:
    return _request_context.set(request)


def pop_request_context(token: object) -> None:
    _request_context.reset(token)


def hash_password(password: str, *, salt: str | None = None, iterations: int = PASSWORD_HASH_ITERATIONS) -> str:
    if not password:
        raise ValueError("password must not be empty")
    selected_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), selected_salt.encode("utf-8"), iterations)
    encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"{PASSWORD_HASH_ALGORITHM}${iterations}${selected_salt}${encoded}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_raw, salt, expected = password_hash.split("$", 3)
        if algorithm != PASSWORD_HASH_ALGORITHM:
            return False
        candidate = hash_password(password, salt=salt, iterations=int(iterations_raw)).split("$", 3)[3]
        return hmac.compare_digest(candidate, expected)
    except Exception:
        return False


def authenticate_admin(settings: Settings, username: str, password: str) -> AccountingPrincipal:
    if not settings.auth_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication is not configured.",
        )
    if not hmac.compare_digest(username.strip(), settings.admin_username.strip()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    if not verify_password(password, settings.admin_password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    return build_admin_principal(settings)


def build_admin_principal(settings: Settings) -> AccountingPrincipal:
    username = settings.admin_username.strip()
    return AccountingPrincipal(
        subject_id=f"strejcek-admin:{username}",
        email=settings.admin_email.strip() or None,
        display_name=settings.admin_display_name.strip() or username,
        permissions=frozenset({ACCOUNTING_ADMIN_PERMISSION}),
    )


def create_access_token(settings: Settings, principal: AccountingPrincipal) -> LoginResponse:
    now = int(time.time())
    expires_at = now + settings.admin_token_ttl_seconds
    payload = {
        "sub": principal.subject_id,
        "username": settings.admin_username.strip(),
        "email": principal.email,
        "display_name": principal.display_name or settings.admin_username.strip(),
        "permissions": sorted(principal.permissions),
        "iat": now,
        "exp": expires_at,
    }
    payload_segment = _urlsafe_json(payload)
    signature = _sign(settings, payload_segment)
    return LoginResponse(
        access_token=f"{payload_segment}.{signature}",
        expires_at=expires_at,
        username=settings.admin_username.strip(),
        display_name=principal.display_name or settings.admin_username.strip(),
        email=principal.email,
    )


def principal_response(principal: AccountingPrincipal, settings: Settings) -> AdminPrincipalResponse:
    return AdminPrincipalResponse(
        username=settings.admin_username.strip(),
        display_name=principal.display_name or settings.admin_username.strip(),
        email=principal.email,
        permissions=sorted(principal.permissions),
    )


def require_admin_from_request(settings: Settings) -> AccountingPrincipal:
    token = _extract_token(_request_context.get())
    payload = _decode_token(settings, token)
    if payload.username != settings.admin_username.strip():
        raise AuthenticationRequiredError("Token principal is not configured admin.")
    return AccountingPrincipal(
        subject_id=payload.subject,
        email=payload.email,
        display_name=payload.display_name,
        permissions=frozenset({ACCOUNTING_ADMIN_PERMISSION}),
    )


class AdminTokenAuthenticationPort(AuthenticationPort):
    """Accounting package auth adapter backed by Strejcek admin tokens."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def get_current_principal(self) -> AccountingPrincipal:
        return require_admin_from_request(self._settings)


def _extract_token(request: Request | None) -> str:
    if request is None:
        raise AuthenticationRequiredError("Request context is unavailable.")

    authorization = request.headers.get("Authorization", "")
    if authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()

    accounting_ui_token = request.headers.get(ACCOUNTING_UI_AUTH_HEADER, "").strip()
    if accounting_ui_token:
        return accounting_ui_token

    raise AuthenticationRequiredError("Missing admin token.")


def _decode_token(settings: Settings, token: str) -> TokenPayload:
    if not settings.secret_key:
        raise AuthenticationRequiredError("Token verification is not configured.")
    try:
        payload_segment, signature = token.split(".", 1)
    except ValueError as exc:
        raise AuthenticationRequiredError("Invalid token format.") from exc

    expected_signature = _sign(settings, payload_segment)
    if not hmac.compare_digest(signature, expected_signature):
        raise AuthenticationRequiredError("Invalid token signature.")

    try:
        payload = json.loads(_urlsafe_decode(payload_segment))
        expires_at = int(payload["exp"])
    except Exception as exc:
        raise AuthenticationRequiredError("Invalid token payload.") from exc

    if expires_at <= int(time.time()):
        raise AuthenticationRequiredError("Admin token expired.")

    return TokenPayload(
        subject=str(payload["sub"]),
        username=str(payload["username"]),
        email=payload.get("email") or None,
        display_name=str(payload.get("display_name") or payload["username"]),
        expires_at=expires_at,
    )


def _sign(settings: Settings, payload_segment: str) -> str:
    digest = hmac.new(settings.secret_key.encode("utf-8"), payload_segment.encode("ascii"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _urlsafe_json(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _urlsafe_decode(value: str) -> str:
    padded = value + ("=" * (-len(value) % 4))
    return base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")


def _main() -> None:
    parser = argparse.ArgumentParser(description="Accounting admin auth utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    hash_parser = subparsers.add_parser("hash-password", help="Generate ADMIN_PASSWORD_HASH.")
    hash_parser.add_argument("password")
    args = parser.parse_args()

    if args.command == "hash-password":
        print(hash_password(args.password))


if __name__ == "__main__":
    _main()
