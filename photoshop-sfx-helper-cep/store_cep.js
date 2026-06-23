/*
 * store_cep.js – plattformSPEZIFISCHE Persistenz für CEP über Node-fs. Die reine
 * Logik (Standardzustand, migrate, sanitizeRules, mergeFontRules, Lernen) kommt
 * aus dem GETEILTEN Kern core/store_core.js (identisch zur UXP-Version).
 *
 * loadState/saveState bekommen den Dateipfad vom Panel (im User-Data-Ordner).
 */
var core = require("./core/store_core");
var fs = require("fs");

function loadState(file) {
  try {
    return core.migrate(JSON.parse(fs.readFileSync(file, "utf8")));
  } catch (e) {
    return core.defaultState();
  }
}

function saveState(file, state) {
  try {
    fs.writeFileSync(file, JSON.stringify(state, null, 2), "utf8");
    return true;
  } catch (e) {
    return false;
  }
}

// Kern + IO re-exportieren, wie bei der UXP-store.js.
var out = { loadState: loadState, saveState: saveState };
for (var k in core) { if (core.hasOwnProperty(k)) out[k] = core[k]; }
module.exports = out;
