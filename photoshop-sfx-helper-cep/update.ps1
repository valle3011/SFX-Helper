# SFX Helper (CEP) updater. Refreshes the shared core (if sfx-core/ is next to
# this plugin) and then runs a clean reinstall. Your saved data (presets, rules,
# learned fonts) lives outside the extension folder, so it is preserved.
# Run update_win.cmd (double-click) or:
#   PowerShell -ExecutionPolicy Bypass -File update.ps1
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = $PSScriptRoot

# 1) If the repo layout is present, pull the latest shared core into core/.
$sync = Join-Path (Split-Path $ScriptDir -Parent) "sync-core.py"
if (Test-Path $sync) {
    Write-Host "Refreshing shared core (sync-core.py) ..." -ForegroundColor Yellow
    try { python $sync } catch { Write-Host "sync-core.py skipped (python not found)." -ForegroundColor Yellow }
}

# 2) Reinstall (install.ps1 does a clean copy = update; keeps PlayerDebugMode).
$install = Join-Path $ScriptDir "install.ps1"
if (-not (Test-Path $install)) {
    Write-Host "[ERROR] install.ps1 not found next to this script." -ForegroundColor Red
    Read-Host "Press Enter to quit"
    exit 1
}
& $install
