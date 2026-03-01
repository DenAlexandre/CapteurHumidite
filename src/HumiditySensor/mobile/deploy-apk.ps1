# ============================================================
# deploy-apk.ps1
# Copie l'APK depuis livrable/ vers le dossier
# Telechargements du telephone connecte en USB via ADB.
# ============================================================
#
# Prerequis :
#   - ADB installe (Android SDK Platform-Tools)
#   - Telephone connecte en USB avec debogage USB active
#
# Usage :
#   .\deploy-apk.ps1                # APK Release par defaut
#   .\deploy-apk.ps1 -Config Debug
#
# ============================================================

param(
    [ValidateSet("Debug", "Release")]
    [string]$Config = "Release"
)

$ErrorActionPreference = "Stop"

$scriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$livrableDir = Join-Path $scriptDir "livrable"
$apkName     = "CapteurHumidite-$Config.apk"
$apkPath     = Join-Path $livrableDir $apkName
$phoneDest   = "/sdcard/Download/$apkName"

# --- Verification APK ---
if (-not (Test-Path $apkPath)) {
    Write-Error "APK introuvable : $apkPath`nLancez d'abord .\publish-apk.ps1"
    exit 1
}

# --- Recherche ADB ---
$adb = Get-Command adb -ErrorAction SilentlyContinue

if (-not $adb) {
    # Recherche dans les emplacements standards
    $candidates = @(
        "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
        "$env:ProgramFiles\Android\android-sdk\platform-tools\adb.exe"
        "${env:ProgramFiles(x86)}\Android\android-sdk\platform-tools\adb.exe"
    )
    foreach ($path in $candidates) {
        if (Test-Path $path) {
            $adb = Get-Item $path
            break
        }
    }
}

if (-not $adb) {
    Write-Error "ADB introuvable.`nInstallez Android SDK Platform-Tools ou ajoutez-le au PATH."
    exit 1
}

$adbExe = if ($adb -is [System.Management.Automation.ApplicationInfo]) { $adb.Source } else { $adb.FullName }
Write-Host "  ADB : $adbExe" -ForegroundColor Gray

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deploiement APK sur telephone" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- Verification appareil connecte ---
Write-Host "[1/2] Verification du telephone..." -ForegroundColor Yellow

$devices = & $adbExe devices | Select-Object -Skip 1 | Where-Object { $_ -match "device$" }

if (-not $devices) {
    Write-Error "Aucun telephone detecte.`nVerifiez la connexion USB et que le debogage USB est active."
    exit 1
}

$deviceId = ($devices[0] -split "\s+")[0]
Write-Host "  Appareil detecte : $deviceId" -ForegroundColor Gray

# --- Copie vers le telephone ---
Write-Host "[2/2] Copie vers Telechargements..." -ForegroundColor Yellow

& $adbExe push $apkPath $phoneDest

if ($LASTEXITCODE -ne 0) {
    Write-Error "Echec de la copie vers le telephone."
    exit 1
}

# --- Resume ---
$size = [math]::Round((Get-Item $apkPath).Length / 1MB, 2)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  APK copie sur le telephone :" -ForegroundColor Green
Write-Host "  $phoneDest" -ForegroundColor White
Write-Host "  Taille : $size Mo" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Ouvrez le fichier depuis l'app" -ForegroundColor White
Write-Host "  Fichiers > Telechargements" -ForegroundColor White
Write-Host "  pour installer l'APK." -ForegroundColor White
Write-Host ""
