/*
 * CSInterface.js – schlanke Variante der Adobe-CEP-Bibliothek (nur das, was der
 * SFX Helper braucht: evalScript ins ExtendScript, Systempfade, App-ID). Adobes
 * Original ist umfangreicher; bei Bedarf die offizielle CSInterface.js von
 * Adobe-CEP/CEP-Resources einsetzen – die API hier ist namensgleich.
 */

var SystemPath = {
  USER_DATA: "userData",
  COMMON_FILES: "commonFiles",
  MY_DOCUMENTS: "myDocuments",
  APPLICATION: "application",
  EXTENSION: "extension",
  HOST_APPLICATION: "hostApplication",
};

function CSInterface() {}

// ExtendScript ausführen; Ergebnis (String) kommt im Callback zurück.
CSInterface.prototype.evalScript = function (script, callback) {
  if (callback === null || callback === undefined) callback = function () {};
  if (typeof window !== "undefined" && window.__adobe_cep__) {
    window.__adobe_cep__.evalScript(script, callback);
  } else {
    callback("EvalScript error: no CEP host");
  }
};

CSInterface.prototype.getApplicationID = function () {
  try {
    var hostEnv = JSON.parse(window.__adobe_cep__.getHostEnvironment());
    return hostEnv.appName;
  } catch (e) { return ""; }
};

CSInterface.prototype.getHostEnvironment = function () {
  try { return JSON.parse(window.__adobe_cep__.getHostEnvironment()); }
  catch (e) { return {}; }
};

// Systempfad holen und in einen normalen Dateipfad umwandeln (file:// + URI weg).
CSInterface.prototype.getSystemPath = function (pathType) {
  if (!(window && window.__adobe_cep__)) return "";
  var path = decodeURI(window.__adobe_cep__.getSystemPath(pathType));
  var OSVersion = (window.navigator && window.navigator.platform) || "";
  if (OSVersion.indexOf("Win") >= 0) {
    path = path.replace("file:///", "");
  } else {
    path = path.replace("file://", "");
  }
  return path;
};

CSInterface.prototype.addEventListener = function (type, listener, obj) {
  if (window && window.__adobe_cep__) {
    window.__adobe_cep__.addEventListener(type, listener, obj);
  }
};

CSInterface.prototype.requestOpenExtension = function () {};

if (typeof module !== "undefined" && module.exports) {
  module.exports = { CSInterface: CSInterface, SystemPath: SystemPath };
}
