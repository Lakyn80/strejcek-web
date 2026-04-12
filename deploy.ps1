# =====================================================

# deploy.ps1 – build → push Docker Hub → restart VPS

# Spuštění: .\deploy.ps1

# =====================================================

$ErrorActionPreference = "Stop"

$DOCKER_USER  = "lakyn80"
$BACKEND_IMG  = "$DOCKER_USER/pvm-deal-backend:latest"
$FRONTEND_IMG = "$DOCKER_USER/pvm-deal-frontend:latest"
$REMOTE       = "lucky@89.221.214.140"
$REMOTE_DIR   = "/home/lucky/projects/apps/pvm-deal"

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n=== 1/6  Docker login ==="
docker login

Write-Host "`n=== 2/6  Build backend ==="
docker build -t $BACKEND_IMG "$ROOT\backend"

Write-Host "`n=== 3/6  Build frontend ==="
docker build -t $FRONTEND_IMG "$ROOT\frontend"

Write-Host "`n=== 4/6  Push na Docker Hub ==="
docker push $BACKEND_IMG
docker push $FRONTEND_IMG

Write-Host "`n=== 5/6  Nahrání konfigurace na VPS ==="
scp "$ROOT\docker-compose.yml"  "${REMOTE}:${REMOTE_DIR}/docker-compose.yml"
scp "$ROOT\pvm-deal.nginx.conf" "${REMOTE}:/tmp/pvm-deal.nginx.conf"

Write-Host "`n=== 6/6  Deploy na VPS ==="
ssh $REMOTE @"
set -e
cd $REMOTE_DIR

# ✅ SPRÁVNÁ kontrola ENV

if [ ! -f backend/.env ]; then
echo '❌ Chybí backend/.env na serveru!'
exit 1
fi

# Nginx config

sudo cp /tmp/pvm-deal.nginx.conf /etc/nginx/sites-available/pvm-deal.cz
sudo ln -sf /etc/nginx/sites-available/pvm-deal.cz /etc/nginx/sites-enabled/pvm-deal.cz
sudo nginx -t && sudo systemctl reload nginx

# Docker deploy

docker compose pull
docker compose up -d --remove-orphans
docker image prune -f

echo '✅ Nasazeno!'
"@

Write-Host "`n✅ Hotovo – http://pvm-deal.cz"
