# SFX Helper (CEP) installer for Photoshop 2019+.
# Sets PlayerDebugMode automatically (HKCU, no admin, no manual regedit) and
# copies the extension into the user's CEP extensions folder. Run install_win.cmd
# (double-click) or: PowerShell -ExecutionPolicy Bypass -File install.ps1
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = $PSScriptRoot
Set-Location -Path $ScriptDir

# --- 1. Sanity check: manifest present ---
$ManifestPath = Join-Path $ScriptDir "CSXS\manifest.xml"
if (-not (Test-Path $ManifestPath)) {
    Write-Host "[ERROR] Not found: $ManifestPath" -ForegroundColor Red
    Write-Host "Run this from the 'photoshop-sfx-helper-cep' folder (next to CSXS, core, host.jsx)."
    Read-Host "Press Enter to quit"
    exit 1
}

# --- 2. Make sure the shared core is present (run sync-core.py if missing) ---
if (-not (Test-Path (Join-Path $ScriptDir "core\rules.js"))) {
    $sync = Join-Path (Split-Path $ScriptDir -Parent) "sync-core.py"
    if (Test-Path $sync) {
        Write-Host "core/ missing - running sync-core.py ..." -ForegroundColor Yellow
        try { python $sync } catch { Write-Host "Could not run sync-core.py automatically." -ForegroundColor Yellow }
    }
}

Clear-Host
Write-Host "+--------------------------------------------------+" -ForegroundColor Cyan
Write-Host "|              SFX Helper - Installer               |" -ForegroundColor Cyan
Write-Host "+--------------------------------------------------+" -ForegroundColor Cyan
Write-Host ""
Write-Host "Close Photoshop first (if it is open)." -ForegroundColor Yellow
Read-Host "Press Enter to continue"

# --- 3. Enable unsigned extensions (PlayerDebugMode) for installed CSXS 6..12 ---
# HKCU only -> no admin rights needed. This is the same registry switch you would
# otherwise set by hand; the script just does it for you.
6..12 | ForEach-Object {
    $RegPath = "HKCU:\Software\Adobe\CSXS.$_"
    if (-not (Test-Path $RegPath)) { New-Item -Path $RegPath -Force | Out-Null }
    Set-ItemProperty -Path $RegPath -Name "PlayerDebugMode" -Value "1" -Type String -ErrorAction SilentlyContinue
}

# --- 4. Copy the extension into the user CEP extensions folder ---
$TargetDir = Join-Path $env:APPDATA "Adobe\CEP\extensions\sfxhelper"
if (Test-Path $TargetDir) { Remove-Item $TargetDir -Recurse -Force -ErrorAction SilentlyContinue }
New-Item -Path $TargetDir -ItemType Directory -Force | Out-Null

$items = @("core", "lib", "CSXS", "host.jsx", "index.html", "main.js",
           "store_cep.js", ".debug", "README.md")
foreach ($item in $items) {
    $src = Join-Path $ScriptDir $item
    if (Test-Path $src) { Copy-Item $src -Destination $TargetDir -Recurse -Force }
}

# --- 5. Done ---
Write-Host ""
Write-Host "+--------------------------------------------------+" -ForegroundColor Green
Write-Host "|             Installation completed                |" -ForegroundColor Green
Write-Host "+--------------------------------------------------+" -ForegroundColor Green
Write-Host ""
Write-Host "Installed to: $TargetDir"
Write-Host "Open Photoshop and click: [Window] > [Extensions] > [SFX Helper]" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to quit"
