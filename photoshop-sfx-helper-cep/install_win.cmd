@echo off
:: Doppelklick-Installer: ruft install.ps1 ohne ExecutionPolicy-Hürde auf.
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File "install.ps1"
