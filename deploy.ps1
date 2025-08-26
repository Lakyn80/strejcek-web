# === Deploy frontend na server ===

# Nastavení
$PROJECT    = "C:\Users\lukas\Desktop\PYTHON_PROJECTS_DESKTOP\PYTHON_POJECTS\strejcek-web\frontend"
$REMOTE     = "lucky@89.221.214.140"
$REMOTE_DIR = "/home/lucky/projects/strejcek-web"

# 1) Build frontend
Write-Host "=== Spouštím build (npm run build) ==="
cd $PROJECT
npm run build

if (-not (Test-Path "$PROJECT\dist")) {
    Write-Error "❌ Build selhal – složka dist neexistuje!"
    exit 1
}

# 2) Upload dist/ na server (přepíše starý obsah)
Write-Host "=== Nahrávám dist/ na server ==="
scp -r "$PROJECT/dist" "$REMOTE:$REMOTE_DIR/"

# 3) Oprava práv na serveru
Write-Host "=== Spouštím fix-dist.sh na serveru ==="
ssh $REMOTE "~/fix-dist.sh"

Write-Host "`n✅ Hotovo: nasazeno na https://pvm-deal.cz"
