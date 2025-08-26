# deploy-strejcek-web.ps1
param(
  [string]$Server = "89.221.214.140",
  [string]$User = "lucky",
  [string]$RemoteBase = "/home/lucky/projects",
  [string]$AppName = "strejcek-web"
)

$ErrorActionPreference = "Stop"

# 1) Najdi frontend (spoustej ve slozce, kde je package.json)
if (-not (Test-Path "package.json")) {
  if (Test-Path "frontend/package.json") {
    Set-Location "frontend"
  } else {
    throw "Nenalezen package.json ani frontend/package.json"
  }
}

# 2) Co posilat (jen zdrojaky a konfigy)
$candidates = @(
  "package.json","package-lock.json","pnpm-lock.yaml","yarn.lock",
  "vite.config.ts","vite.config.js",
  "tailwind.config.ts","tailwind.config.js",
  "postcss.config.js","tsconfig.json",
  "index.html","src","public"
)
$include = @()
foreach ($p in $candidates) { if (Test-Path $p) { $include += $p } }
if ($include.Count -eq 0) { throw "Neni co posilat - chybi src/public/configy." }

# 3) Zabal vybrane polozky
$archive = Join-Path $PWD "src-upload.tgz"
if (Test-Path $archive) { Remove-Item $archive -Force }
& tar -czf $archive -- $include

# 4) Cesty na serveru
$remoteProj = "$RemoteBase/$AppName"
$remoteTar  = "$RemoteBase/src-upload.tgz"

# 5) Upload archivu
& scp $archive ("{0}@{1}:{2}" -f $User,$Server,$remoteTar)

# 6) Build na serveru
$bash = @"
set -e
mkdir -p '$remoteProj'
rm -rf '$remoteProj'/*
tar -xzf '$remoteTar' -C '$remoteProj'
rm -f '$remoteTar'
cd '$remoteProj'

if command -v pnpm >/dev/null 2>&1 && [ -f pnpm-lock.yaml ]; then
  pnpm install --frozen-lockfile && pnpm build
else
  if command -v yarn >/dev/null 2>&1 && [ -f yarn.lock ]; then
    yarn install --frozen-lockfile && yarn build
  else
    npm ci && npm run build
  fi
fi
"@


# 7) Uklid
Remove-Item $archive -Force
Write-Host "`n✅ Hotovo. Build je na serveru v $remoteProj/dist"
