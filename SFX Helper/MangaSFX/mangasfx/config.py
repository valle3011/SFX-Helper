# -*- coding: utf-8 -*-
"""
=====================================================================
  HIER ANPASSEN  –  Fonts, Presets, Mood-Mapping, Startwerte
=====================================================================
Alles, was du regelmäßig ändern willst, steht in dieser einen Datei.
Du musst den restlichen Code nicht anfassen.
"""

# ---------------------------------------------------------------------
# 1) FONTS
# ---------------------------------------------------------------------
# Du musst NICHT alle Fonts von Hand eintragen: Das Dropdown wird
# automatisch mit ALLEN installierten System-Fonts gefüllt – einfach
# reintippen und suchen. Die Namen kommen direkt aus Qt, stimmen also
# garantiert mit Kritas Schreibweise überein.
#
# SFX_FONTS ist nur noch deine FAVORITEN-Liste: Diese Fonts erscheinen
# zum Schnellzugriff ganz oben im Dropdown (über einem Trennstrich).
# Der erste Eintrag ist der Standard beim Öffnen.
SFX_FONTS = [
    "CC Wild Words",     # <- Standard / Schnellzugriff (Dialog & "Soft")
    "CC Shout Out",      # deine laute SFX-Schrift
    "Impact",            # immer vorhanden -> Fallback
    "Creepster",         # Horror-Platzhalter (später ersetzen)
]

# Zusätzlich alle installierten System-Fonts anzeigen? (empfohlen: True)
SHOW_ALL_SYSTEM_FONTS = True

# ---------------------------------------------------------------------
# 2) PRESETS  -> ein Klick setzt Font + Größe + Farben + Outline
# ---------------------------------------------------------------------
# Das sind die INTEGRIERTEN Presets. Weitere Presets legst du bequem
# direkt im Docker an (Button „Aktuelles als Preset speichern“) – die
# werden gespeichert und bleiben erhalten.
#
# "outline_px" = sichtbare Konturstärke in Pixeln.
# "keywords"   = optionale Schlüsselwörter (klein) für den Mood-Vorschlag:
#                tippst du so ein Wort in den SFX-Text, schlägt der Docker
#                dieses Preset vor. Leere Liste/weglassen = kein Vorschlag.
SFX_PRESETS = [
    {
        "name": "Loud",
        "font": "CC Shout Out",
        "size": 160,
        "fill": "#000000",      # schwarz
        "outline": "#ffffff",   # weiß
        "outline_px": 8,
        "keywords": ["boom", "crash", "bang", "explo"],
    },
    {
        "name": "Soft",
        "font": "CC Wild Words",
        "size": 90,
        "fill": "#3a3a3a",      # dunkelgrau
        "outline": "#ffffff",
        "outline_px": 3,
        "keywords": ["whisper", "soft"],
    },
    {
        "name": "Horror",
        "font": "Creepster",
        "size": 140,
        "fill": "#000000",      # schwarz
        "outline": "#c0140f",   # blutrot
        "outline_px": 6,
        "keywords": ["scream", "blood", "horror"],
    },
]

# ---------------------------------------------------------------------
# 3) MOOD-VORSCHLAG
# ---------------------------------------------------------------------
# Hier ist nichts mehr einzustellen: Der Mood-Vorschlag nutzt die
# "keywords" der Presets oben (integrierte UND die im Docker selbst
# angelegten). Willst du ein Wort einem Stil zuordnen, gib dem passenden
# Preset einfach ein Schlüsselwort.

# ---------------------------------------------------------------------
# 4) STARTWERTE der Regler beim Öffnen des Dockers
# ---------------------------------------------------------------------
DEFAULTS = {
    "size": 140,
    "fill": "#000000",
    "outline": "#ffffff",
    "outline_px": 8,
}
