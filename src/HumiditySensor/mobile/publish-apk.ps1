# ============================================================
# publish-apk.ps1
# Compile l'application MAUI en APK Release et copie le
# livrable dans le dossier livrable/
# ============================================================
#
# Usage :
#   .\publish-apk.ps1              # Build Release par defaut
#   .\publish-apk.ps1 -Config Debug
#
# ============================================================

param(
    [ValidateSet("Debug", "Release")]
    [string]$Config = "Release"
)

$ErrorActionPreference = "Stop"

$scriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectDir  = Join-Path $scriptDir "HumiditySensorApp"
$csproj      = Join-Path $projectDir "HumiditySensorApp.csproj"
$livrableDir = Join-Path $scriptDir "livrable"
$framework   = "net10.0-android"

# --- Verification ---
if (-not (Test-Path $csproj)) {
    Write-Error "Projet introuvable : $csproj"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Build APK - Capteur Humidite" -ForegroundColor Cyan
Write-Host "  Configuration : $Config" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- Build ---
Write-Host "[1/3] Compilation en cours..." -ForegroundColor Yellow

dotnet publish $csproj `
    -f $framework `
    -c $Config

if ($LASTEXITCODE -ne 0) {
    Write-Error "La compilation a echoue."
    exit 1
}

Write-Host "[1/3] Compilation reussie." -ForegroundColor Green

# --- Recherche de l'APK ---
Write-Host "[2/3] Recherche de l'APK..." -ForegroundColor Yellow

$publishDir = Join-Path $projectDir "bin\$Config\$framework\publish"
$apk = Get-ChildItem -Path $publishDir -Filter "*.apk" -Recurse -ErrorAction SilentlyContinue |
       Sort-Object LastWriteTime -Descending |
       Select-Object -First 1

if (-not $apk) {
    # Fallback : chercher aussi dans bin/Config/framework directement
    $altDir = Join-Path $projectDir "bin\$Config\$framework"
    $apk = Get-ChildItem -Path $altDir -Filter "*.apk" -Recurse -ErrorAction SilentlyContinue |
           Sort-Object LastWriteTime -Descending |
           Select-Object -First 1
}

if (-not $apk) {
    Write-Error "Aucun fichier APK trouve dans $publishDir"
    exit 1
}

Write-Host "  APK trouve : $($apk.FullName)" -ForegroundColor Gray

# --- Copie vers livrable ---
Write-Host "[3/3] Copie vers livrable/..." -ForegroundColor Yellow

if (-not (Test-Path $livrableDir)) {
    New-Item -ItemType Directory -Path $livrableDir | Out-Null
}

$destName = "CapteurHumidite-$Config.apk"
$destPath = Join-Path $livrableDir $destName

Copy-Item -Path $apk.FullName -Destination $destPath -Force

Write-Host "[3/3] Copie terminee." -ForegroundColor Green

# --- Resume ---
$size = [math]::Round((Get-Item $destPath).Length / 1MB, 2)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  APK disponible :" -ForegroundColor Green
Write-Host "  $destPath" -ForegroundColor White
Write-Host "  Taille : $size Mo" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
