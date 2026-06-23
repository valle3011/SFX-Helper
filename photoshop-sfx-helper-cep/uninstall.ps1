# SFX Helper (CEP) uninstaller. Removes the extension from the user's CEP
# extensions folder. Optionally also deletes your saved data (presets, rules,
# learned fonts). Does NOT touch PlayerDebugMode (other extensions may need it).
# Run uninstall_win.cmd (double-click) or:
#   PowerShell -ExecutionPolicy Bypass -File uninstall.ps1
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$TargetDir = Join-Path $env:APPDATA "Adobe\CEP\extensions\sfxhelper"
$DataDir   = Join-Path $env:APPDATA "SFXHelperCEP"

Clear-Host
Write-Host "+--------------------------------------------------+" -ForegroundColor Cyan
Write-Host "|             SFX Helper - Uninstaller              |" -ForegroundColor Cyan
Write-Host "+--------------------------------------------------+" -ForegroundColor Cyan
Write-Host ""
Write-Host "Close Photoshop first (if it is open)." -ForegroundColor Yellow
Read-Host "Press Enter to continue"

# --- 1. Remove the extension folder ---
if (Test-Path $TargetDir) {
    Remove-Item $TargetDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Removed: $TargetDir" -ForegroundColor Green
} else {
    Write-Host "Extension not found (already removed): $TargetDir" -ForegroundColor Yellow
}

# --- 2. Optionally remove saved data ---
if (Test-Path $DataDir) {
    Write-Host ""
    $ans = Read-Host "Also delete your saved data (presets, rules, learned fonts)? [y/N]"
    if ($ans -match '^(y|yes|j|ja)$') {
        Remove-Item $DataDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Removed saved data: $DataDir" -ForegroundColor Green
    } else {
        Write-Host "Kept saved data: $DataDir" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "Done. Restart Photoshop to drop the panel from the Extensions menu."
Read-Host "Press Enter to quit"
