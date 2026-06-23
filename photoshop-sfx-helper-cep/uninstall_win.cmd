@echo off
:: Doppelklick-Deinstaller: ruft uninstall.ps1 ohne ExecutionPolicy-Hürde auf.
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File "uninstall.ps1"
