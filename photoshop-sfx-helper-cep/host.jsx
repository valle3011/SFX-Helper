/*
 * host.jsx – ExtendScript-Gegenstück zu insert.js (UXP). Läuft IN Photoshop
 * (auch PS 2019) und wird vom Panel per CSInterface.evalScript aufgerufen.
 *
 * WICHTIG: ExtendScript ist ES3 – kein let/const/Arrow/Template/JSON. Hier
 * stehen NUR die Photoshop-Aktionen; die gemeinsame Logik (Regeln/Matching/
 * i18n) läuft im Panel (CEF+Node) über den geteilten Kern.
 *
 * Die Action-Manager-Deskriptoren (Stroke = frameFX außen, Drop Shadow hart,
 * RGB mit Grn/Bl) müssen gegen PS 2019 gegengeprüft werden.
 */

function cTID(s) { return charIDToTypeID(s); }
function sTID(s) { return stringIDToTypeID(s); }

function sfxHexToRGB(hex) {
    hex = String(hex || "").replace("#", "");
    if (hex.length !== 6) hex = "000000";
    return [parseInt(hex.substring(0, 2), 16),
            parseInt(hex.substring(2, 4), 16),
            parseInt(hex.substring(4, 6), 16)];
}

function sfxSolidColor(hex) {
    var c = sfxHexToRGB(hex);
    var s = new SolidColor();
    s.rgb.red = c[0]; s.rgb.green = c[1]; s.rgb.blue = c[2];
    return s;
}

// Alle installierten Schriften als "Name<TAB>PostScriptName" je Zeile.
function sfxListFonts() {
    var out = [];
    try {
        var fonts = app.fonts;
        for (var i = 0; i < fonts.length; i++) {
            var nm = "", ps = "";
            try { nm = fonts[i].name; } catch (e) {}
            try { ps = fonts[i].postScriptName; } catch (e2) {}
            out.push(nm + "\t" + ps);
        }
    } catch (e3) { return ""; }
    return out.join("\n");
}

// Kontur (außen) + optional harter Schlagschatten als Ebenenstil.
function sfxApplyFX(outlineHex, outlinePx, doShadow, shadowHex, sdx, sdy) {
    var oc = sfxHexToRGB(outlineHex);
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putProperty(cTID("Prpr"), sTID("layerEffects"));
    ref.putEnumerated(cTID("Lyr "), cTID("Ordn"), cTID("Trgt"));
    desc.putReference(cTID("null"), ref);

    var fx = new ActionDescriptor();
    fx.putUnitDouble(cTID("Scl "), cTID("#Prc"), 100);

    // Stroke (frameFX, außen)
    if (outlinePx > 0) {
        var fr = new ActionDescriptor();
        fr.putBoolean(cTID("enab"), true);
        fr.putEnumerated(sTID("style"), sTID("frameStyle"), sTID("outsetFrame"));
        fr.putEnumerated(cTID("PntT"), sTID("frameFill"), sTID("solidColor"));
        fr.putEnumerated(cTID("Md  "), cTID("BlnM"), cTID("Nrml"));
        fr.putUnitDouble(cTID("Opct"), cTID("#Prc"), 100);
        fr.putUnitDouble(cTID("Sz  "), cTID("#Pxl"), outlinePx);
        var col = new ActionDescriptor();
        col.putDouble(cTID("Rd  "), oc[0]);
        col.putDouble(cTID("Grn "), oc[1]);
        col.putDouble(cTID("Bl  "), oc[2]);
        fr.putObject(cTID("Clr "), cTID("RGBC"), col);
        fx.putObject(sTID("frameFX"), sTID("frameFX"), fr);
    }

    // Drop Shadow (hart = versetzte Kopie)
    if (doShadow) {
        var sc = sfxHexToRGB(shadowHex);
        var dist = Math.round(Math.sqrt(sdx * sdx + sdy * sdy));
        var ang = Math.atan2(sdy, -sdx) * 180 / Math.PI;
        var sh = new ActionDescriptor();
        sh.putBoolean(cTID("enab"), true);
        sh.putEnumerated(cTID("Md  "), cTID("BlnM"), cTID("Nrml"));
        var scol = new ActionDescriptor();
        scol.putDouble(cTID("Rd  "), sc[0]);
        scol.putDouble(cTID("Grn "), sc[1]);
        scol.putDouble(cTID("Bl  "), sc[2]);
        sh.putObject(cTID("Clr "), cTID("RGBC"), scol);
        sh.putUnitDouble(cTID("Opct"), cTID("#Prc"), 100);
        sh.putBoolean(sTID("useGlobalAngle"), false);
        sh.putUnitDouble(cTID("lagl"), cTID("#Ang"), ang);
        sh.putUnitDouble(cTID("Dstn"), cTID("#Pxl"), dist);
        sh.putUnitDouble(cTID("Ckmt"), cTID("#Pxl"), 0);
        sh.putUnitDouble(cTID("blur"), cTID("#Pxl"), 0);
        fx.putObject(sTID("dropShadow"), sTID("dropShadow"), sh);
    }

    desc.putObject(cTID("T   "), sTID("layerEffects"), fx);
    executeAction(cTID("setd"), desc, DialogModes.NO);
}

// Eigentliche Einfügung (liest die Nutzdaten aus $.global, damit sie in einem
// suspendHistory-Schritt laufen kann).
function sfxDoInsert() {
    var saved = app.preferences.rulerUnits;
    app.preferences.rulerUnits = Units.PIXELS;
    try {
        var p = String($.global.__sfxPayload).split(String.fromCharCode(1));
        var text = p[0], fontPS = p[1], fontName = p[2];
        var size = parseFloat(p[3]) || 100;
        var fillHex = p[4], outlineHex = p[5];
        var outlinePx = parseFloat(p[6]) || 0;
        var bold = p[7] === "1", italic = p[8] === "1", upper = p[9] === "1";
        var shadow = p[10] === "1", shadowHex = p[11];
        var sdx = parseFloat(p[12]) || 0, sdy = parseFloat(p[13]) || 0;

        var doc = app.activeDocument;
        var cx = doc.width.as("px") / 2, cy = doc.height.as("px") / 2;
        try {
            var b = doc.selection.bounds;             // wirft, wenn keine Auswahl
            cx = (b[0].as("px") + b[2].as("px")) / 2;
            cy = (b[1].as("px") + b[3].as("px")) / 2;
        } catch (e) {}

        if (upper) text = text.toUpperCase();
        var layer = doc.artLayers.add();
        layer.kind = LayerKind.TEXT;
        var ti = layer.textItem;
        ti.kind = TextType.POINTTEXT;
        ti.contents = text;
        try { ti.font = fontPS; } catch (e1) {
            try { ti.font = fontName; } catch (e2) {}
        }
        ti.size = size;                                // Punkt
        ti.color = sfxSolidColor(fillHex);
        try { ti.fauxBold = bold; } catch (e3) {}
        try { ti.fauxItalic = italic; } catch (e4) {}
        ti.position = [cx, cy];

        // exakt auf den Zielmittelpunkt schieben
        var lb = layer.bounds;
        var lcx = (lb[0].as("px") + lb[2].as("px")) / 2;
        var lcy = (lb[1].as("px") + lb[3].as("px")) / 2;
        layer.translate(cx - lcx, cy - lcy);

        sfxApplyFX(outlineHex, outlinePx, shadow, shadowHex, sdx, sdy);
        $.global.__sfxResult = "ok";
    } catch (err) {
        $.global.__sfxResult = "err:" + err.toString();
    } finally {
        app.preferences.rulerUnits = saved;
    }
}

// Vom Panel aufgerufen: alles in EINEM Undo-Schritt.
function sfxInsert(payload) {
    if (!app.documents.length) return "no_document";
    $.global.__sfxPayload = payload;
    $.global.__sfxResult = "";
    try {
        app.activeDocument.suspendHistory("Insert SFX", "sfxDoInsert()");
    } catch (e) {
        sfxDoInsert();                                 // Fallback ohne Bündelung
    }
    return $.global.__sfxResult || "ok";
}
