# -*- coding: utf-8 -*-
"""
SVG-Erzeugung für die SFX-Texte.

Hier entsteht der String, der später per
    vectorLayer.addShapesFromSvg(svg)
in die Vektor-Ebene eingefügt wird.

Aufbau von unten nach oben: Schatten -> Kontur -> Füllung. Jede Lage ist eine
eigene Textkopie (statt eines paint-order-Tricks) – so funktioniert es
unabhängig vom SVG-Renderer und der Schatten kann die volle Silhouette zeigen.
"""


def _xml_escape(s):
    """Macht Text fürs XML/SVG sicher (z. B. & < > in 'AT&T')."""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))


def _text_el(text_esc, font_esc, font_size, x, y, anchor, fill,
             weight_attr, style_attr, stroke=None, stroke_w=0.0):
    """Ein einzelnes <text>-Element (eine Lage)."""
    attrs = (
        f'x="{x}" y="{y}" '
        f'font-family="{font_esc}" '
        f'font-size="{font_size}" '
        f'text-anchor="{anchor}" '
        f'fill="{fill}"'
        f'{weight_attr}{style_attr}'
    )
    if stroke is not None and stroke_w > 0:
        attrs += (f' stroke="{stroke}" stroke-width="{stroke_w}"'
                  f' stroke-linejoin="round" stroke-linecap="round"')
    return f'  <text {attrs}>{text_esc}</text>\n'


def build_sfx_svg(text, font_family, font_size, fill, outline, outline_px,
                  bold=False, italic=False, x=40, y=None,
                  anchor="start", img_w=None, img_h=None,
                  shadow=False, shadow_color="#000000",
                  shadow_dx=0.0, shadow_dy=0.0):
    """
    Baut das SVG für einen SFX-Text.

    Verdoppelte stroke-width:
        Die Kontur liegt mittig auf der Glyphen-Kante, die Füllung deckt die
        innere Hälfte ab. Sichtbar bleibt also nur die äußere Hälfte. Damit
        "outline_px" der WIRKLICH sichtbaren Stärke entspricht, setzen wir
        stroke-width = outline_px * 2.

    anchor:
        "start" (Standard, wie früher) oder "middle" – mit "middle" sitzt der
        Text waagerecht zentriert um x (für das Einfügen in die Bild-/Auswahl-
        mitte).

    shadow:
        Optionaler Schlagschatten als versetzte Kopie hinter Kontur + Füllung;
        übernimmt die Konturstärke, damit die Silhouette passt.
    """
    text_esc = _xml_escape(text)
    font_esc = _xml_escape(font_family)

    if y is None:
        # Grundlinie etwa eine Zeilenhöhe nach unten setzen, damit der Text
        # oben nicht abgeschnitten an der Dokumentkante klebt.
        y = int(font_size) + 10

    weight_attr = ' font-weight="bold"' if bold else ""
    style_attr = ' font-style="italic"' if italic else ""

    has_outline = bool(outline_px) and outline_px > 0
    stroke_w = outline_px * 2 if has_outline else 0.0

    body = ""

    # 1) Schatten (ganz unten): versetzte Kopie; übernimmt die Konturstärke
    if shadow and (shadow_dx or shadow_dy):
        body += _text_el(
            text_esc, font_esc, font_size, x + shadow_dx, y + shadow_dy, anchor,
            fill=shadow_color, weight_attr=weight_attr, style_attr=style_attr,
            stroke=(shadow_color if stroke_w > 0 else None), stroke_w=stroke_w)

    # 2) Kontur (Mitte): dicke Linie in Konturfarbe
    if has_outline:
        body += _text_el(
            text_esc, font_esc, font_size, x, y, anchor,
            fill=outline, weight_attr=weight_attr, style_attr=style_attr,
            stroke=outline, stroke_w=stroke_w)

    # 3) Füllung (oben)
    body += _text_el(
        text_esc, font_esc, font_size, x, y, anchor,
        fill=fill, weight_attr=weight_attr, style_attr=style_attr)

    if img_w and img_h:
        size_attrs = f' width="{int(img_w)}" height="{int(img_h)}"'
    else:
        size_attrs = ""

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg"{size_attrs}>\n'
        f'{body}'
        '</svg>'
    )
