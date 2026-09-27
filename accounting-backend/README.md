# PVM-Deal Accounting Backend

Standalone FastAPI host for `accounting-api` from `Lakyn80/cz-accounting-module`.

## Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r accounting-backend\requirements.txt
copy accounting-backend\.env.example accounting-backend\.env
```

Generate an admin password hash:

```powershell
cd accounting-backend
python -m app.auth hash-password "your-admin-password"
```

Fill `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH`, `SECRET_KEY`, and host-specific accounting settings in `.env`.

Run locally:

```powershell
cd accounting-backend
uvicorn app.asgi:app --reload --host 127.0.0.1 --port 8000
```

The accounting router is mounted at `/api/accounting`.
