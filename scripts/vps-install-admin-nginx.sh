#!/usr/bin/env bash
set -euo pipefail

SRC="/home/lucky/projects/apps/pvm-deal/admin.pvm-deal.nginx.conf"
DEST="/etc/nginx/sites-available/admin.pvm-deal.cz"

# Do not touch existing pvm-deal.cz site
sudo cp "$SRC" "$DEST"
sudo ln -sf "$DEST" /etc/nginx/sites-enabled/admin.pvm-deal.cz
sudo nginx -t
sudo systemctl reload nginx
echo "NGINX_ADMIN_HTTP_DONE"

# SSL only if DNS already points here; otherwise leave PENDING
if getent hosts admin.pvm-deal.cz | awk '{print $1}' | grep -q '89.221.214.140'; then
  echo "DNS_POINTS_HERE"
  # Do not run certbot automatically against shared certs without review.
  echo "SSL_ADMIN_PENDING_RUN_CERTBOT_SEPARATELY"
else
  echo "DNS_NOT_READY"
  echo "SSL_ADMIN_PENDING"
fi
