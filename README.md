# Palety • Big-Bagy • Krabice Strejček — Fullstack (Flask + React + Tailwind)

Čistý projekt. reCAPTCHA řešena přes `urllib` (žádný `requests`).
Doporučený postup (Windows PowerShell):

```powershell
cd strejcek-web
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

cd backend
copy .env.example .env
python run.py    # http://127.0.0.1:5000

# Nové okno
cd ..\frontend
copy .env.example .env
npm i
npm run dev      # http://localhost:5173
```
