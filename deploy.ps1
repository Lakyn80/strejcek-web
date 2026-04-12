# =====================================================
# deploy.ps1 – build → push Docker Hub → restart VPS
# Spuštění: .\deploy.ps1
# =====================================================

$ErrorActionPreference = "Stop"

$DOCKER_USER  = "lakyn80"
$TAG          = (Get-Date -Format "yyyyMMdd-HHmmss")
$BACKEND_IMG  = "$DOCKER_USER/pvm-deal-backend:$TAG"
$FRONTEND_IMG = "$DOCKER_USER/pvm-deal-frontend:$TAG"
$REMOTE       = "lucky@89.221.214.140"
$REMOTE_DIR   = "/home/lucky/projects/apps/pvm-deal"

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n=== TAG: $TAG ==="

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

# Vygeneruj docker-compose s konkrétním tagem
$composeContent = @"
services:
  backend:
    image: $BACKEND_IMG
    restart: always
    env_file:
      - ./backend/.env
    ports:
      - "127.0.0.1:8070:5000"
    networks:
      - pvm

  frontend:
    image: $FRONTEND_IMG
    restart: always
    ports:
      - "127.0.0.1:8095:80"
    depends_on:
      - backend
    networks:
      - pvm

networks:
  pvm:
    driver: bridge
"@

$tmpCompose = "$ROOT\docker-compose.deploy.yml"
$composeContent | Out-File -FilePath $tmpCompose -Encoding utf8 -NoNewline

scp $tmpCompose         "${REMOTE}:${REMOTE_DIR}/docker-compose.yml"
scp "$ROOT\pvm-deal.nginx.conf" "${REMOTE}:/tmp/pvm-deal.nginx.conf"

Remove-Item $tmpCompose -Force

Write-Host "`n=== 6/6  Deploy na VPS ==="
ssh $REMOTE @"
set -e
cd $REMOTE_DIR

if [ ! -f backend/.env ]; then
  echo 'Chybi backend/.env na serveru!'
  exit 1
fi

sudo cp /tmp/pvm-deal.nginx.conf /etc/nginx/sites-available/pvm-deal.cz
sudo ln -sf /etc/nginx/sites-available/pvm-deal.cz /etc/nginx/sites-enabled/pvm-deal.cz
sudo nginx -t && sudo systemctl reload nginx

docker compose pull
docker compose up -d --remove-orphans
docker image prune -f

echo 'Nasazeno: $TAG'
"@

Write-Host "`n Hotovo – https://pvm-deal.cz (tag: $TAG)"
