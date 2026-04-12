# Palety • Big-Bagy • Krabice Strejček — Full-Stack Platform (Flask + React + Tailwind)

This repository contains the production codebase behind **[pvm-deal.cz](https://pvm-deal.cz)**.
It is a modern full-stack application built with a **Flask** backend and a **React (Vite + Tailwind)** frontend.
The platform handles lead intake, validates submissions (incl. reCAPTCHA), and routes notifications to both the site owner and the client.

---

## Architecture Overview

+---------------------------+ +---------------------------+
| Frontend | | Backend |
| React (Vite + Tailwind) | HTTPS | Flask API + App services |
| - Public pages +----------->+ - REST endpoints |
| - Forms (reCAPTCHA) | | - Validation & routing |
| - Client-side routing | | - Email notifications |
+-------------+-------------+ +-------------+-------------+
^ |
| v
| +--------------------+
| | Persistence |
| | (SQLite in dev; |
| | external DB in |
| | production) |
| +--------------------+
|
| Static assets (built)
+-----------------------> CDN / Web server 


**Key principles**
- Clear separation of concerns between **UI** and **API**.
- No application secrets or local databases are committed to source control.
- Environment-specific configuration is injected via `.env` files (ignored by Git).

---

## Key Features

- **Mobile-first UI** with Tailwind and Vite dev experience.
- **Secure lead forms** with server-side verification (reCAPTCHA).
- **Email notifications** for both requester and site owner.
- **Strict repository hygiene**: `.env`, databases, uploads, caches and build artefacts are excluded.

---

## Technology Stack

- **Frontend:** React, Vite, Tailwind CSS
- **Backend:** Python, Flask
- **Validation & Security:** reCAPTCHA verification (server-side), input sanitation
- **Emailing:** SMTP (configurable via environment variables)
- **Data:** SQLite for local development; external/managed DB recommended in production

---

## Getting Started (Windows PowerShell)

```powershell
# Clone and enter project root
git clone <YOUR_SSH_URL_OR_HTTPS>
cd strejcek-web   # or the folder name you cloned into

# --- Backend setup ---
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

# Configure environment
copy backend\.env.example backend\.env
# (fill in SMTP, RECAPTCHA keys, DB connection as needed)

# Run backend
cd backend
python run.py         # http://127.0.0.1:5000

# --- New terminal for the frontend ---
cd ..\frontend
copy .env.example .env
npm install
npm run dev           # http://localhost:5173

Configuration

Backend (backend/.env):

FLASK_ENV=development|production

SECRET_KEY=<random-string>

RECAPTCHA_SECRET=<server-key>

SMTP_HOST=…, SMTP_PORT=…, SMTP_USER=…, SMTP_PASS=…

DATABASE_URL=sqlite:///instance/database.db (dev) or production DSN

Frontend (frontend/.env):

VITE_API_BASE_URL=https://api.example.com

VITE_RECAPTCHA_SITE_KEY=<site-key>

Security note: .env* files are intentionally ignored and must never be committed.

Repository Hygiene & Security

This repository is configured to avoid committing the following:

Secrets: .env, .env.*, keys/certificates

Local databases and dumps: *.db, *.sqlite*, *.sql.gz, *.sqlite.gz

Generated/large folders: uploads/, static/invoices/, node_modules/, dist/, .vite/, .cache/

Test/IDE artefacts: __pycache__/, .pytest_cache/, .vscode/, .idea/