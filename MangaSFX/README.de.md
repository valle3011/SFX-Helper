# SFX Helper – Krita-Docker

Ein dockbares Panel für Krita 5.x, mit dem du schnell gestaltete Manga-SFX
(Sound Effects) mit Outline in eine **Vektor-Ebene** setzt – ohne Font,
Farbe und Kontur jedes Mal von Hand einzustellen.

## Funktionen
- Texteingabe für das SFX-Wort
- Font-Dropdown mit allen installierten Fonts (durchsuchbar) + Favoritenliste
- Regler/Felder für Schriftgröße, Füllfarbe, Outline-Farbe, Outline-Stärke
- **Optionaler Schlagschatten** (neu): Farbe + Versatz X/Y
- **WYSIWYG-Live-Vorschau** (neu): zeigt den Text mit der tatsächlichen
  **Kontur und dem Schatten** (nicht nur Füllung), eingepasst in die Fläche
- Preset-Buttons (Font + Farbe + Outline + Schatten auf einen Klick)
- „SFX einfügen“ -> erzeugt SVG-Text und fügt ihn per `addShapesFromSvg`
  in die aktive Vektor-Ebene ein (legt sie automatisch an, falls nötig). Der
  Text wird jetzt **zentriert** gesetzt – in die Mitte der aktiven **Auswahl**,
  sonst in die Bildmitte (nicht mehr oben links).
- Font-Vorschläge: du legst im Docker fest, welche Font(s) zu welchem SFX-Wort
  passen – optional in Gruppen (z. B. Shout/Scared/Normal/Leise); beim Tippen
  erscheinen sie nach Gruppen geordnet als anklickbarer Vorschlag
- Sprache umschaltbar: **Englisch = Standard**, Deutsch – oben im Docker
- Komfort: Live-Vorschau der Schrift, GROSSBUCHSTABEN-, Fett- und Kursiv-Schalter,
  und der Docker merkt sich den zuletzt genutzten Stil über Neustarts
- „Zurücksetzen"-Button: Stil auf Standardwerte – optional auch alle eigenen
  Presets + Font-Regeln löschen
- Import/Export: eigene Presets + Font-Regeln (mit Gruppen) als `.json` sichern,
  teilen und wieder einlesen (Zusammenführen oder Ersetzen)

---

## Installation (Windows, Krita 5.x)

1. **Resource-Ordner öffnen**
   Krita -> *Einstellungen ▸ Ressourcen verwalten… ▸ Ressourcenordner öffnen*.
   Alternativ direkt im Explorer:
   `C:\Users\<DU>\AppData\Roaming\krita\`

2. Darin in den Ordner **`pykrita`** wechseln (falls nicht vorhanden: anlegen).

3. **Hineinkopieren** (genau diese zwei Dinge):
   ```
   pykrita\
     ├─ mangasfx.desktop      <- die Datei
     └─ mangasfx\             <- der ganze Ordner mit allen .py-Dateien
          ├─ __init__.py
          ├─ config.py
          ├─ i18n.py
          ├─ presets_store.py
          ├─ svg_builder.py
          └─ sfx_docker.py
   ```
   Wichtig: `mangasfx.desktop` liegt **neben** dem Ordner `mangasfx\`,
   nicht darin.

4. **Krita neu starten.**

5. **Plugin aktivieren**
   *Einstellungen ▸ Krita einrichten… ▸ Python-Plugin-Manager* ->
   Häkchen bei **„SFX Helper“** -> OK -> **Krita erneut neu starten**.

6. **Docker einblenden**
   *Einstellungen ▸ Andockbare Dialoge ▸ SFX Helper*.

> Hinweis: Es muss eine Python-fähige Krita-Version sein (der normale
> Windows-Build von krita.org ist das standardmäßig).

---

## Benutzung
1. Dokument offen haben, SFX-Wort eintippen.
2. Font/Größe/Farben/Schatten wählen **oder** ein Preset klicken. Die
   **Live-Vorschau** zeigt genau, wie es aussehen wird (mit Kontur + Schatten).
3. **„SFX einfügen“** (oder Enter im Textfeld).
   Ist gerade keine Vektor-Ebene aktiv, wird automatisch eine Ebene „SFX“
   angelegt. Der Text wird **zentriert** gesetzt (in die aktive Auswahl, sonst
   in die Bildmitte) – danach frei verschieben/transformieren.

---

## Selbst erweitern – alles in `config.py`

**Fonts:** Das Dropdown enthält automatisch ALLE installierten System-Fonts
(einfach reintippen und suchen). `SFX_FONTS` ist nur deine Favoriten-Liste
für den Schnellzugriff oben im Dropdown – der erste Eintrag ist der Standard.
Alle Fonts ausblenden und nur Favoriten zeigen: `SHOW_ALL_SYSTEM_FONTS = False`.
```python
SFX_FONTS = [
    "CC Wild Words",         # Standard
    "Mein Lieblings-SFX",    # <- neu als Favorit
]
```

**Presets direkt im Docker anlegen (empfohlen):**
1. Font, Größe, Farben und Outline einstellen.
2. **„＋ Aktuelles als Preset speichern"** klicken und einen Namen vergeben.
3. Optional Schlüsselwörter (Komma-getrennt) angeben – tippst du so ein Wort
   später in den SFX-Text, schlägt der Docker dieses Preset vor.

Dein Preset erscheint sofort als Button. **Rechtsklick auf ein eigenes Preset**
öffnet ein Menü: *Umbenennen*, *Schlüsselwörter bearbeiten*, *Mit aktuellen
Reglerwerten überschreiben* oder *Löschen*. So bearbeitest du ein Preset:
Button anklicken (lädt die Werte) → Regler anpassen → Rechtsklick →
*Mit aktuellen Reglerwerten überschreiben*. Gespeichert wird in den
Krita-Einstellungen, bleibt also über Neustarts erhalten.

**Integrierte Presets** bearbeitest du im Block `SFX_PRESETS` (`config.py`);
`keywords` ist optional und steuert den Mood-Vorschlag:
```python
{
    "name": "Donner",
    "font": "Bangers",
    "size": 150,
    "fill": "#101010",
    "outline": "#ffd400",
    "outline_px": 7,
    "keywords": ["donner", "rumble"],   # optional
},
```

**Font-Vorschläge (welche Font[s] zu welchem SFX-Wort passen):**
Abschnitt *Font-Vorschläge* im Docker → **„＋ Font-Regel hinzufügen"**:
1. **Gruppe** wählen oder neu eintippen (z. B. `Shout`, `Scared`, `Normal`,
   `Leise`) – so legst du für dasselbe Wort mehrere Stimmungs-Varianten an.
   Leer lassen = ohne Gruppe.
2. Stichwörter angeben (Komma-getrennt, z. B. `ah, aah`).
3. Font(s) wählen: ein **durchsuchbares Font-Dropdown** + „Hinzufügen" (so kannst
   du Namen bequem nachschlagen); die Liste bleibt frei editierbar, also auch
   **mehrere Fonts** per Komma möglich.

Beispiel: Lege für das Wort `ah` vier Regeln an – Gruppe *Shout* → lauter Font,
*Scared* → zittriger Font, *Normal* → Standardfont, *Leise* → dünner Font.
Tippst du oben `ah`, erscheinen die Vorschläge **nach Gruppen geordnet**
(Klick setzt den Font). **Linksklick** auf eine Regel bearbeitet sie,
**Rechtsklick** öffnet *Bearbeiten/Löschen*. Wird dauerhaft gespeichert.

Es gibt **29 eingebaute Regeln** (über 400 SFX, englisch + romanisiert
japanisch), die sofort aktiv sind. Zusätzlich:
- **Schätzung für unbekannte SFX:** Passt kein Wort, rät eine Lautmuster-
  Heuristik die Stimmung (z. B. `DKKBAM` → Boom, `fwooosh` → Whoosh,
  `iiiieee` → Schrei, `zzzz` → Schlaf) – Überschrift „Beste Schätzung".
- **Lernt mit:** Beim Einfügen merkt sich der Docker, welche Schrift du für
  welches Wort gewählt hast, und bietet sie beim nächsten Mal unter „Vorher
  benutzt" zuerst an (in den Krita-Einstellungen gespeichert).

**Presets & Regeln sichern/teilen:** Unten im Docker schreibt **Export…** deine
eigenen Presets + Font-Regeln (inkl. Gruppen) in eine `.json`-Datei; **Import…**
liest sie wieder ein – wahlweise *Zusammenführen* (zu Vorhandenem dazu, gleicher
Preset-Name wird ersetzt, exakte Doppel-Regeln werden übersprungen) oder
*Ersetzen* (alles Eigene durch die Datei überschreiben). Praktisch für Backups
oder den Wechsel zwischen Rechnern. Integrierte Presets aus `config.py` sind
nicht betroffen.

Nach Änderungen an `config.py` genügt ein **Krita-Neustart**.

---

## Was du noch von Hand machst
Das Plugin setzt den Text sauber – die künstlerische Platzierung bleibt
deine Arbeit:
- **Positionieren/Skalieren/Rotieren:** Werkzeug *Form bearbeiten* bzw.
  *Transformieren* (Strg+T).
- **Warpen/Perspektive** (SFX an Bewegung/Panel anpassen): Transformieren ->
  *Verkrümmen*, *Käfig* oder *Perspektive*. Tipp: Bei starkem Warp die
  SFX-Ebene vorher per Rechtsklick *In Pixel-Ebene umwandeln* (rastern),
  dann verzerrt es zuverlässiger.
- **Feinschliff:** Verlauf/Glow auf der Füllung oder doppelte Outline – als
  zusätzliche Ebenen-Effekte. (Ein einfacher **Schlagschatten** ist jetzt
  eingebaut.)

> Performance-Hinweis: Die System-Font-Liste wird nur **einmal eingelesen und
> gecacht** – der Docker bleibt auch bei sehr großen Font-Sammlungen flott.
