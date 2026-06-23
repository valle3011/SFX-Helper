@echo off
:: Doppelklick-Updater: frischt den geteilten Kern auf (falls vorhanden) und
:: installiert sauber neu. Eigene Daten (Presets/Regeln/Lernen) bleiben erhalten.
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File "update.ps1"
