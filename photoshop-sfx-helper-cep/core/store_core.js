/* AUTO-COPIED from sfx-core/ by sync-core.py - edit the source there. */
/*
 * store_core.js – plattformUNABHÄNGIGER Teil der Persistenz: Standardzustand,
 * Migrate (defensiv gegen alte/fehlende Felder), Import-Helfer (sanitizeRules,
 * mergeFontRules) und die Lern-Statistik. KEINE Datei-/PS-/UXP-Zugriffe – mit
 * Node testbar und von BEIDEN Photoshop-Plugins (UXP + CEP) genutzt.
 *
 * Der plattformspezifische IO-Teil (loadState/saveState) liegt je Plugin in
 * store.js (UXP) bzw. store_cep.js (CEP) und baut auf diesem Kern auf.
 */

const { DEFAULTS } = require("./rules");

// Vollständiger Standardzustand (Startwerte aus rules.DEFAULTS).
function defaultState() {
  return {
    settings: {
      font: "",
      size: DEFAULTS.size,
      fill: DEFAULTS.fill,
      outline: DEFAULTS.outline,
      outline_px: DEFAULTS.outline_px,
      shadow: DEFAULTS.shadow,
      shadow_color: DEFAULTS.shadow_color,
      shadow_dx: DEFAULTS.shadow_dx,
      shadow_dy: DEFAULTS.shadow_dy,
      uppercase: true,
      bold: false,
      italic: false,
    },
    user_presets: [],
    font_rules: [],          // eigene Regeln, jede mit group/keywords/fonts/lang
    rule_lang: "en",
    ui_lang: "en",
    favorites: [],
    usage: {},               // { normWort: { fontName: anzahl } }
    collapsed: {},           // { sectionKey: true } – eingeklappte Panel-Abschnitte
    sections: {},            // { sectionKey: false } – ganz ausgeblendete Abschnitte
    ui_scale: 100,           // UI-Skalierung in Prozent (Größe des Dockers)
    hidden_builtins: [],     // Schlüssel (grouplang) gelöschter Built-in-Regeln
  };
}

// Geladene Daten defensiv mit dem Standard mischen (additiv, alte Felder ok).
function migrate(data) {
  const out = defaultState();
  if (!data || typeof data !== "object") return out;
  if (data.settings && typeof data.settings === "object") {
    Object.assign(out.settings, data.settings);
  }
  if (Array.isArray(data.user_presets)) out.user_presets = data.user_presets;
  if (Array.isArray(data.font_rules)) {
    out.font_rules = sanitizeRules(data.font_rules);
  }
  if (typeof data.rule_lang === "string") out.rule_lang = data.rule_lang;
  if (typeof data.ui_lang === "string") out.ui_lang = data.ui_lang;
  if (Array.isArray(data.favorites)) out.favorites = data.favorites;
  if (data.usage && typeof data.usage === "object") out.usage = data.usage;
  if (data.collapsed && typeof data.collapsed === "object") out.collapsed = data.collapsed;
  if (data.sections && typeof data.sections === "object") out.sections = data.sections;
  if (typeof data.ui_scale === "number") out.ui_scale = data.ui_scale;
  if (Array.isArray(data.hidden_builtins)) out.hidden_builtins = data.hidden_builtins;
  return out;
}

// Importierte Font-Regeln robust machen (fehlende Felder, alt -> "*");
// unvollständige (keine keywords/fonts) verwerfen.
function sanitizeRules(raw) {
  const out = [];
  if (!Array.isArray(raw)) return out;
  for (const r of raw) {
    if (!r || typeof r !== "object") continue;
    const kws = Array.isArray(r.keywords)
      ? r.keywords.map((k) => String(k).trim().toLowerCase()).filter(Boolean) : [];
    const fonts = Array.isArray(r.fonts)
      ? r.fonts.map((f) => String(f).trim()).filter(Boolean) : [];
    if (!kws.length || !fonts.length) continue;
    out.push({
      group: String(r.group || "").trim(),
      keywords: kws,
      fonts: fonts,
      lang: String(r.lang || "").trim() || "*",
    });
  }
  return out;
}

// Importierte Regeln in `existing` einmischen: gleiche (Gruppe, Sprache) ->
// Stichwörter/Fonts vereinigen statt Duplikat anzulegen; sonst anhängen.
function mergeFontRules(existing, imported) {
  const out = (existing || []).map((r) => ({
    group: r.group, keywords: r.keywords.slice(),
    fonts: r.fonts.slice(), lang: r.lang || "*",
  }));
  const key = (r) => String(r.group || "").trim().toLowerCase() + " " + (r.lang || "*");
  const index = {};
  out.forEach((r, i) => { if (!(key(r) in index)) index[key(r)] = i; });
  for (const r of imported) {
    const k = key(r);
    if (k in index) {
      const tgt = out[index[k]];
      for (const kw of r.keywords) if (tgt.keywords.indexOf(kw) === -1) tgt.keywords.push(kw);
      for (const f of r.fonts) if (tgt.fonts.indexOf(f) === -1) tgt.fonts.push(f);
    } else {
      index[k] = out.length;
      out.push({ group: r.group, keywords: r.keywords.slice(),
                 fonts: r.fonts.slice(), lang: r.lang || "*" });
    }
  }
  return out;
}

// Lern-Statistik fortschreiben: Wort(normalisiert) -> gewählte Schrift +1.
function recordUsage(state, normWord, font) {
  if (!normWord || !font) return state;
  if (!state.usage) state.usage = {};
  if (!state.usage[normWord]) state.usage[normWord] = {};
  const d = state.usage[normWord];
  d[font] = (d[font] || 0) + 1;
  return state;
}

module.exports = {
  defaultState, migrate, sanitizeRules, mergeFontRules, recordUsage,
};
