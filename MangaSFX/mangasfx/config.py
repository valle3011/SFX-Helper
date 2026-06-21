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
    # Schatten (Schlagschatten als versetzte Kopie) – standardmäßig aus
    "shadow": False,
    "shadow_color": "#000000",
    "shadow_dx": 6,
    "shadow_dy": 6,
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
    {"group": "Boom / Explosion",
     "keywords": ["boom", "kaboom", "bam", "bang", "blam", "blast", "explode",
                  "burst", "detonate", "kablam", "badoom", "thoom", "doom",
                  "doomf", "slam", "don", "donn", "dokan", "dogan", "dosun",
                  "doshin"],
     "fonts": ["BadaBoom Pro BB", "A.C.M.E. Explosive",
               "Astounder Squared BB"]},
    {"group": "Hit / Punch",
     "keywords": ["pow", "wham", "smack", "slap", "thud", "thump", "bonk",
                  "whack", "whomp", "whump", "bump", "bop", "knock", "kick",
                  "punch", "chop", "uppercut", "bash", "ram", "charge",
                  "impact", "hit", "doga", "dogo", "gotsu", "baki"],
     "fonts": ["BeatDown BB", "Astounder Squared BB", "ActionFigure BB"]},
    {"group": "Crash / Break",
     "keywords": ["crash", "smash", "crack", "clash", "break", "shatter",
                  "crunch", "gasha", "bakin", "pakin", "paki", "bari"],
     "fonts": ["Autodestruct BB", "A.C.M.E. Explosive"]},
    {"group": "Slash / Cut / Tear",
     "keywords": ["slash", "slice", "cut", "stab", "pierce", "swipe", "shing",
                  "jab", "poke", "snap", "rip", "tear", "zan", "giri"],
     "fonts": ["Brushzerker BB", "Armor Piercing BB"]},
    {"group": "Gunfire",
     "keywords": ["shot", "gun", "ratatat", "tatatat", "ping", "pew", "blam"],
     "fonts": ["Bulletproof BB", "Armor Piercing BB"]},
    {"group": "Metal / Clang / Click",
     "keywords": ["clang", "clink", "clunk", "clank", "kachi", "katsu", "click",
                  "clack", "tick", "tock", "ting", "twang", "thunk", "doink",
                  "plunk", "clatter", "gatan", "gata", "goton", "gacha", "gakin",
                  "gokin", "kaan", "kiin"],
     "fonts": ["Armor Piercing BB", "Armored Science BB", "Android Nation BB"]},
    {"group": "Whoosh / Dash",
     "keywords": ["dash", "whoosh", "woosh", "swoosh", "swish", "fwoosh", "fwip",
                  "whiz", "zing", "voom", "vwoom", "rush", "fwash", "fwish",
                  "shoop", "shoopf", "run", "sprint", "race", "suu", "sutto"],
     "fonts": ["Blowhole BB", "BlackHole BB", "Astrogator BB"]},
    {"group": "Jump / Fall / Slide",
     "keywords": ["hop", "skip", "jump", "leap", "land", "bounce", "roll",
                  "tumble", "fall", "collapse", "slide", "slip", "skid"],
     "fonts": ["ActionFigure BB", "Astounder Round BB"]},
    {"group": "Friction / Creak",
     "keywords": ["scrape", "scratch", "scuff", "creak", "screech", "grind",
                  "girii"],
     "fonts": ["AtlandSketches BB", "Brushzerker BB"]},
    {"group": "Rumble / Shake",
     "keywords": ["rumble", "rattle", "shake", "tremble", "quake", "shiver",
                  "racket", "noise", "gogo", "goro", "gorogoro"],
     "fonts": ["Autodestruct BB", "Astounder Squared BB"]},
    {"group": "Engine / Electronic",
     "keywords": ["beep", "boop", "buzz", "bzzz", "vrrr", "whirr", "vroom",
                  "zoom", "rev", "engine", "toot", "honk", "ding", "dong",
                  "ring", "alarm", "brrring", "mecha", "robot"],
     "fonts": ["Android Nation BB", "Astrogator BB"]},
    {"group": "Electric / Spark",
     "keywords": ["zap", "zzt", "bzzzt", "spark", "flash", "biri", "bachi",
                  "pachi", "bishi", "crackle", "sizzle", "fizz"],
     "fonts": ["BlackHole BB", "Android Nation BB"]},
    {"group": "Sparkle / Shine / Magic",
     "keywords": ["shine", "sparkle", "kira", "pika", "glimmer", "gleam",
                  "twinkle", "shimmer", "blink", "wink", "gira", "glow",
                  "magic"],
     "fonts": ["Arcanum BB", "Astounder Round BB"]},
    {"group": "Water / Liquid",
     "keywords": ["splash", "splish", "sploosh", "drip", "drop", "plop", "pour",
                  "gush", "spray", "splatter", "bubble", "ripple", "wave",
                  "stream", "shower", "plip", "glug", "glub", "gurgle", "blub",
                  "basha", "pasha", "poro", "pota", "gutsu"],
     "fonts": ["Blowhole BB", "Astounder Round BB"]},
    {"group": "Eating / Mouth",
     "keywords": ["munch", "chomp", "nom", "nibble", "chew", "gobble", "slurp",
                  "sip", "gulp", "swallow", "burp", "zuru"],
     "fonts": ["Blambot Casual", "AveAve BB"]},
    {"group": "Cry / Sob",
     "keywords": ["sob", "boohoo", "waaah", "wail", "whimper", "cry", "hic",
                  "sniff"],
     "fonts": ["Blambot Casual", "Anime Ace 2.0 BB"]},
    {"group": "Breath / Sleep",
     "keywords": ["gasp", "cough", "hack", "sigh", "pant", "huff", "puff",
                  "breathe", "groan", "moan", "yawn", "snore", "doze", "sleep",
                  "faint", "zzz"],
     "fonts": ["Blambot Casual", "Afterlife BB"]},
    {"group": "Whisper / Silence",
     "keywords": ["murmur", "mumble", "whisper", "psst", "shhh", "hush",
                  "mutter", "koso", "shiin", "shin"],
     "fonts": ["Anime Ace 2.0 BB", "Background Echo", "Afterlife BB"]},
    {"group": "Laugh / Smile",
     "keywords": ["giggle", "chuckle", "snicker", "cackle", "haha", "hehe",
                  "fufu", "kukuku", "teehee", "wahaha", "niko", "niyari",
                  "nita"],
     "fonts": ["Blambot Casual", "Astromonkey"]},
    {"group": "Roar / Growl",
     "keywords": ["roar", "growl", "grr", "snarl", "howl", "grah", "graa",
                  "gao"],
     "fonts": ["Always Angry BB", "Braaains BB", "BloodyMurder BB"]},
    {"group": "Scream / Shout",
     "keywords": ["scream", "yell", "shout", "shriek", "gyaa", "gyan", "kyaa",
                  "uwaa", "uwah", "hyaa", "hiss"],
     "fonts": ["Always Angry BB", "BigBadBold BB"]},
    {"group": "Reaction",
     "keywords": ["eek", "ack", "ugh", "oof", "ow", "aah", "eh", "huh", "wha",
                  "yikes", "gaan"],
     "fonts": ["ActionFigure BB", "Anime Ace 2.0 BB"]},
    {"group": "Heartbeat / Tension / Stare",
     "keywords": ["doki", "kyun", "piku", "bikun", "biku", "jii", "throb",
                  "heartbeat", "drum", "beat", "badump", "bathump", "dun",
                  "zawa", "stare", "glare", "look", "peek", "peep", "nod",
                  "tilt", "turn"],
     "fonts": ["Astounder Squared BB", "Afterlife BB", "BloodyMurder BB"]},
    {"group": "Touch / Grab / Soft",
     "keywords": ["cling", "grab", "clutch", "squeeze", "hug", "pet", "stroke",
                  "rub", "tickle", "pinch", "flick", "peta", "beta", "pera",
                  "mofu", "fuwa", "noro", "sara", "hira"],
     "fonts": ["Astounder Round LC BB", "A Brush No", "Blambot Casual"]},
    {"group": "Pop / Bounce",
     "keywords": ["pop", "poof", "fwump", "boing", "pon", "pyon", "poyo",
                  "fluff"],
     "fonts": ["Astounder Round BB", "AveAve BB", "Blambot Casual"]},
    {"group": "Flutter / Flap",
     "keywords": ["flutter", "rustle", "swirl", "spin", "twirl", "flap",
                  "basa", "batan"],
     "fonts": ["Astounder Round LC BB", "A Brush No"]},
    {"group": "Footsteps / Taps",
     "keywords": ["tap", "pat", "step", "tok", "toko", "patter", "pitter",
                  "clop", "stomp", "stamp", "march", "shuffle", "drag",
                  "trudge"],
     "fonts": ["Blambot Casual", "Astounder Round BB"]},
    {"group": "Clap / Cheer",
     "keywords": ["clap", "applause", "cheer", "yay", "hooray", "tada"],
     "fonts": ["ActionFigure BB", "BigBadBold BB"]},
    {"group": "Animal",
     "keywords": ["nyaa", "nyan", "meow", "purr", "woof", "bark", "arf",
                  "chirp", "tweet", "caw", "hoot", "croak", "ribbit"],
     "fonts": ["Blambot Casual", "Astromonkey"]},
]
