/* AUTO-COPIED from sfx-core/ by sync-core.py - edit the source there. */
/*
 * rules.js – Daten: Favoriten-Fonts, eingebaute Presets, Startwerte und die
 * eingebauten Font-Regeln (Stichwort -> Fonts, nach Stimmung gruppiert).
 *
 * Reine Daten, keine Photoshop-Abhängigkeit – mit Node testbar. 1:1 aus der
 * Krita-Version (MangaSFX/mangasfx/config.py) übernommen.
 *
 * Jede Regel hat ein Sprachfeld "lang":
 *   "en"/"de"/"es"/… = nur aktiv, wenn diese Regelsprache gewählt ist
 *   "*"              = immer aktiv (romanisierte japanische Onomatopöie)
 * Die Fontnamen sind die echten Familiennamen der Blambot-Comic-Schriften;
 * sie müssen im System installiert sein, damit Photoshop sie rendert.
 */

// Favoriten zum Schnellzugriff oben in der Schriftauswahl (erster = Standard).
const SFX_FONTS = [
  "CC Wild Words",
  "CC Shout Out",
  "Impact",
  "Creepster",
];

// Eingebaute Presets: ein Klick setzt Font + Größe + Farben + Outline.
const SFX_PRESETS = [
  { name: "Loud", font: "CC Shout Out", size: 160, fill: "#000000",
    outline: "#ffffff", outline_px: 8,
    keywords: ["boom", "crash", "bang", "explo"] },
  { name: "Soft", font: "CC Wild Words", size: 90, fill: "#3a3a3a",
    outline: "#ffffff", outline_px: 3,
    keywords: ["whisper", "soft"] },
  { name: "Horror", font: "Creepster", size: 140, fill: "#000000",
    outline: "#c0140f", outline_px: 6,
    keywords: ["scream", "blood", "horror"] },
];

// Startwerte der Regler.
const DEFAULTS = {
  size: 140,
  fill: "#000000",
  outline: "#ffffff",
  outline_px: 8,
  shadow: false,
  shadow_color: "#000000",
  shadow_dx: 6,
  shadow_dy: 6,
};

// Sprachen, für die eine Regelsprache gewählt werden kann (Endonyme fürs Menü).
const RULE_LANGS = ["en", "de", "es", "fr", "pt", "it"];
const RULE_LANG_NAMES = {
  en: "English", de: "Deutsch", es: "Español",
  fr: "Français", pt: "Português", it: "Italiano",
};

// Eingebaute Font-Regeln. r() füllt "lang" auf "en" auf (englische Regeln).
function r(group, keywords, fonts, lang) {
  return { group, keywords, fonts, lang: lang || "en" };
}

const SFX_RULES = [
  // --- Englisch ----------------------------------------------------------
  r("Boom / Explosion",
    ["boom", "kaboom", "bam", "bang", "blam", "blast", "explode", "burst",
     "detonate", "kablam", "badoom", "thoom", "doom", "doomf", "slam", "don",
     "donn", "dokan", "dogan", "dosun", "doshin"],
    ["BadaBoom Pro BB", "A.C.M.E. Explosive", "Astounder Squared BB"]),
  r("Hit / Punch",
    ["pow", "wham", "smack", "slap", "thud", "thump", "bonk", "whack", "whomp",
     "whump", "bump", "bop", "knock", "kick", "punch", "chop", "uppercut",
     "bash", "ram", "charge", "impact", "hit", "doga", "dogo", "gotsu", "baki"],
    ["BeatDown BB", "Astounder Squared BB", "ActionFigure BB"]),
  r("Crash / Break",
    ["crash", "smash", "crack", "clash", "break", "shatter", "crunch", "gasha",
     "bakin", "pakin", "paki", "bari"],
    ["Autodestruct BB", "A.C.M.E. Explosive"]),
  r("Slash / Cut / Tear",
    ["slash", "slice", "cut", "stab", "pierce", "swipe", "shing", "jab", "poke",
     "snap", "rip", "tear", "zan", "giri"],
    ["Brushzerker BB", "Armor Piercing BB"]),
  r("Gunfire",
    ["shot", "gun", "ratatat", "tatatat", "ping", "pew", "blam"],
    ["Bulletproof BB", "Armor Piercing BB"]),
  r("Metal / Clang / Click",
    ["clang", "clink", "clunk", "clank", "kachi", "katsu", "click", "clack",
     "tick", "tock", "ting", "twang", "thunk", "doink", "plunk", "clatter",
     "gatan", "gata", "goton", "gacha", "gakin", "gokin", "kaan", "kiin"],
    ["Armor Piercing BB", "Armored Science BB", "Android Nation BB"]),
  r("Whoosh / Dash",
    ["dash", "whoosh", "woosh", "swoosh", "swish", "fwoosh", "fwip", "whiz",
     "zing", "voom", "vwoom", "rush", "fwash", "fwish", "shoop", "shoopf",
     "run", "sprint", "race", "suu", "sutto"],
    ["Blowhole BB", "BlackHole BB", "Astrogator BB"]),
  r("Jump / Fall / Slide",
    ["hop", "skip", "jump", "leap", "land", "bounce", "roll", "tumble", "fall",
     "collapse", "slide", "slip", "skid"],
    ["ActionFigure BB", "Astounder Round BB"]),
  r("Friction / Creak",
    ["scrape", "scratch", "scuff", "creak", "screech", "grind", "girii"],
    ["AtlandSketches BB", "Brushzerker BB"]),
  r("Rumble / Shake",
    ["rumble", "rattle", "shake", "tremble", "quake", "shiver", "racket",
     "noise", "gogo", "goro", "gorogoro"],
    ["Autodestruct BB", "Astounder Squared BB"]),
  r("Engine / Electronic",
    ["beep", "boop", "buzz", "bzzz", "vrrr", "whirr", "vroom", "zoom", "rev",
     "engine", "toot", "honk", "ding", "dong", "ring", "alarm", "brrring",
     "mecha", "robot"],
    ["Android Nation BB", "Astrogator BB"]),
  r("Electric / Spark",
    ["zap", "zzt", "bzzzt", "spark", "flash", "biri", "bachi", "pachi", "bishi",
     "crackle", "sizzle", "fizz"],
    ["BlackHole BB", "Android Nation BB"]),
  r("Sparkle / Shine / Magic",
    ["shine", "sparkle", "kira", "pika", "glimmer", "gleam", "twinkle",
     "shimmer", "blink", "wink", "gira", "glow", "magic"],
    ["Arcanum BB", "Astounder Round BB"]),
  r("Water / Liquid",
    ["splash", "splish", "sploosh", "drip", "drop", "plop", "pour", "gush",
     "spray", "splatter", "bubble", "ripple", "wave", "stream", "shower",
     "plip", "glug", "glub", "gurgle", "blub", "basha", "pasha", "poro",
     "pota", "gutsu"],
    ["Blowhole BB", "Astounder Round BB"]),
  r("Eating / Mouth",
    ["munch", "chomp", "nom", "nibble", "chew", "gobble", "slurp", "sip",
     "gulp", "swallow", "burp", "zuru"],
    ["Blambot Casual", "AveAve BB"]),
  r("Cry / Sob",
    ["sob", "boohoo", "waaah", "wail", "whimper", "cry", "hic", "sniff"],
    ["Blambot Casual", "Anime Ace 2.0 BB"]),
  r("Breath / Sleep",
    ["gasp", "cough", "hack", "sigh", "pant", "huff", "puff", "breathe",
     "groan", "moan", "yawn", "snore", "doze", "sleep", "faint", "zzz"],
    ["Blambot Casual", "Afterlife BB"]),
  r("Whisper / Silence",
    ["murmur", "mumble", "whisper", "psst", "shhh", "hush", "mutter", "koso",
     "shiin", "shin"],
    ["Anime Ace 2.0 BB", "Background Echo", "Afterlife BB"]),
  r("Laugh / Smile",
    ["giggle", "chuckle", "snicker", "cackle", "haha", "hehe", "fufu", "kukuku",
     "teehee", "wahaha", "niko", "niyari", "nita"],
    ["Blambot Casual", "Astromonkey"]),
  r("Roar / Growl",
    ["roar", "growl", "grr", "snarl", "howl", "grah", "graa", "gao"],
    ["Always Angry BB", "Braaains BB", "BloodyMurder BB"]),
  r("Scream / Shout",
    ["scream", "yell", "shout", "shriek", "gyaa", "gyan", "kyaa", "uwaa",
     "uwah", "hyaa", "hiss"],
    ["Always Angry BB", "BigBadBold BB"]),
  r("Reaction",
    ["eek", "ack", "ugh", "oof", "ow", "aah", "eh", "huh", "wha", "yikes",
     "gaan"],
    ["ActionFigure BB", "Anime Ace 2.0 BB"]),
  r("Heartbeat / Tension / Stare",
    ["doki", "kyun", "piku", "bikun", "biku", "jii", "throb", "heartbeat",
     "drum", "beat", "badump", "bathump", "dun", "zawa", "stare", "glare",
     "look", "peek", "peep", "nod", "tilt", "turn"],
    ["Astounder Squared BB", "Afterlife BB", "BloodyMurder BB"]),
  r("Touch / Grab / Soft",
    ["cling", "grab", "clutch", "squeeze", "hug", "pet", "stroke", "rub",
     "tickle", "pinch", "flick", "peta", "beta", "pera", "mofu", "fuwa",
     "noro", "sara", "hira"],
    ["Astounder Round LC BB", "A Brush No", "Blambot Casual"]),
  r("Pop / Bounce",
    ["pop", "poof", "fwump", "boing", "pon", "pyon", "poyo", "fluff"],
    ["Astounder Round BB", "AveAve BB", "Blambot Casual"]),
  r("Flutter / Flap",
    ["flutter", "rustle", "swirl", "spin", "twirl", "flap", "basa", "batan"],
    ["Astounder Round LC BB", "A Brush No"]),
  r("Footsteps / Taps",
    ["tap", "pat", "step", "tok", "toko", "patter", "pitter", "clop", "stomp",
     "stamp", "march", "shuffle", "drag", "trudge"],
    ["Blambot Casual", "Astounder Round BB"]),
  r("Clap / Cheer",
    ["clap", "applause", "cheer", "yay", "hooray", "tada"],
    ["ActionFigure BB", "BigBadBold BB"]),
  r("Animal",
    ["nyaa", "nyan", "meow", "purr", "woof", "bark", "arf", "chirp", "tweet",
     "caw", "hoot", "croak", "ribbit"],
    ["Blambot Casual", "Astromonkey"]),

  // --- Universell: romanisierte japanische Onomatopöie (immer aktiv) -----
  r("JP Impact", ["don", "dokan", "dosun", "doshin", "dogan", "gogo", "goro"],
    ["BadaBoom Pro BB", "Astounder Squared BB"], "*"),
  r("JP Hit", ["doki", "doka", "baki", "doga", "gotsu", "gusha", "boko"],
    ["BeatDown BB", "Astounder Squared BB"], "*"),
  r("JP Crash", ["gasha", "gashan", "gachan", "bakin", "pakin", "bari"],
    ["Autodestruct BB", "A.C.M.E. Explosive"], "*"),
  r("JP Slash", ["zan", "zash", "giri", "suba", "shaki"],
    ["Brushzerker BB", "Armor Piercing BB"], "*"),
  r("JP Metal", ["gakin", "gokin", "kaan", "kiin", "gatan", "gacha"],
    ["Armor Piercing BB", "Android Nation BB"], "*"),
  r("JP Electric", ["biri", "bachi", "pachi", "bishi"],
    ["BlackHole BB", "Android Nation BB"], "*"),
  r("JP Sparkle", ["kira", "pika", "gira"],
    ["Arcanum BB", "Astounder Round BB"], "*"),
  r("JP Heartbeat", ["doki", "kyun", "piku", "bikun", "zawa"],
    ["Astounder Squared BB", "Afterlife BB"], "*"),
  r("JP Soft", ["peta", "beta", "fuwa", "mofu", "pyon", "pon", "sara", "koso",
     "niko"],
    ["Blambot Casual", "Astounder Round BB"], "*"),
  r("JP Water", ["basha", "pasha", "poro", "pota", "gutsu"],
    ["Blowhole BB", "Astounder Round BB"], "*"),
  r("JP Silence", ["shiin", "shin"],
    ["Afterlife BB", "Background Echo"], "*"),

  // --- Deutsch -----------------------------------------------------------
  r("Knall", ["bumm", "bum", "peng", "pang", "wumm", "rumms", "kawumm", "päng",
     "wamm"],
    ["BadaBoom Pro BB", "A.C.M.E. Explosive", "Astounder Squared BB"], "de"),
  r("Schlag", ["bums", "klatsch", "patsch", "zack", "batsch", "plopp", "knuff"],
    ["BeatDown BB", "Astounder Squared BB"], "de"),
  r("Krachen", ["krach", "splitter", "knack", "ratsch", "klirr", "bersten"],
    ["Autodestruct BB", "A.C.M.E. Explosive"], "de"),
  r("Metall", ["kling", "klong", "scheppern", "klimper"],
    ["Armor Piercing BB", "Android Nation BB"], "de"),
  r("Wusch", ["wusch", "schwupp", "zisch", "sausen", "flitz", "wuff"],
    ["Blowhole BB", "BlackHole BB"], "de"),
  r("Schrei", ["aaah", "waaah", "hilfe", "brüll", "kreisch", "röhr", "argh"],
    ["Always Angry BB", "BigBadBold BB"], "de"),
  r("Leise", ["flüster", "psst", "schnief", "schluchz", "murmel", "tapp",
     "klopf", "schnarch"],
    ["Blambot Casual", "Anime Ace 2.0 BB"], "de"),
  r("Lachen", ["haha", "hihi", "hoho", "kicher", "gröl", "grins"],
    ["Blambot Casual", "Astromonkey"], "de"),

  // --- Spanisch ----------------------------------------------------------
  r("Explosión", ["bum", "bam", "pum", "cataplum", "catapum", "buum", "boom"],
    ["BadaBoom Pro BB", "A.C.M.E. Explosive", "Astounder Squared BB"], "es"),
  r("Golpe", ["pam", "paf", "zas", "plaf", "toma", "cataplaf", "zasca"],
    ["BeatDown BB", "Astounder Squared BB"], "es"),
  r("Romper", ["crac", "cras", "plas", "crunch", "chas"],
    ["Autodestruct BB", "A.C.M.E. Explosive"], "es"),
  r("Metal", ["clin", "clon", "tolon", "tilin", "ñiqui"],
    ["Armor Piercing BB", "Android Nation BB"], "es"),
  r("Veloz", ["fiu", "zum", "fium", "swoosh", "shht"],
    ["Blowhole BB", "BlackHole BB"], "es"),
  r("Grito", ["aaah", "aaay", "socorro", "grr", "guaaa", "buaaa"],
    ["Always Angry BB", "BigBadBold BB"], "es"),
  r("Suave", ["psst", "shh", "snif", "muac", "toc", "ronc", "glup"],
    ["Blambot Casual", "Anime Ace 2.0 BB"], "es"),
  r("Risa", ["jaja", "jiji", "jeje", "muajaja", "joro"],
    ["Blambot Casual", "Astromonkey"], "es"),
];

module.exports = {
  SFX_FONTS, SFX_PRESETS, DEFAULTS, SFX_RULES, RULE_LANGS, RULE_LANG_NAMES,
};
