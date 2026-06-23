/* AUTO-COPIED from sfx-core/ by sync-core.py - edit the source there. */
/*
 * match.js – reine SFX-Logik (keine Photoshop-Abhängigkeit, mit Node testbar):
 * Normalisierung, Stichwort-Abgleich, Lautmuster-Heuristik und der komplette
 * Vorschlags-Builder (gelernt -> Regeln/Heuristik -> Preset). 1:1 aus der
 * Krita-Version (sfx_docker.py).
 */

const RUN_RE = /(.)\1+/g;                  // jede Wiederholung eines Zeichens

// "BOOOOM"->"bom", "gashaaan"->"gashan", "ka-boom!"->"kabom".
// Sonderfall: ein Wort aus nur EINEM wiederholten Zeichen ("zzz") behält 2.
function normalizeSfx(text) {
  const raw = String(text || "").toLowerCase().replace(/[^a-z0-9]+/g, "");
  let s = raw.replace(RUN_RE, "$1");
  if (s.length === 1 && raw.length >= 2) s = s + s;
  return s;
}

// <2 Zeichen Rest -> ignorieren; ==2 -> exakt (so matcht "ow" nicht in "pow");
// >=3 -> Teilstring (so matchen verdoppelte/gedehnte Formen wie "boom-boom").
function keywordMatches(keyword, textNorm) {
  const kw = normalizeSfx(keyword);
  if (kw.length < 2) return false;
  if (kw.length === 2) return textNorm === kw;
  return textNorm.indexOf(kw) !== -1;
}

// --- Lautmuster-Heuristik (Fallback für unbekannte SFX) --------------------
const HARD = new Set("bdgkpqt".split(""));
const SIB = new Set("fsz".split(""));
const NASAL = new Set("mn".split(""));
const LIQUID = new Set("lr".split(""));
const END_VOWEL_RE = /([aeiouy])\1{2,}$/;

function countSet(s, set) {
  let n = 0;
  for (const c of s) if (set.has(c)) n++;
  return n;
}
function occ(s, sub) {       // Anzahl (überlappungsfrei) von sub in s
  let n = 0, i = 0;
  while ((i = s.indexOf(sub, i)) !== -1) { n++; i += sub.length; }
  return n;
}

function classifySfx(word, available) {
  const raw = String(word || "").trim();
  const letters = raw.toLowerCase().replace(/[^a-z]/g, "");
  if (letters.length < 2) return [];
  const s = letters, n = s.length;
  const hard = countSet(s, HARD);
  const sib = countSet(s, SIB) + occ(s, "sh") + occ(s, "wh");
  const nasal = countSet(s, NASAL);
  const liquid = countSet(s, LIQUID);
  const z = occ(s, "z"), g = occ(s, "g"), rr = occ(s, "r");
  const caps = raw.toUpperCase() === raw && /[A-Z]/.test(raw) && n >= 2;
  const bang = raw.indexOf("!") !== -1;
  const onlyZ = /^z+$/.test(s);
  const endVowelRun = END_VOWEL_RE.test(s);

  const score = {};
  const add = (group, pts) => { if (pts > 0) score[group] = (score[group] || 0) + pts; };

  if (onlyZ) add("Breath / Sleep", 5);
  else if (z) add("Electric / Spark", 2 + z);
  if (hard >= 2) add("Boom / Explosion", hard + (caps ? 1 : 0) + (bang ? 1 : 0));
  if (hard >= 1 && n <= 5) add("Hit / Punch", hard + (caps ? 1 : 0));
  if (sib >= 1 && (s.indexOf("w") !== -1 || s.indexOf("f") !== -1 || occ(s, "sh")))
    add("Whoosh / Dash", sib + 1);
  if (endVowelRun) add("Scream / Shout", 3 + (caps ? 1 : 0) + (bang ? 1 : 0));
  if (g >= 1 && rr >= 1) add("Roar / Growl", g + rr + 1);
  if (occ(s, "sp") || occ(s, "dr") || occ(s, "pl") || occ(s, "bl") || occ(s, "gl"))
    add("Water / Liquid", 2);
  if (nasal + liquid >= 2 && hard === 0 && !caps && !bang)
    add("Whisper / Silence", nasal + liquid);
  if (bang && Object.keys(score).length === 0) add("Scream / Shout", 2);

  let ordered = Object.keys(score).map((grp) => [grp, score[grp]]);
  ordered.sort((a, b) => b[1] - a[1]);
  if (available) ordered = ordered.filter(([grp]) => available.has(grp));
  if (!ordered.length) return [];
  const top = ordered[0][1];
  return ordered.filter(([, p]) => p >= Math.max(2, top * 0.6))
                .slice(0, 2).map(([grp]) => grp);
}

// --- Regeln + Vorschläge ---------------------------------------------------

// Gruppenname -> Fonts (erste passende Regel) aus ALLEN Regeln; für die
// Heuristik bewusst sprachunabhängig.
function groupFonts(rules) {
  const map = {};
  for (const r of rules) if (!(r.group in map)) map[r.group] = r.fonts.slice();
  return map;
}

// Nur Regeln der aktiven Sprache plus die sprachübergreifenden "*"-Regeln.
function activeRules(rules, lang) {
  return rules.filter((r) => {
    const l = r.lang || "*";
    return l === "*" || l === lang;
  });
}

// [{group, fonts}] für Regeln, deren Stichwort im Text steckt; Gruppen mit
// einem EXAKTEN Worttreffer zuerst.
function suggestedGroups(rules, lang, textNorm) {
  if (!textNorm) return [];
  const result = [];          // [group, fonts[], exact]
  const index = {};
  for (const rule of activeRules(rules, lang)) {
    const matched = rule.keywords.filter((kw) => keywordMatches(kw, textNorm));
    if (!matched.length) continue;
    const exact = matched.some((kw) => normalizeSfx(kw) === textNorm);
    const g = rule.group || "";
    if (!(g in index)) { index[g] = result.length; result.push([g, [], exact]); }
    const entry = result[index[g]];
    entry[2] = entry[2] || exact;
    for (const f of rule.fonts) if (f && entry[1].indexOf(f) === -1) entry[1].push(f);
  }
  result.sort((a, b) => (a[2] ? 0 : 1) - (b[2] ? 0 : 1));   // stabil
  return result.map(([group, fonts]) => ({ group, fonts }));
}

function findMatchingPreset(presets, textNorm) {
  if (!textNorm) return null;
  for (const p of presets) {
    for (const kw of (p.keywords || [])) {
      if (keywordMatches(kw, textNorm)) return p;
    }
  }
  return null;
}

function learnedFonts(usage, textNorm) {
  if (!textNorm) return [];
  const d = (usage && usage[textNorm]) || {};
  return Object.keys(d).sort((a, b) => d[b] - d[a]);
}

/*
 * suggest(text, ctx) -> fertiges, gerendert-bereites Ergebnis:
 *   { guessed, header, learned:[font], groups:[{group,fonts}], preset|null }
 * Fonts werden gruppenübergreifend dedupliziert und auf `limit` begrenzt.
 * ctx = { rules, presets, lang, usage, limit }
 */
function suggest(text, ctx) {
  const rules = ctx.rules, presets = ctx.presets || [];
  const lang = ctx.lang || "en", usage = ctx.usage || {};
  const limit = ctx.limit || 8;
  const norm = normalizeSfx(text);

  const learnedAll = learnedFonts(usage, norm);
  let groups = suggestedGroups(rules, lang, norm);
  let guessed = false;
  if (!groups.length) {                       // keine Regel -> Heuristik
    const gf = groupFonts(rules);
    const avail = new Set(Object.keys(gf));
    groups = classifySfx(text, avail)
      .map((g) => ({ group: g, fonts: (gf[g] || []).slice() }))
      .filter((g) => g.fonts.length);
    guessed = groups.length > 0;
  }
  const preset = findMatchingPreset(presets, norm);

  // gemeinsam deduplizieren + begrenzen: zuerst gelernt, dann Gruppen
  const shown = new Set();
  let remaining = limit;
  const learned = [];
  for (const f of learnedAll) {
    if (remaining <= 0) break;
    if (shown.has(f)) continue;
    shown.add(f); remaining--; learned.push(f);
  }
  const outGroups = [];
  for (const g of groups) {
    if (remaining <= 0) break;
    const nf = g.fonts.filter((f) => !shown.has(f)).slice(0, remaining);
    if (!nf.length) continue;
    nf.forEach((f) => shown.add(f));
    remaining -= nf.length;
    outGroups.push({ group: g.group, fonts: nf });
  }
  return { guessed, learned, groups: outGroups, preset };
}

module.exports = {
  normalizeSfx, keywordMatches, classifySfx,
  groupFonts, activeRules, suggestedGroups, findMatchingPreset,
  learnedFonts, suggest,
};
