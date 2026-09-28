from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect

from app.auth import ACCOUNTING_UI_AUTH_HEADER, hash_password
from app.config import Settings
from app.main import create_app


def build_settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        accounting_database_url=f"sqlite:///{tmp_path / 'accounting.db'}",
        accounting_storage_path=tmp_path / "storage",
        accounting_email_from="accounting@example.test",
        admin_username="admin",
        admin_password_hash=hash_password("correct-password", salt="testsalt", iterations=1_000),
        admin_display_name="Test Admin",
        admin_email="admin@example.test",
        secret_key="test-secret-key",
        admin_allowed_origins="http://localhost:5174",
    )


def test_health_and_database_initialization(tmp_path: Path) -> None:
    settings = build_settings(tmp_path)
    app = create_app(settings)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    table_names = inspect(create_engine(settings.accounting_database_url)).get_table_names()
    assert "invoice_settings" in table_names
    assert "invoices" in table_names


def test_accounting_router_requires_authentication(tmp_path: Path) -> None:
    app = create_app(build_settings(tmp_path))
    client = TestClient(app)

    response = client.get("/api/accounting")

    assert response.status_code == 401
    assert response.json()["detail"] == "Přihlaste se do adminu"


def test_login_and_authenticated_accounting_access(tmp_path: Path) -> None:
    app = create_app(build_settings(tmp_path))
    client = TestClient(app)

    bad_login = client.post("/api/admin/login", json={"username": "admin", "password": "wrong"})
    assert bad_login.status_code == 401

    login = client.post(
        "/api/admin/login",
        json={"username": "admin", "password": "correct-password"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/admin/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "admin"

    accounting = client.get("/api/accounting", headers={ACCOUNTING_UI_AUTH_HEADER: token})
    assert accounting.status_code == 200
    assert accounting.json() == []

    logout = client.post("/api/admin/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout.status_code == 200
    assert logout.json() == {"ok": True}


def test_settings_get_returns_empty_defaults_when_unconfigured(tmp_path: Path) -> None:
    app = create_app(build_settings(tmp_path))
    client = TestClient(app)

    login = client.post(
        "/api/admin/login",
        json={"username": "admin", "password": "correct-password"},
    )
    token = login.json()["access_token"]

    response = client.get(
        "/api/accounting/settings",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["issuer_ico"] == ""
    assert payload["default_currency"] == "CZK"
    assert payload["payment_method"] == "Převodem"
