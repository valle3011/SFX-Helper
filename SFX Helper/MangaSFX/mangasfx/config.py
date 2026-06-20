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

# ---------------------------------------------------------------------
# 5) EINGEBAUTE FONT-REGELN  (Stichwort -> Font(s), nach Stimmung gruppiert)
# ---------------------------------------------------------------------
# Diese Regeln sind sofort aktiv: Tippst du oben ein passendes SFX-Wort,
# schlägt der Docker die zugehörigen Fonts vor (nach Gruppen sortiert).
# Eigene Regeln im Docker kommen zusätzlich dazu und überschreiben nichts.
#
# Die Stichwörter decken englische UND romanisierte japanische Onomatopöie
# ab (z. B. "doki" = Herzklopfen, "gashan" = Klirren, "zan" = Schnitt).
# Lange/gedehnte Schreibweisen werden automatisch erkannt ("BOOOOM" -> boom).
#
# WICHTIG: Die Fonts müssen in Windows installiert sein, damit Krita sie
# anzeigt. Die hier genutzten Namen sind die echten Familiennamen der
# Blambot-Comic-Schriften (BadaBoom, Blambot FXPro, Astounder usw.).
SFX_RULES = [
    {"group": "Boom / Impact",
     "keywords": ["boom", "kaboom", "bam", "blam", "bang", "blast",
                  "explosion", "explode", "doon", "dosun", "dgah", "gogo"],
     "fonts": ["BadaBoom Pro BB", "A.C.M.E. Explosive",
               "Astounder Squared BB"]},
    {"group": "Hit / Punch",
     "keywords": ["pow", "smack", "whack", "thwack", "punch", "bonk", "thud",
                  "doki", "doka", "baki", "doga", "gusha", "boko", "buchi"],
     "fonts": ["BeatDown BB", "Astounder Squared BB"]},
    {"group": "Crash / Break",
     "keywords": ["crash", "smash", "crack", "shatter", "break", "crunch",
                  "gashan", "gachan", "bari", "mishi", "pakin"],
     "fonts": ["Autodestruct BB", "A.C.M.E. Explosive"]},
    {"group": "Slash / Cut",
     "keywords": ["slash", "slice", "cut", "shing", "shink", "swish", "swoosh",
                  "zan", "zash", "suba", "shaki", "zubaa"],
     "fonts": ["Brushzerker BB", "Armor Piercing BB"]},
    {"group": "Gun / Metal",
     "keywords": ["shot", "gun", "clang", "ping", "ratatat", "kachak",
                  "kakin", "gakin", "chakin"],
     "fonts": ["Bulletproof BB", "Armor Piercing BB"]},
    {"group": "Electric / Energy",
     "keywords": ["zap", "bzzt", "buzz", "spark", "crackle", "bachi",
                  "biri", "pachi", "bishi"],
     "fonts": ["BlackHole BB", "Android Nation BB"]},
    {"group": "Sci-fi / Tech",
     "keywords": ["beep", "boop", "whirr", "vwoom", "hum", "mecha", "robot",
                  "wiin"],
     "fonts": ["Android Nation BB", "Astrogator BB"]},
    {"group": "Magic / Glow",
     "keywords": ["magic", "glow", "shimmer", "sparkle", "kira", "pika",
                  "fwoosh", "vwoo", "fuwa"],
     "fonts": ["Arcanum BB", "Astounder Round BB"]},
    {"group": "Shout / Loud",
     "keywords": ["shout", "yell", "roar", "waaah", "gyaa", "uwaa",
                  "raaah", "gao", "gaaah", "doooh"],
     "fonts": ["Always Angry BB", "BigBadBold BB"]},
    {"group": "Horror / Scary",
     "keywords": ["scream", "kyaa", "blood", "gore", "creak", "drip", "doku",
                  "zoku", "gurgle", "zawa", "giri"],
     "fonts": ["BloodyMurder BB", "Afterlife BB"]},
    {"group": "Monster / Zombie",
     "keywords": ["groan", "growl", "gah", "braain", "ugh", "ghaa",
                  "gao"],
     "fonts": ["Braaains BB", "Afterlife BB"]},
    {"group": "Soft / Quiet",
     "keywords": ["whisper", "soft", "hush", "mutter", "mumble",
                  "pata", "koso", "suya", "sniff", "potsu"],
     "fonts": ["Blambot Casual", "Anime Ace 2.0 BB"]},
    {"group": "Cute / Light",
     "keywords": ["pop", "poof", "fwip", "tap", "pomf", "puni", "fluff",
                  "twinkle", "boing", "pyon"],
     "fonts": ["Astounder Round BB", "Blambot Casual"]},
]
