# Palety • Big-Bagy • Krabice Strejček — Fullstack (Flask + React + Tailwind)

This is the **fullstack project** powering [pvm-deal.cz](https://pvm-deal.cz).  
Backend is written in **Flask**, frontend in **React (Vite + Tailwind)**.  
Form submissions send emails to both client and site owner.  
reCAPTCHA verification is handled via Python’s `urllib` (no `requests` dependency).

---

## 🚀 Quick start (Windows PowerShell)

```powershell
# Clone and enter project
cd strejcek-web

# --- Backend setup ---
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

cd backend
copy .env.example .env
python run.py    # http://127.0.0.1:5000

# --- New terminal for frontend ---
cd ..\frontend
copy .env.example .env
npm install
npm run dev      # http://localhost:5173
