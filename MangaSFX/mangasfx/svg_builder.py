# -*- coding: utf-8 -*-
"""
SVG-Erzeugung für die SFX-Texte.

Hier entsteht der String, der später per
    vectorLayer.addShapesFromSvg(svg)
in die Vektor-Ebene eingefügt wird.
"""


def _xml_escape(s):
    """Macht Text fürs XML/SVG sicher (z. B. & < > in 'AT&T')."""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))


def build_sfx_svg(text, font_family, font_size, fill, outline, outline_px,
                  bold=False, italic=False, x=40, y=None):
    """
    Baut ein SVG mit genau einem <text>-Element.

    paint-order="stroke":
        Die Kontur wird ZUERST gezeichnet (also HINTER der Füllung) –
        das ist der typische saubere Manga-Outline-Look. Ohne diesen
        Trick würde die Kontur zur Hälfte in die Buchstaben hineinfressen.

    Verdoppelte stroke-width:
        Die Kontur liegt mittig auf der Glyphen-Kante, die Füllung deckt
        die innere Hälfte ab. Sichtbar bleibt also nur die äußere Hälfte.
        Damit "outline_px" der WIRKLICH sichtbaren Stärke entspricht,
        setzen wir stroke-width = outline_px * 2.
    """
    text_esc = _xml_escape(text)
    font_esc = _xml_escape(font_family)

    if y is None:
        # Grundlinie etwa eine Zeilenhöhe nach unten setzen, damit der
        # Text oben nicht abgeschnitten an der Dokumentkante klebt.
        y = int(font_size) + 10

    # Kontur ist optional: bei 0 wird gar kein stroke gesetzt.
    if outline_px and outline_px > 0:
        stroke_attrs = (
            f' stroke="{outline}"'
            f' stroke-width="{outline_px * 2}"'
            f' stroke-linejoin="round"'   # runde Ecken = weicher SFX-Look
            f' paint-order="stroke"'      # Kontur hinter die Füllung
        )
    else:
        stroke_attrs = ""

    # Fett / Kursiv optional (manche SFX-Fonts haben echte Schnitte dafür)
    weight_attr = ' font-weight="bold"' if bold else ""
    style_attr = ' font-style="italic"' if italic else ""

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg">\n'
        f'  <text x="{x}" y="{y}" '
        f'font-family="{font_esc}" '
        f'font-size="{font_size}" '
        f'fill="{fill}"'
        f'{weight_attr}'
        f'{style_attr}'
        f'{stroke_attrs}>'
        f'{text_esc}</text>\n'
        '</svg>'
    )
    return svg
