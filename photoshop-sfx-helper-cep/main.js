/*
 * main.js – Panel-Verhalten des CEP-SFX-Helper (PS 2019+). Gleiche UI/Logik wie
 * die UXP-Version (ui.js); nur die plattformspezifischen Teile sind anders:
 *   - Fonts + Einfügen laufen über host.jsx (CSInterface.evalScript),
 *   - Persistenz über Node-fs (store_cep.js),
 *   - Import/Export über window.cep.fs.
 * Die gemeinsame Logik (Regeln/Matching/Vorschläge/i18n/Schema) kommt 1:1 aus
 * dem geteilten Kern in core/.
 */

var CS = new CSInterface();
var EXT_ROOT = CS.getSystemPath(SystemPath.EXTENSION);

var RULES = require(EXT_ROOT + "/core/rules.js");
var MATCH = require(EXT_ROOT + "/core/match.js");
var I18N = require(EXT_ROOT + "/core/i18n.js");
var STORE = require(EXT_ROOT + "/store_cep.js");

var nodeFs = require("fs");
var nodePath = require("path");
var DATA_DIR = nodePath.join(CS.getSystemPath(SystemPath.USER_DATA), "SFXHelperCEP");
try { nodeFs.mkdirSync(DATA_DIR, { recursive: true }); } catch (e) {}
var DATA_FILE = nodePath.join(DATA_DIR, "sfxhelper.json");

var state = null;
var fonts = [];
var saveTimer = null;
var editingRef = { kind: "new" };   // welche Regel gerade bearbeitet wird

function el(id) { return document.getElementById(id); }
function t(key) { return I18N.tr(state.ui_lang, key); }
var DEL = String.fromCharCode(1);

function scheduleSave() {
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(function () { STORE.saveState(DATA_FILE, state); }, 400);
}

// --- i18n auf das statische Markup anwenden --------------------------------
function applyI18n() {
  var n = document.querySelectorAll("[data-i18n]");
  for (var i = 0; i < n.length; i++) n[i].textContent = t(n[i].getAttribute("data-i18n"));
  var p = document.querySelectorAll("[data-i18n-ph]");
  for (var j = 0; j < p.length; j++) p[j].setAttribute("placeholder", t(p[j].getAttribute("data-i18n-ph")));
}

function buildSelect(sel, items, names, value) {
  sel.innerHTML = "";
  for (var i = 0; i < items.length; i++) {
    var o = document.createElement("option");
    o.value = items[i]; o.textContent = names[items[i]] || items[i];
    if (items[i] === value) o.selected = true;
    sel.appendChild(o);
  }
}

// --- Schriftliste ----------------------------------------------------------
function buildFontList() {
  var sel = el("fontList");
  var filter = (el("fontSearch").value || "").toLowerCase();
  sel.innerHTML = "";
  var seen = {};
  function add(label, family, ps, fav) {
    if (filter && label.toLowerCase().indexOf(filter) === -1) return;
    var o = document.createElement("option");
    o.value = ps || family || label;
    o.textContent = (fav ? "★ " : "") + label;
    o.setAttribute("data-family", family || label);
    o.setAttribute("data-ps", ps || "");
    if ((ps || family || label) === state.settings.font) o.selected = true;
    sel.appendChild(o);
  }
  var favs = RULES.SFX_FONTS.concat(state.favorites || []);
  for (var i = 0; i < favs.length; i++) {
    if (seen[favs[i]]) continue; seen[favs[i]] = 1;
    var hit = null;
    for (var k = 0; k < fonts.length; k++) {
      if (fonts[k].family === favs[i] || fonts[k].name === favs[i]) { hit = fonts[k]; break; }
    }
    add(favs[i], hit ? hit.family : favs[i], hit ? hit.postScriptName : "", true);
  }
  for (var j = 0; j < fonts.length; j++) {
    var label = fonts[j].family || fonts[j].name;
    if (seen[label]) continue; seen[label] = 1;
    add(label, fonts[j].family, fonts[j].postScriptName, false);
  }
  if (!sel.options.length) add("Impact", "Impact", "", true);
}

function selectedFont() {
  var sel = el("fontList");
  var o = sel.options[sel.selectedIndex] || sel.options[0];
  if (!o) return { family: "Impact", postScriptName: "", name: "Impact" };
  return { family: o.getAttribute("data-family") || o.value,
           postScriptName: o.getAttribute("data-ps") || "",
           name: (o.textContent || "").replace(/^★ /, "") };
}

// --- Inputs <-> Style ------------------------------------------------------
function readInputs() {
  var f = selectedFont(), s = state.settings;
  s.font = f.postScriptName || f.family;
  s.fontFamily = f.family;
  s.size = parseFloat(el("size").value) || RULES.DEFAULTS.size;
  s.fill = el("fill").value || "#000000";
  s.outline = el("outline").value || "#ffffff";
  s.outline_px = parseFloat(el("outlineW").value) || 0;
  s.uppercase = el("upper").checked;
  s.bold = el("boldChk").checked;
  s.italic = el("italicChk").checked;
  s.shadow = el("shadowChk").checked;
  s.shadow_color = el("shadowColor").value || "#000000";
  s.shadow_dx = parseFloat(el("shadowX").value) || 0;
  s.shadow_dy = parseFloat(el("shadowY").value) || 0;
}

function writeInputs() {
  var s = state.settings;
  el("size").value = s.size; el("fill").value = s.fill;
  el("outline").value = s.outline; el("outlineW").value = s.outline_px;
  el("upper").checked = !!s.uppercase; el("boldChk").checked = !!s.bold;
  el("italicChk").checked = !!s.italic; el("shadowChk").checked = !!s.shadow;
  el("shadowColor").value = s.shadow_color;
  el("shadowX").value = s.shadow_dx; el("shadowY").value = s.shadow_dy;
  updateSwatches();
}

function updateSwatches() {
  el("fillSwatch").style.background = el("fill").value || "#000";
  el("outlineSwatch").style.background = el("outline").value || "#fff";
  el("shadowSwatch").style.background = el("shadowColor").value || "#000";
}

// --- Live-Vorschau ---------------------------------------------------------
function refreshPreview() {
  var cv = el("preview"), ctx = cv.getContext("2d");
  var w = cv.width = cv.clientWidth || 260, h = cv.height = cv.clientHeight || 90;
  ctx.clearRect(0, 0, w, h);
  var txt = el("sfxText").value || "BOOM";
  if (state.settings.uppercase) txt = txt.toUpperCase();
  var fam = state.settings.fontFamily || "Impact";
  var styleStr = (state.settings.italic ? "italic " : "") + (state.settings.bold ? "bold " : "");
  var px = 64;
  ctx.font = styleStr + px + 'px "' + fam + '"';
  var tw = ctx.measureText(txt).width || 1;
  px = Math.max(10, Math.min(px * (w - 24) / tw, h - 24));
  ctx.font = styleStr + px + 'px "' + fam + '"';
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  var cx = w / 2, cy = h / 2;
  var k = px / Math.max(1, state.settings.size);
  var ow = Math.max(0, state.settings.outline_px * k);
  if (state.settings.shadow) {
    ctx.fillStyle = state.settings.shadow_color;
    ctx.fillText(txt, cx + state.settings.shadow_dx * k, cy + state.settings.shadow_dy * k);
  }
  if (ow > 0) {
    ctx.lineWidth = ow * 2; ctx.lineJoin = "round";
    ctx.strokeStyle = state.settings.outline; ctx.strokeText(txt, cx, cy);
  }
  ctx.fillStyle = state.settings.fill; ctx.fillText(txt, cx, cy);
}

// --- Vorschläge ------------------------------------------------------------
function refreshSuggestions() {
  var box = el("suggestions"); box.innerHTML = "";
  var res = MATCH.suggest(el("sfxText").value, {
    rules: activeRulesForMatch(),
    presets: RULES.SFX_PRESETS.concat(state.user_presets || []),
    lang: state.rule_lang, usage: state.usage, limit: 8,
  });
  function addChips(label, list, cls) {
    if (!list.length) return;
    var wrap = document.createElement("div");
    if (label) {
      var l = document.createElement("div");
      l.className = "sgroup-label"; l.textContent = label; wrap.appendChild(l);
    }
    var chips = document.createElement("div"); chips.className = "chips";
    for (var i = 0; i < list.length; i++) {
      (function (font) {
        var b = document.createElement("button");
        b.className = "chip" + (cls ? " " + cls : "");
        b.textContent = font;
        b.addEventListener("click", function () { pickFont(font); });
        chips.appendChild(b);
      })(list[i]);
    }
    wrap.appendChild(chips); box.appendChild(wrap);
  }
  if (res.learned.length) addChips(t("suggestions_learned"), res.learned, "learned");
  for (var i = 0; i < res.groups.length; i++) {
    addChips(res.groups[i].group, res.groups[i].fonts, res.guessed ? "guess" : "");
  }
  if (!box.children.length) {
    var m = document.createElement("span");
    m.className = "muted"; m.textContent = t("no_suggestions"); box.appendChild(m);
  }
}

function pickFont(family) {
  var sel = el("fontList"), found = null;
  for (var i = 0; i < sel.options.length; i++) {
    var o = sel.options[i];
    if (o.getAttribute("data-family") === family ||
        o.textContent.replace(/^★ /, "") === family) { found = o; break; }
  }
  if (!found) {
    found = document.createElement("option");
    found.value = family; found.textContent = family;
    found.setAttribute("data-family", family);
    sel.insertBefore(found, sel.firstChild);
  }
  found.selected = true;
  readInputs(); refreshPreview(); scheduleSave();
}

// --- Presets ---------------------------------------------------------------
function renderPresets() {
  var box = el("presets"); box.innerHTML = "";
  var all = RULES.SFX_PRESETS.concat(state.user_presets || []);
  for (var i = 0; i < all.length; i++) {
    (function (p) {
      var b = document.createElement("button");
      b.textContent = p.name;
      b.addEventListener("click", function () { applyPreset(p); });
      box.appendChild(b);
    })(all[i]);
  }
}

function applyPreset(p) {
  var s = state.settings;
  if (p.size) s.size = p.size;
  if (p.fill) s.fill = p.fill;
  if (p.outline) s.outline = p.outline;
  if (typeof p.outline_px === "number") s.outline_px = p.outline_px;
  if (typeof p.bold === "boolean") s.bold = p.bold;
  if (typeof p.italic === "boolean") s.italic = p.italic;
  if (p.font) pickFont(p.font);
  writeInputs(); refreshPreview(); scheduleSave();
}

function saveCurrentPreset() {
  var name = (el("sfxText").value || "Preset").trim().slice(0, 24) || "Preset";
  var f = selectedFont();
  state.user_presets.push({
    name: name, font: f.family, size: state.settings.size,
    fill: state.settings.fill, outline: state.settings.outline,
    outline_px: state.settings.outline_px, bold: state.settings.bold,
    italic: state.settings.italic, keywords: [],
  });
  renderPresets(); scheduleSave(); setStatus(t("presets") + " +1");
}

// --- Regel-Manager: anzeigen / hinzufügen / bearbeiten / löschen -----------
// Auch EINGEBAUTE Regeln sind bearbeitbar/löschbar: gelöschte/bearbeitete
// Built-ins werden per Schlüssel (group+lang) in state.hidden_builtins
// ausgeblendet; "Eingebaute zurücksetzen" macht das rückgängig.
function ruleIsActive(r) {
  var l = r.lang || "*";
  return l === "*" || l === state.rule_lang;
}

function builtinKey(r) { return (r.group || "") + "\u0001" + (r.lang || "*"); }
function hiddenSet() {
  var m = {}, h = state.hidden_builtins || [];
  for (var i = 0; i < h.length; i++) m[h[i]] = true;
  return m;
}

function activeRulesForMatch() {
  var hid = hiddenSet(), out = [];
  for (var i = 0; i < RULES.SFX_RULES.length; i++) {
    if (!hid[builtinKey(RULES.SFX_RULES[i])]) out.push(RULES.SFX_RULES[i]);
  }
  return out.concat(state.font_rules || []);
}

function renderRules() {
  var box = el("rulesList");
  if (!box) return;
  box.innerHTML = "";
  var hid = hiddenSet();
  function label(txt, cls) {
    var d = document.createElement("div");
    d.className = "sgroup-label" + (cls ? " " + cls : "");
    d.textContent = txt; box.appendChild(d);
  }
  var user = [], fr = state.font_rules || [];
  for (var i = 0; i < fr.length; i++) {
    if (ruleIsActive(fr[i])) user.push({ r: fr[i], ref: { kind: "user", idx: i } });
  }
  var builtins = [];
  for (var k = 0; k < RULES.SFX_RULES.length; k++) {
    var br = RULES.SFX_RULES[k];
    if (ruleIsActive(br) && !hid[builtinKey(br)]) builtins.push(br);
  }
  if (user.length) label(t("your_rules"));
  for (var u = 0; u < user.length; u++) box.appendChild(ruleRow(user[u].r, user[u].ref, false));
  if (builtins.length) label(t("builtin_rules"), "muted");
  for (var b = 0; b < builtins.length; b++) {
    box.appendChild(ruleRow(builtins[b],
      { kind: "builtin", key: builtinKey(builtins[b]), rule: builtins[b] }, true));
  }
  if (!user.length && !builtins.length) label(t("no_rules"), "muted");
  var restore = el("restoreBuiltins");
  if (restore) restore.style.display = (state.hidden_builtins || []).length ? "" : "none";
}

function ruleRow(r, ref, builtin) {
  var row = document.createElement("div");
  row.className = "rule-row";
  var info = document.createElement("div");
  info.className = "rule-info";
  var g = document.createElement("div");
  g.className = "rule-group"; g.textContent = r.group || "—";
  var kw = document.createElement("div");
  kw.className = "rule-meta"; kw.textContent = (r.keywords || []).join(", ");
  var fo = document.createElement("div");
  fo.className = "rule-meta rule-fonts";
  fo.textContent = (r.fonts || []).join(", ");
  fo.addEventListener("click", function () { if (r.fonts && r.fonts[0]) pickFont(r.fonts[0]); });
  info.appendChild(g); info.appendChild(kw); info.appendChild(fo);
  row.appendChild(info);
  var acts = document.createElement("div");
  acts.className = "rule-actions";
  if (builtin) {
    var tag = document.createElement("span");
    tag.className = "rule-tag"; tag.textContent = t("builtin");
    acts.appendChild(tag);
  }
  var ed = document.createElement("button");
  ed.textContent = "✎"; ed.title = t("edit");
  (function (rf) { ed.addEventListener("click", function () { openRuleForm(rf); }); })(ref);
  var del = document.createElement("button");
  del.textContent = "✕"; del.title = t("delete");
  (function (rf) { del.addEventListener("click", function () { deleteRuleRef(rf); }); })(ref);
  acts.appendChild(ed); acts.appendChild(del);
  row.appendChild(acts);
  return row;
}

function openRuleForm(ref) {
  editingRef = (ref && ref.kind) ? ref : { kind: "new" };
  var r;
  if (editingRef.kind === "user") r = state.font_rules[editingRef.idx];
  else if (editingRef.kind === "builtin") r = editingRef.rule;
  else r = { group: "", keywords: [], fonts: [selectedFont().family] };
  el("ruleGroup").value = r.group || "";
  el("ruleKeywords").value = (r.keywords || []).join(", ");
  el("ruleFonts").value = (r.fonts || []).join(", ");
  el("ruleForm").style.display = "";
  el("ruleGroup").focus();
}

function closeRuleForm() {
  el("ruleForm").style.display = "none";
  editingRef = { kind: "new" };
}

function splitList(s) {
  return (s || "").split(",").map(function (x) { return x.trim(); })
    .filter(function (x) { return !!x; });
}

function ruleLangFor(ref) {
  if (ref.kind === "builtin") return ref.rule.lang || "*";
  if (ref.kind === "user") return state.font_rules[ref.idx].lang || state.rule_lang;
  return state.rule_lang;
}

function hideBuiltin(key) {
  if (!state.hidden_builtins) state.hidden_builtins = [];
  if (state.hidden_builtins.indexOf(key) === -1) state.hidden_builtins.push(key);
}

function saveRuleForm() {
  var keywords = splitList(el("ruleKeywords").value).map(function (x) { return x.toLowerCase(); });
  var fonts = splitList(el("ruleFonts").value);
  if (!keywords.length || !fonts.length) { setStatus(t("rule_need")); return; }
  var rule = { group: el("ruleGroup").value.replace(/^\s+|\s+$/g, ""),
               keywords: keywords, fonts: fonts, lang: ruleLangFor(editingRef) };
  if (editingRef.kind === "user") {
    state.font_rules[editingRef.idx] = rule;
  } else {
    if (editingRef.kind === "builtin") hideBuiltin(editingRef.key);
    state.font_rules.push(rule);
  }
  STORE.saveState(DATA_FILE, state);
  closeRuleForm(); renderRules(); refreshSuggestions();
  setStatus(t("rule_saved"));
}

function deleteRuleRef(ref) {
  if (ref.kind === "user") {
    if (ref.idx < 0 || ref.idx >= (state.font_rules || []).length) return;
    state.font_rules.splice(ref.idx, 1);
  } else if (ref.kind === "builtin") {
    hideBuiltin(ref.key);
  }
  STORE.saveState(DATA_FILE, state);
  renderRules(); refreshSuggestions();
  setStatus(t("rule_deleted"));
}

function restoreBuiltins() {
  state.hidden_builtins = [];
  STORE.saveState(DATA_FILE, state);
  renderRules(); refreshSuggestions();
  setStatus(t("restore_builtins"));
}

// --- Ansicht: Größe + Abschnitte ein-/ausblenden + Photoshop-Theme ---------
function applyScale() {
  var sc = Math.max(50, Math.min(300, state.ui_scale || 100)) / 100;
  document.documentElement.style.setProperty("--scale", String(sc));
}

function applySectionVisibility() {
  var secs = document.querySelectorAll(".sec");
  for (var i = 0; i < secs.length; i++) {
    var key = secs[i].getAttribute("data-sec");
    if (key === "view") continue;
    var hidden = state.sections && state.sections[key] === false;
    if (hidden) secs[i].classList.add("hidden-sec");
    else secs[i].classList.remove("hidden-sec");
  }
}

function buildSectionToggles() {
  var box = el("sectionToggles");
  if (!box) return;
  box.innerHTML = "";
  var secs = document.querySelectorAll(".sec");
  for (var i = 0; i < secs.length; i++) {
    (function (sec) {
      var key = sec.getAttribute("data-sec");
      if (!key || key === "view") return;
      var head = sec.querySelector(".sec-head span:last-child");
      var lbl = document.createElement("label");
      var cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = !(state.sections && state.sections[key] === false);
      cb.addEventListener("change", function () {
        if (!state.sections) state.sections = {};
        state.sections[key] = cb.checked;
        applySectionVisibility(); scheduleSave();
      });
      var txt = document.createElement("span");
      txt.textContent = head ? head.textContent : key;
      lbl.appendChild(cb); lbl.appendChild(txt);
      box.appendChild(lbl);
    })(secs[i]);
  }
}

// Photoshop-Theme übernehmen: echte Panel-Hintergrundfarbe aus dem Host lesen
// und die CSS-Variablen setzen (passt sich Kritas… äh Photoshops Hell/Dunkel an).
function applyHostTheme() {
  try {
    var info = CS.getHostEnvironment().appSkinInfo;
    if (!info || !info.panelBackgroundColor) return;
    var c = info.panelBackgroundColor.color;     // {red,green,blue,alpha} 0..255
    var bg = "rgb(" + Math.round(c.red) + "," + Math.round(c.green) + "," + Math.round(c.blue) + ")";
    var dark = (0.299 * c.red + 0.587 * c.green + 0.114 * c.blue) < 128;
    var rs = document.documentElement.style;
    rs.setProperty("--bg", bg);
    rs.setProperty("--fg", dark ? "#d6d6d6" : "#1e1e1e");
    rs.setProperty("--muted-fg", dark ? "#9a9a9a" : "#5a5a5a");
    rs.setProperty("--border", dark ? "#555" : "#b0b0b0");
    rs.setProperty("--input-bg", dark ? "#404040" : "#ffffff");
    rs.setProperty("--input-fg", dark ? "#e8e8e8" : "#1e1e1e");
    rs.setProperty("--btn-bg", dark ? "#4b4b4b" : "#e6e6e6");
    rs.setProperty("--btn-hover", dark ? "#565656" : "#dadada");
  } catch (e) {}
}

// --- Einklappbare Abschnitte (Klick auf den Kopf), Zustand gespeichert ------
function setupCollapsibles() {
  var secs = document.querySelectorAll(".sec");
  for (var i = 0; i < secs.length; i++) {
    (function (sec) {
      var head = sec.querySelector(".sec-head");
      var arrow = sec.querySelector(".arrow");
      var key = sec.getAttribute("data-sec");
      if (!head || !key) return;
      function setArrow(collapsed) {
        if (collapsed) sec.classList.add("collapsed");
        else sec.classList.remove("collapsed");
        if (arrow) arrow.textContent = collapsed ? "▸" : "▾";
      }
      setArrow(!!(state.collapsed && state.collapsed[key]));
      head.onclick = function () {
        var now = !sec.classList.contains("collapsed");
        setArrow(now);
        if (!state.collapsed) state.collapsed = {};
        state.collapsed[key] = now;
        scheduleSave();
      };
    })(secs[i]);
  }
}

// --- Import / Export (CEP) -------------------------------------------------
function exportData() {
  try {
    var res = window.cep.fs.showSaveDialog(t("export"), DATA_DIR);
    if (!res || !res.data) return;
    var p = res.data; if (!/\.json$/i.test(p)) p += ".json";
    nodeFs.writeFileSync(p, JSON.stringify(state, null, 2), "utf8");
    setStatus(t("export") + " ✓");
  } catch (e) { setStatus("Export: " + (e.message || e)); }
}

function importData() {
  try {
    var res = window.cep.fs.showOpenDialog(false, false, t("import"), DATA_DIR, ["json"]);
    if (!res || !res.data || !res.data.length) return;
    var data = JSON.parse(nodeFs.readFileSync(res.data[0], "utf8"));
    var rulesOnly = data && data.font_rules && !data.settings &&
                    !(data.user_presets instanceof Array);
    if (rulesOnly) {
      var imp = STORE.sanitizeRules(data.font_rules);
      state.font_rules = STORE.mergeFontRules(state.font_rules || [], imp);
      setStatus(t("import") + " ✓ (+" + imp.length + ")");
    } else {
      state = STORE.migrate(data);
      setStatus(t("import") + " ✓");
    }
    STORE.saveState(DATA_FILE, state);
    afterStateLoaded();
  } catch (e) { setStatus("Import: " + (e.message || e)); }
}

function resetAll() {
  state = STORE.defaultState();
  STORE.saveState(DATA_FILE, state);
  afterStateLoaded();
  setStatus(t("reset") + " ✓");
}

// --- Einfügen (über host.jsx) ----------------------------------------------
function doInsert() {
  readInputs();
  var text = el("sfxText").value.replace(/^\s+|\s+$/g, "");
  if (!text) return;
  var f = selectedFont(), s = state.settings;
  var payload = [text, f.postScriptName || f.family, f.family, s.size, s.fill,
    s.outline, s.outline_px, s.bold ? "1" : "0", s.italic ? "1" : "0",
    s.uppercase ? "1" : "0", s.shadow ? "1" : "0", s.shadow_color,
    s.shadow_dx, s.shadow_dy].join(DEL);
  setStatus("…");
  CS.evalScript("sfxInsert(" + JSON.stringify(payload) + ")", function (res) {
    if (res === "ok") {
      STORE.recordUsage(state, MATCH.normalizeSfx(text), f.family);
      scheduleSave(); refreshSuggestions(); setStatus(t("inserted"));
    } else if (res === "no_document") {
      setStatus(t("no_document"));
    } else {
      setStatus("⚠ " + res);
    }
  });
}

function setStatus(msg) { el("status").textContent = msg || ""; }

function setUiLang(code) {
  state.ui_lang = code; applyI18n(); refreshSuggestions(); renderPresets();
  renderRules(); scheduleSave();
}
function setRuleLang(code) {
  state.rule_lang = code; closeRuleForm(); renderRules(); refreshSuggestions(); scheduleSave();
}

// Mausrad darf <select>/Number-Inputs nicht ungewollt verstellen: beim Rad das
// Element die Fokus abgeben lassen, sodass nur die Seite scrollt.
function guardWheel() {
  var nodes = document.querySelectorAll("select, input[type=number]");
  for (var i = 0; i < nodes.length; i++) {
    nodes[i].addEventListener("wheel", function () {
      if (document.activeElement !== this) this.blur();
    });
  }
}

function bind() {
  el("sfxText").addEventListener("input", function () { refreshPreview(); refreshSuggestions(); });
  el("insertBtn").addEventListener("click", doInsert);
  var toggles = ["upper", "boldChk", "italicChk", "shadowChk"];
  for (var i = 0; i < toggles.length; i++) {
    el(toggles[i]).addEventListener("change", function () { readInputs(); refreshPreview(); scheduleSave(); });
  }
  var nums = ["size", "fill", "outline", "outlineW", "shadowColor", "shadowX", "shadowY"];
  for (var j = 0; j < nums.length; j++) {
    el(nums[j]).addEventListener("input", function () { readInputs(); updateSwatches(); refreshPreview(); scheduleSave(); });
  }
  el("fontSearch").addEventListener("input", buildFontList);
  el("fontList").addEventListener("change", function () { readInputs(); refreshPreview(); scheduleSave(); });
  el("savePreset").addEventListener("click", saveCurrentPreset);
  el("addRuleBtn").addEventListener("click", function () { openRuleForm(null); });
  el("ruleSave").addEventListener("click", saveRuleForm);
  el("ruleCancel").addEventListener("click", closeRuleForm);
  el("restoreBuiltins").addEventListener("click", restoreBuiltins);
  el("uiScale").addEventListener("input", function () {
    state.ui_scale = parseFloat(el("uiScale").value) || 100;
    applyScale(); scheduleSave();
  });
  try { CS.addEventListener("com.adobe.csxs.events.ThemeColorChanged", applyHostTheme); } catch (e) {}
  el("exportBtn").addEventListener("click", exportData);
  el("importBtn").addEventListener("click", importData);
  el("resetBtn").addEventListener("click", resetAll);
  el("uiLang").addEventListener("change", function (e) { setUiLang(e.target.value); });
  el("ruleLang").addEventListener("change", function (e) { setRuleLang(e.target.value); });
  window.addEventListener("resize", refreshPreview);
  guardWheel();
}

function afterStateLoaded() {
  buildSelect(el("uiLang"), I18N.LANGUAGES, I18N.LANGUAGE_NAMES, state.ui_lang);
  buildSelect(el("ruleLang"), RULES.RULE_LANGS, RULES.RULE_LANG_NAMES, state.rule_lang);
  applyI18n(); buildFontList(); writeInputs(); readInputs();
  renderPresets(); renderRules(); setupCollapsibles();
  el("uiScale").value = state.ui_scale || 100;
  applyScale(); buildSectionToggles(); applySectionVisibility(); applyHostTheme();
  refreshPreview(); refreshSuggestions();
}

function init() {
  state = STORE.loadState(DATA_FILE);
  bind();
  // Fonts asynchron aus Photoshop holen, dann UI aufbauen.
  CS.evalScript("sfxListFonts()", function (res) {
    fonts = [];
    if (res && res.indexOf("EvalScript") !== 0) {
      var lines = res.split("\n");
      for (var i = 0; i < lines.length; i++) {
        var parts = lines[i].split("\t");
        if (parts[0]) fonts.push({ name: parts[0], family: parts[0], postScriptName: parts[1] || "" });
      }
    }
    fonts.sort(function (a, b) { return (a.family || a.name).localeCompare(b.family || b.name); });
    afterStateLoaded();
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
