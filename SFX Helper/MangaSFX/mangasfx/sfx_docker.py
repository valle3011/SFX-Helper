# -*- coding: utf-8 -*-
"""
Manga SFX Typesetter – die eigentliche Docker-Klasse (UI + Logik).

Sprache: Standard Englisch, umschaltbar auf Deutsch (oben im Docker).
Komfort: Live-Vorschau, GROSSBUCHSTABEN-Schalter, merkt sich den zuletzt
genutzten Stil über Neustarts.
"""
import json

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QSpinBox, QSlider, QColorDialog, QScrollArea,
    QCompleter, QInputDialog, QMessageBox, QMenu, QCheckBox,
    QDialog, QDialogButtonBox, QFileDialog,
)
from PyQt5.QtGui import QColor, QFontDatabase, QFont
from PyQt5.QtCore import Qt

from krita import Krita, DockWidget

from .config import (
    SFX_FONTS, SFX_PRESETS, DEFAULTS, SHOW_ALL_SYSTEM_FONTS,
)
from .svg_builder import build_sfx_svg
from .presets_store import (
    load_user_presets, save_user_presets, load_font_rules, save_font_rules,
    load_language, save_language, load_settings, save_settings,
)
from .i18n import tr, LANGUAGES


class MangaSFXDocker(DockWidget):
    """Dockbares Panel zum schnellen Setzen von Manga-SFX."""

    def __init__(self):
        super().__init__()
        self._lang = load_language("en")          # Standard: Englisch
        self._user_presets = load_user_presets()  # eigene Presets (persistiert)
        self._font_rules = load_font_rules()      # Stichwort -> Font(s) (persistiert)
        self._pending_state = load_settings()     # zuletzt genutzter Stil
        self.setWindowTitle(self.t("window_title"))
        self._build_ui()

    # ------------------------------------------------------------------
    # Pflicht-Override der DockWidget-API (wird hier nicht gebraucht)
    # ------------------------------------------------------------------
    def canvasChanged(self, canvas):
        pass

    # ------------------------------------------------------------------
    # Übersetzungs-Kurzform
    # ------------------------------------------------------------------
    def t(self, key, **kw):
        return tr(self._lang, key, **kw)

    # ==================================================================
    #  UI-Aufbau (wird bei Sprachwechsel komplett neu aufgebaut)
    # ==================================================================
    def _build_ui(self):
        root = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        root.setLayout(layout)

        # --- Sprachauswahl --------------------------------------------
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel(self.t("lang_label") + ":"))
        self.lang_combo = QComboBox()
        for code, label in LANGUAGES:
            self.lang_combo.addItem(label, code)
        li = self.lang_combo.findData(self._lang)
        self.lang_combo.setCurrentIndex(li if li >= 0 else 0)
        # erst nach dem Setzen verbinden, sonst feuert es beim Aufbau
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(self.lang_combo, 1)
        layout.addLayout(lang_row)

        # --- 1) Texteingabe -------------------------------------------
        layout.addWidget(self._heading(self.t("sfx_text")))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText(self.t("sfx_placeholder"))
        self.text_input.returnPressed.connect(self._insert_sfx)  # Enter = einfügen
        layout.addWidget(self.text_input)

        # Schalter: GROSSBUCHSTABEN / Fett / Kursiv (2-spaltig, damit nichts
        # bei schmalem Docker abgeschnitten wird)
        opt_grid = QGridLayout()
        self.upper_chk = QCheckBox(self.t("uppercase"))
        self.upper_chk.setChecked(True)
        self.upper_chk.toggled.connect(self._on_upper_toggled)
        self.bold_chk = QCheckBox(self.t("bold"))
        self.bold_chk.toggled.connect(lambda _c: self._update_preview())
        self.italic_chk = QCheckBox(self.t("italic"))
        self.italic_chk.toggled.connect(lambda _c: self._update_preview())
        opt_grid.addWidget(self.upper_chk, 0, 0)
        opt_grid.addWidget(self.bold_chk, 0, 1)
        opt_grid.addWidget(self.italic_chk, 1, 0)
        opt_grid.setColumnStretch(2, 1)
        layout.addLayout(opt_grid)

        # --- Live-Vorschau --------------------------------------------
        layout.addWidget(self._heading(self.t("preview")))
        self.preview = QLabel("")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(56)
        layout.addWidget(self.preview)

        # --- Live-Vorschläge zum aktuellen SFX-Wort -------------------
        self.suggest_box = QVBoxLayout()
        self.suggest_box.setSpacing(3)
        layout.addLayout(self.suggest_box)
        # textChanged erst jetzt verbinden – suggest_box/preview müssen existieren
        self.text_input.textChanged.connect(self._on_text_changed)

        # --- 2) Font (Favoriten + alle System-Fonts, durchsuchbar) ----
        layout.addWidget(self._heading(self.t("font")))
        self.font_combo = self._build_font_combo()
        self.font_combo.currentTextChanged.connect(lambda _t: self._update_preview())
        layout.addWidget(self.font_combo)

        # --- 3) Schriftgröße ------------------------------------------
        self.size_slider, self.size_spin = self._slider_spin_row(
            layout, self.t("font_size"), 10, 600, DEFAULTS["size"])
        self.size_spin.valueChanged.connect(lambda _v: self._update_preview())

        # --- Füllfarbe ------------------------------------------------
        layout.addWidget(self._heading(self.t("fill_color")))
        self.fill_btn = QPushButton()
        self.fill_btn.setFixedHeight(26)
        self._set_btn_color(self.fill_btn, QColor(DEFAULTS["fill"]))
        self.fill_btn.clicked.connect(lambda: self._pick_color(self.fill_btn))
        layout.addWidget(self.fill_btn)

        # --- Outline-Farbe --------------------------------------------
        layout.addWidget(self._heading(self.t("outline_color")))
        self.outline_btn = QPushButton()
        self.outline_btn.setFixedHeight(26)
        self._set_btn_color(self.outline_btn, QColor(DEFAULTS["outline"]))
        self.outline_btn.clicked.connect(lambda: self._pick_color(self.outline_btn))
        layout.addWidget(self.outline_btn)

        # --- Outline-Stärke -------------------------------------------
        self.out_slider, self.out_spin = self._slider_spin_row(
            layout, self.t("outline_width"), 0, 60, DEFAULTS["outline_px"])

        # --- 4) Presets (integriert + selbst angelegte) ---------------
        layout.addWidget(self._heading(self.t("presets")))
        self.preset_box = QVBoxLayout()
        layout.addLayout(self.preset_box)
        self.save_preset_btn = QPushButton(self.t("save_preset_btn"))
        self.save_preset_btn.setToolTip(self.t("save_preset_tip"))
        self.save_preset_btn.clicked.connect(self._save_current_as_preset)
        layout.addWidget(self.save_preset_btn)
        self._rebuild_presets()

        # --- 4b) Font-Vorschläge verwalten (Stichwort -> Font(s)) -----
        layout.addWidget(self._heading(self.t("font_suggestions")))
        rules_hint = QLabel(self.t("rules_hint"))
        rules_hint.setWordWrap(True)
        layout.addWidget(rules_hint)
        self.rules_box = QVBoxLayout()
        self.rules_box.setSpacing(3)
        layout.addLayout(self.rules_box)
        self.add_rule_btn = QPushButton(self.t("add_rule_btn"))
        self.add_rule_btn.setToolTip(self.t("add_rule_tip"))
        self.add_rule_btn.clicked.connect(self._add_font_rule)
        layout.addWidget(self.add_rule_btn)
        self._rebuild_rules()

        # --- 5) Einfügen ----------------------------------------------
        self.insert_btn = QPushButton(self.t("insert_btn"))
        self.insert_btn.setMinimumHeight(34)
        self.insert_btn.clicked.connect(self._insert_sfx)
        layout.addWidget(self.insert_btn)

        # --- Status / Hinweise ----------------------------------------
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # --- Import / Export (eigene Presets + Font-Regeln) -----------
        io_row = QHBoxLayout()
        self.import_btn = QPushButton(self.t("import_btn"))
        self.import_btn.clicked.connect(self._import_data)
        self.export_btn = QPushButton(self.t("export_btn"))
        self.export_btn.clicked.connect(self._export_data)
        io_row.addWidget(self.import_btn)
        io_row.addWidget(self.export_btn)
        layout.addLayout(io_row)

        # --- Zurücksetzen ---------------------------------------------
        self.reset_btn = QPushButton(self.t("reset_btn"))
        self.reset_btn.setToolTip(self.t("reset_tip"))
        self.reset_btn.clicked.connect(self._reset)
        layout.addWidget(self.reset_btn)

        layout.addStretch(1)

        # In ScrollArea verpacken; alte (bei Sprachwechsel) sauber entsorgen
        old = self.widget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(root)
        self.setWidget(scroll)
        if old is not None:
            old.setParent(None)
            old.deleteLater()

        # zuletzt genutzten / vor dem Sprachwechsel gemerkten Stil anwenden
        self._apply_state(self._pending_state)
        self._update_preview()

    # ==================================================================
    #  Sprache
    # ==================================================================
    def _on_lang_changed(self, _idx):
        code = self.lang_combo.currentData()
        if code and code != self._lang:
            self._set_language(code)

    def _set_language(self, lang):
        self._pending_state = self._capture_state()   # Eingaben nicht verlieren
        self._lang = lang
        save_language(lang)
        self.setWindowTitle(self.t("window_title"))
        self._build_ui()                               # komplett neu in neuer Sprache

    # ==================================================================
    #  kleine UI-Helfer
    # ==================================================================
    def _heading(self, text):
        lbl = QLabel(text)
        f = lbl.font()
        f.setBold(True)
        lbl.setFont(f)
        return lbl

    def _slider_spin_row(self, parent_layout, title, lo, hi, value):
        """Erzeugt 'Überschrift + Slider + SpinBox' und synchronisiert beide."""
        parent_layout.addWidget(self._heading(title))
        row = QHBoxLayout()
        slider = QSlider(Qt.Horizontal)
        slider.setRange(lo, hi)
        slider.setValue(value)
        spin = QSpinBox()
        spin.setRange(lo, hi)
        spin.setValue(value)
        slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(slider.setValue)
        row.addWidget(slider, 1)
        row.addWidget(spin, 0)
        parent_layout.addLayout(row)
        return slider, spin

    def _set_btn_color(self, btn, qcolor):
        """Färbt einen Button als Farb-Swatch und schreibt den Hexcode drauf."""
        btn._color = qcolor
        txt = "#000000" if qcolor.lightness() > 128 else "#ffffff"
        btn.setText(qcolor.name())
        btn.setStyleSheet(
            f"background-color: {qcolor.name()}; color: {txt};"
            f" border: 1px solid #555; padding: 3px;")

    def _pick_color(self, btn):
        c = QColorDialog.getColor(btn._color, self.widget(), self.t("choose_color"))
        if c.isValid():
            self._set_btn_color(btn, c)
            self._update_preview()

    # --- Vorschau / Großbuchstaben ------------------------------------
    def _effective_text(self):
        """Der Text, der wirklich eingefügt wird (ggf. in Großbuchstaben)."""
        txt = self.text_input.text().strip()
        if getattr(self, "upper_chk", None) and self.upper_chk.isChecked():
            txt = txt.upper()
        return txt

    def _on_upper_toggled(self, _checked):
        self._update_preview()

    def _update_preview(self):
        """Zeigt das Wort in gewähltem Font + Füllfarbe (ohne Outline)."""
        if not all(hasattr(self, a) for a in
                   ("preview", "font_combo", "size_spin", "fill_btn")):
            return
        text = self._effective_text() or "Aa"
        font = QFont(self.font_combo.currentText())
        font.setPointSize(max(10, min(44, int(self.size_spin.value() / 3))))
        if hasattr(self, "bold_chk"):
            font.setBold(self.bold_chk.isChecked())
        if hasattr(self, "italic_chk"):
            font.setItalic(self.italic_chk.isChecked())
        self.preview.setFont(font)
        self.preview.setText(text)
        self.preview.setStyleSheet(
            f"color: {self.fill_btn._color.name()}; background: #9a9a9a;"
            " border: 1px solid #555; border-radius: 3px; padding: 6px;")

    # --- Stand sichern / wiederherstellen -----------------------------
    def _capture_state(self):
        return {
            "text": self.text_input.text(),
            "font": self.font_combo.currentText(),
            "size": self.size_spin.value(),
            "fill": self.fill_btn._color.name(),
            "outline": self.outline_btn._color.name(),
            "outline_px": self.out_spin.value(),
            "uppercase": self.upper_chk.isChecked(),
            "bold": self.bold_chk.isChecked(),
            "italic": self.italic_chk.isChecked(),
        }

    def _apply_state(self, st):
        if not st:
            return
        if st.get("text"):
            self.text_input.setText(st["text"])
        if st.get("font"):
            self._select_font(st["font"])
        for key, spin in (("size", self.size_spin), ("outline_px", self.out_spin)):
            if key in st:
                try:
                    spin.setValue(int(st[key]))
                except (TypeError, ValueError):
                    pass
        if st.get("fill"):
            self._set_btn_color(self.fill_btn, QColor(st["fill"]))
        if st.get("outline"):
            self._set_btn_color(self.outline_btn, QColor(st["outline"]))
        if "uppercase" in st:
            self.upper_chk.setChecked(bool(st["uppercase"]))
        if "bold" in st:
            self.bold_chk.setChecked(bool(st["bold"]))
        if "italic" in st:
            self.italic_chk.setChecked(bool(st["italic"]))

    def _preset_tooltip(self, p):
        lines = [
            self.t("tip_font", v=p["font"]),
            self.t("tip_size", v=p["size"]),
            self.t("tip_fill", v=p["fill"]),
            self.t("tip_outline", c=p["outline"], w=p["outline_px"]),
        ]
        kws = p.get("keywords") or []
        if kws:
            lines.append(self.t("tip_keywords", v=", ".join(kws)))
        lines.append(self.t("tip_user_preset") if p.get("user")
                     else self.t("tip_builtin"))
        return "\n".join(lines)

    # ==================================================================
    #  Presets
    # ==================================================================
    def _apply_preset(self, preset):
        self._select_font(preset["font"])
        self.size_spin.setValue(preset["size"])
        self.out_spin.setValue(preset["outline_px"])
        self._set_btn_color(self.fill_btn, QColor(preset["fill"]))
        self._set_btn_color(self.outline_btn, QColor(preset["outline"]))
        self.bold_chk.setChecked(bool(preset.get("bold", False)))
        self.italic_chk.setChecked(bool(preset.get("italic", False)))
        self._update_preview()
        self.status_label.setText(self.t("st_preset_loaded", name=preset["name"]))

    def _all_presets(self):
        """Integrierte Presets (aus config.py) + eigene (persistiert)."""
        builtin = [dict(p, user=False) for p in SFX_PRESETS]
        return builtin + self._user_presets

    def _rebuild_presets(self):
        """Baut die Preset-Buttons neu auf (nach Anlegen/Löschen aufrufen)."""
        self._clear_layout(self.preset_box)
        grid = QGridLayout()
        grid.setSpacing(4)
        for i, preset in enumerate(self._all_presets()):
            btn = QPushButton(preset["name"])
            btn.setToolTip(self._preset_tooltip(preset))
            btn.clicked.connect(lambda _c=False, p=preset: self._apply_preset(p))
            if preset.get("user"):
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(
                    lambda pos, p=preset, b=btn: self._show_preset_menu(p, b, pos))
            grid.addWidget(btn, i // 2, i % 2)
        self.preset_box.addLayout(grid)

    def _clear_layout(self, layout):
        """Entfernt alle Widgets/Unterlayouts aus einem Layout."""
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            else:
                child = item.layout()
                if child is not None:
                    self._clear_layout(child)

    def _current_settings_as_preset(self, name, keywords):
        """Liest die aktuellen Regler aus und baut daraus ein Preset-Dict."""
        return {
            "name": name,
            "font": self.font_combo.currentText(),
            "size": self.size_spin.value(),
            "fill": self.fill_btn._color.name(),
            "outline": self.outline_btn._color.name(),
            "outline_px": self.out_spin.value(),
            "bold": self.bold_chk.isChecked(),
            "italic": self.italic_chk.isChecked(),
            "keywords": keywords,
            "user": True,
        }

    def _save_current_as_preset(self):
        """Fragt Name (+ optionale Schlüsselwörter) ab und speichert das Preset."""
        name, ok = QInputDialog.getText(
            self.widget(), self.t("dlg_save_title"), self.t("dlg_save_name"))
        if not ok:
            return
        name = name.strip()
        if not name:
            self._warn(self.t("warn_no_name"))
            return

        kw_text, ok2 = QInputDialog.getText(
            self.widget(), self.t("dlg_kw_opt_title"), self.t("dlg_kw_opt_label"))
        keywords = []
        if ok2 and kw_text.strip():
            keywords = [k.strip().lower() for k in kw_text.split(",") if k.strip()]

        preset = self._current_settings_as_preset(name, keywords)
        self._user_presets = [p for p in self._user_presets
                              if p.get("name") != name]
        self._user_presets.append(preset)
        save_user_presets(self._user_presets)
        self._rebuild_presets()
        self.status_label.setText(self.t("st_preset_saved", name=name))

    def _show_preset_menu(self, preset, button, pos):
        """Kontextmenü für ein eigenes Preset (Rechtsklick)."""
        menu = QMenu(self.widget())
        act_rename = menu.addAction(self.t("menu_rename"))
        act_keywords = menu.addAction(self.t("menu_edit_keywords"))
        act_overwrite = menu.addAction(self.t("menu_overwrite"))
        menu.addSeparator()
        act_delete = menu.addAction(self.t("menu_delete"))

        chosen = menu.exec_(button.mapToGlobal(pos))
        if chosen is None:
            return
        if chosen == act_rename:
            self._rename_user_preset(preset)
        elif chosen == act_keywords:
            self._edit_keywords(preset)
        elif chosen == act_overwrite:
            self._overwrite_user_preset(preset)
        elif chosen == act_delete:
            self._delete_user_preset(preset)

    def _rename_user_preset(self, preset):
        old = preset.get("name", "")
        new, ok = QInputDialog.getText(
            self.widget(), self.t("dlg_rename_title"), self.t("dlg_rename_label"),
            text=old)
        if not ok:
            return
        new = new.strip()
        if not new:
            self._warn(self.t("warn_no_name"))
            return
        if new == old:
            return
        if any(p is not preset and p.get("name") == new for p in self._user_presets):
            self._warn(self.t("warn_name_exists", name=new))
            return
        preset["name"] = new
        save_user_presets(self._user_presets)
        self._rebuild_presets()
        self.status_label.setText(self.t("st_preset_renamed", name=new))

    def _edit_keywords(self, preset):
        current = ", ".join(preset.get("keywords", []))
        txt, ok = QInputDialog.getText(
            self.widget(), self.t("dlg_editkw_title"), self.t("dlg_editkw_label"),
            text=current)
        if not ok:
            return
        preset["keywords"] = [k.strip().lower() for k in txt.split(",") if k.strip()]
        save_user_presets(self._user_presets)
        self._rebuild_presets()
        self._on_text_changed(self.text_input.text())
        self.status_label.setText(self.t("st_keywords_updated", name=preset["name"]))

    def _overwrite_user_preset(self, preset):
        reply = QMessageBox.question(
            self.widget(), self.t("dlg_overwrite_title"),
            self.t("dlg_overwrite_q", name=preset["name"]),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        preset["font"] = self.font_combo.currentText()
        preset["size"] = self.size_spin.value()
        preset["fill"] = self.fill_btn._color.name()
        preset["outline"] = self.outline_btn._color.name()
        preset["outline_px"] = self.out_spin.value()
        preset["bold"] = self.bold_chk.isChecked()
        preset["italic"] = self.italic_chk.isChecked()
        save_user_presets(self._user_presets)
        self._rebuild_presets()
        self.status_label.setText(self.t("st_preset_overwritten", name=preset["name"]))

    def _delete_user_preset(self, preset):
        name = preset.get("name", "")
        reply = QMessageBox.question(
            self.widget(), self.t("dlg_delpreset_title"),
            self.t("dlg_delpreset_q", name=name),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        self._user_presets = [p for p in self._user_presets if p is not preset]
        save_user_presets(self._user_presets)
        self._rebuild_presets()
        self.status_label.setText(self.t("st_preset_deleted", name=name))

    # ==================================================================
    #  Font-Dropdown
    # ==================================================================
    def _build_font_combo(self):
        """Dropdown mit Favoriten + allen System-Fonts, durchsuchbar."""
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.NoInsert)

        combo.addItems(SFX_FONTS)
        if SHOW_ALL_SYSTEM_FONTS:
            families = QFontDatabase().families()
            if families:
                combo.insertSeparator(combo.count())
                combo.addItems(families)

        completer = combo.completer()
        if completer is not None:
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)

        combo.setCurrentIndex(0)
        return combo

    def _select_font(self, font_name):
        """Wählt den Font im Dropdown; bei editierbarem Feld notfalls als Text."""
        idx = self.font_combo.findText(font_name)
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        else:
            self.font_combo.setCurrentText(font_name)

    # ==================================================================
    #  Live-Vorschläge
    # ==================================================================
    def _on_text_changed(self, txt):
        self._refresh_suggestions(txt)
        self._update_preview()

    def _refresh_suggestions(self, text):
        """Baut die Vorschlagszeile neu: passende Fonts (nach Gruppen) + Preset."""
        self._clear_layout(self.suggest_box)
        groups = self._suggested_groups(text)
        preset = self._find_matching_preset(text)
        if not groups and preset is None:
            return

        info = QLabel(self.t("suggestions"))
        info.setWordWrap(True)
        self.suggest_box.addWidget(info)

        for group, fonts in groups:
            if group:                       # Gruppen-Überschrift (z. B. "Shout")
                self.suggest_box.addWidget(self._mini_heading(group))
            for fnt in fonts:
                btn = QPushButton(self.t("sug_font", name=fnt))
                btn.setToolTip(self.t("sug_font_tip", name=fnt))
                btn.clicked.connect(lambda _c=False, ff=fnt: self._select_font(ff))
                self.suggest_box.addWidget(btn)

        if preset is not None:
            btn = QPushButton(self.t("sug_preset", name=preset["name"],
                                     font=preset["font"]))
            btn.setToolTip(self.t("sug_preset_tip"))
            btn.clicked.connect(lambda _c=False, p=preset: self._apply_preset(p))
            self.suggest_box.addWidget(btn)

    def _suggested_groups(self, text):
        """[(group, [fonts]), ...] für Regeln, deren Stichwort im Text vorkommt."""
        low = text.lower()
        if not low:
            return []
        result = []
        index = {}
        for rule in self._font_rules:
            if not any(kw and kw.lower() in low for kw in rule.get("keywords", [])):
                continue
            g = rule.get("group") or ""
            if g not in index:
                index[g] = len(result)
                result.append((g, []))
            bucket = result[index[g]][1]
            for f in rule.get("fonts", []):
                if f and f not in bucket:
                    bucket.append(f)
        return result

    def _mini_heading(self, text):
        """Kleine, fette Zwischenüberschrift (für Gruppen)."""
        lbl = QLabel(text)
        f = lbl.font()
        f.setBold(True)
        lbl.setFont(f)
        return lbl

    def _find_matching_preset(self, text):
        """Erstes Preset, dessen Schlüsselwort im Text vorkommt (oder None)."""
        low = text.lower()
        if not low:
            return None
        for preset in self._all_presets():
            for kw in preset.get("keywords", []):
                if kw and kw.lower() in low:
                    return preset
        return None

    # ==================================================================
    #  Font-Vorschläge (Stichwort -> Font(s)), im Docker verwaltbar
    # ==================================================================
    def _rebuild_rules(self):
        """Baut die Regel-Buttons neu auf, nach Gruppen sortiert."""
        self._clear_layout(self.rules_box)
        if not self._font_rules:
            hint = QLabel(self.t("no_rules"))
            hint.setWordWrap(True)
            self.rules_box.addWidget(hint)
            return
        for group in self._ordered_groups():
            self.rules_box.addWidget(
                self._mini_heading(group if group else self.t("group_none")))
            for rule in self._font_rules:
                if (rule.get("group") or "") != group:
                    continue
                kw = ", ".join(rule.get("keywords", []))
                fo = ", ".join(rule.get("fonts", []))
                btn = QPushButton(f"{kw}  →  {fo}")
                btn.setToolTip(self.t("rule_tip"))
                btn.clicked.connect(lambda _c=False, r=rule: self._edit_font_rule(r))
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(
                    lambda pos, r=rule, b=btn: self._show_rule_menu(r, b, pos))
                self.rules_box.addWidget(btn)

    def _ordered_groups(self):
        """Gruppen in Reihenfolge des ersten Auftretens; 'ohne Gruppe' ans Ende."""
        order = []
        has_empty = False
        for r in self._font_rules:
            g = r.get("group") or ""
            if g == "":
                has_empty = True
            elif g not in order:
                order.append(g)
        if has_empty:
            order.append("")
        return order

    def _existing_groups(self):
        """Vorhandene (nicht-leere) Gruppennamen – für die Auswahl im Dialog."""
        seen = []
        for r in self._font_rules:
            g = (r.get("group") or "").strip()
            if g and g not in seen:
                seen.append(g)
        return seen

    def _show_rule_menu(self, rule, button, pos):
        menu = QMenu(self.widget())
        act_edit = menu.addAction(self.t("menu_edit"))
        menu.addSeparator()
        act_del = menu.addAction(self.t("menu_delete"))
        chosen = menu.exec_(button.mapToGlobal(pos))
        if chosen == act_edit:
            self._edit_font_rule(rule)
        elif chosen == act_del:
            self._delete_font_rule(rule)

    def _ask_fonts(self, fonts_init):
        """
        Dialog zum Auswählen der Font(s) für eine Regel.

        Bietet ein durchsuchbares Dropdown ALLER Fonts (Namen nachschlagen!)
        + 'Hinzufügen'-Knopf, der den gewählten Font an die Liste anhängt.
        Die Liste bleibt frei editierbar, also auch mehrere Fonts per Hand
        möglich. Rückgabe: Komma-String oder None bei Abbruch.
        """
        dlg = QDialog(self.widget())
        dlg.setWindowTitle(self.t("dlg_rule_fonts_title"))
        lay = QVBoxLayout(dlg)
        lbl = QLabel(self.t("dlg_rule_fonts_label"))
        lbl.setWordWrap(True)
        lay.addWidget(lbl)

        # Durchsuchbares Dropdown aller Fonts + Hinzufügen-Knopf
        pick_row = QHBoxLayout()
        combo = self._build_font_combo()
        pick_row.addWidget(combo, 1)
        add_btn = QPushButton(self.t("add_font_btn"))
        pick_row.addWidget(add_btn, 0)
        lay.addLayout(pick_row)

        # frei editierbare, Komma-getrennte Liste (mehrere Fonts möglich)
        line = QLineEdit(fonts_init)
        lay.addWidget(line)

        def add_current():
            name = combo.currentText().strip()
            if not name:
                return
            existing = [f.strip() for f in line.text().split(",") if f.strip()]
            if name not in existing:
                existing.append(name)
            line.setText(", ".join(existing))

        add_btn.clicked.connect(add_current)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(dlg.accept)
        bb.rejected.connect(dlg.reject)
        lay.addWidget(bb)

        if dlg.exec_() != QDialog.Accepted:
            return None
        return line.text()

    def _prompt_font_rule(self, group_init, kw_init, fonts_init):
        """Fragt Gruppe + Stichwörter + Fonts ab; (group, keywords, fonts) oder None."""
        # Gruppe: vorhandene Gruppen zur Auswahl, editierbar (neue eintippbar)
        items = list(self._existing_groups())
        if group_init and group_init not in items:
            items.insert(0, group_init)
        if not items:
            items = [""]
        current = items.index(group_init) if group_init in items else 0
        group, ok = QInputDialog.getItem(
            self.widget(), self.t("dlg_rule_group_title"),
            self.t("dlg_rule_group_label"), items, current, True)
        if not ok:
            return None
        group = group.strip()

        kw_text, ok2 = QInputDialog.getText(
            self.widget(), self.t("dlg_rule_kw_title"), self.t("dlg_rule_kw_label"),
            text=kw_init)
        if not ok2:
            return None
        keywords = [k.strip().lower() for k in kw_text.split(",") if k.strip()]
        if not keywords:
            self._warn(self.t("warn_no_keyword"))
            return None

        fonts_text = self._ask_fonts(fonts_init)
        if fonts_text is None:
            return None
        fonts = [f.strip() for f in fonts_text.split(",") if f.strip()]
        if not fonts:
            self._warn(self.t("warn_no_font"))
            return None
        return group, keywords, fonts

    def _add_font_rule(self):
        res = self._prompt_font_rule("", "", self.font_combo.currentText())
        if res is None:
            return
        group, keywords, fonts = res
        self._font_rules.append(
            {"group": group, "keywords": keywords, "fonts": fonts})
        save_font_rules(self._font_rules)
        self._rebuild_rules()
        self._refresh_suggestions(self.text_input.text())
        self.status_label.setText(self.t("st_rule_added"))

    def _edit_font_rule(self, rule):
        res = self._prompt_font_rule(
            rule.get("group", ""),
            ", ".join(rule.get("keywords", [])),
            ", ".join(rule.get("fonts", [])))
        if res is None:
            return
        rule["group"], rule["keywords"], rule["fonts"] = res
        save_font_rules(self._font_rules)
        self._rebuild_rules()
        self._refresh_suggestions(self.text_input.text())
        self.status_label.setText(self.t("st_rule_updated"))

    def _delete_font_rule(self, rule):
        reply = QMessageBox.question(
            self.widget(), self.t("dlg_delrule_title"), self.t("dlg_delrule_q"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        self._font_rules = [r for r in self._font_rules if r is not rule]
        save_font_rules(self._font_rules)
        self._rebuild_rules()
        self._refresh_suggestions(self.text_input.text())
        self.status_label.setText(self.t("st_rule_deleted"))

    # ==================================================================
    #  Kern: SFX einfügen
    # ==================================================================
    def _insert_sfx(self):
        doc = Krita.instance().activeDocument()
        if doc is None:
            self._warn(self.t("st_no_doc"))
            return

        text = self._effective_text()
        if not text:
            self._warn(self.t("st_no_text"))
            return

        # Aktive Ebene prüfen – ist es keine Vektor-Ebene, neue anlegen.
        node = doc.activeNode()
        created = False
        if node is None or node.type() != "vectorlayer":
            node = doc.createVectorLayer("SFX")
            rootnode = doc.rootNode()
            children = rootnode.childNodes()
            above = children[-1] if children else None   # möglichst ganz oben
            rootnode.addChildNode(node, above)
            doc.setActiveNode(node)
            created = True

        svg = build_sfx_svg(
            text=text,
            font_family=self.font_combo.currentText(),
            font_size=self.size_spin.value(),
            fill=self.fill_btn._color.name(),
            outline=self.outline_btn._color.name(),
            outline_px=self.out_spin.value(),
            bold=self.bold_chk.isChecked(),
            italic=self.italic_chk.isChecked(),
        )

        try:
            ok = node.addShapesFromSvg(svg)
        except Exception as e:                      # noqa: BLE001
            self._warn(self.t("st_insert_fail", err=e))
            return
        doc.refreshProjection()

        if ok is False:
            self._warn(self.t("st_svg_fail"))
            return

        # zuletzt genutzten Stil merken (ohne den Text selbst)
        style = self._capture_state()
        style.pop("text", None)
        save_settings(style)

        self.status_label.setText(
            self.t("st_layer_created") if created else self.t("st_inserted"))

    # ==================================================================
    #  Zurücksetzen
    # ==================================================================
    def _reset(self):
        """Zurücksetzen – wahlweise nur Stil oder alles (Presets + Regeln)."""
        box = QMessageBox(self.widget())
        box.setWindowTitle(self.t("reset_title"))
        box.setText(self.t("reset_q"))
        btn_style = box.addButton(self.t("reset_style"), QMessageBox.AcceptRole)
        btn_all = box.addButton(self.t("reset_all"), QMessageBox.DestructiveRole)
        box.addButton(self.t("cancel"), QMessageBox.RejectRole)
        box.setDefaultButton(btn_style)
        box.exec_()
        clicked = box.clickedButton()

        if clicked is btn_all:
            self._user_presets = []
            self._font_rules = []
            save_user_presets(self._user_presets)
            save_font_rules(self._font_rules)
            self._rebuild_presets()
            self._rebuild_rules()
            msg = self.t("st_reset_all")
        elif clicked is btn_style:
            msg = self.t("st_reset_style")
        else:
            return  # Abbrechen

        self._reset_style_to_defaults()
        save_settings({})                 # gemerkten Stil verwerfen
        self.status_label.setText(msg)

    def _reset_style_to_defaults(self):
        """Setzt Font/Größe/Farben/Outline/Großschreibung auf die Startwerte."""
        if SFX_FONTS:
            self._select_font(SFX_FONTS[0])
        else:
            self.font_combo.setCurrentIndex(0)
        self.size_spin.setValue(DEFAULTS["size"])
        self.out_spin.setValue(DEFAULTS["outline_px"])
        self._set_btn_color(self.fill_btn, QColor(DEFAULTS["fill"]))
        self._set_btn_color(self.outline_btn, QColor(DEFAULTS["outline"]))
        self.upper_chk.setChecked(True)
        self.bold_chk.setChecked(False)
        self.italic_chk.setChecked(False)
        self.text_input.clear()
        self._update_preview()

    def _warn(self, msg):
        self.status_label.setText("⚠ " + msg)

    # ==================================================================
    #  Import / Export (eigene Presets + Font-Regeln)
    # ==================================================================
    def _export_data(self):
        """Schreibt eigene Presets + Font-Regeln in eine .json-Datei."""
        path, _flt = QFileDialog.getSaveFileName(
            self.widget(), self.t("export_title"),
            "manga_sfx_presets.json", "JSON (*.json)")
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        data = {
            "manga_sfx": 1,
            "presets": self._user_presets,
            "font_rules": self._font_rules,
        }
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
        except OSError as e:                        # noqa: BLE001
            self._warn(self.t("st_export_fail", err=e))
            return
        self.status_label.setText(self.t(
            "st_exported", p=len(self._user_presets), r=len(self._font_rules)))

    def _import_data(self):
        """Liest Presets + Regeln aus einer .json-Datei (Zusammenführen/Ersetzen)."""
        path, _flt = QFileDialog.getOpenFileName(
            self.widget(), self.t("import_title"), "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as e:          # noqa: BLE001
            self._warn(self.t("st_import_fail", err=e))
            return
        if not isinstance(data, dict):
            self._warn(self.t("st_import_bad"))
            return

        presets = self._sanitize_presets(data.get("presets", []))
        rules = self._sanitize_rules(data.get("font_rules", []))
        if not presets and not rules:
            self._warn(self.t("st_import_empty"))
            return

        # Zusammenführen oder ersetzen?
        box = QMessageBox(self.widget())
        box.setWindowTitle(self.t("import_title"))
        box.setText(self.t("import_q", p=len(presets), r=len(rules)))
        btn_merge = box.addButton(self.t("import_merge"), QMessageBox.AcceptRole)
        btn_replace = box.addButton(self.t("import_replace"),
                                    QMessageBox.DestructiveRole)
        box.addButton(self.t("cancel"), QMessageBox.RejectRole)
        box.setDefaultButton(btn_merge)
        box.exec_()
        clicked = box.clickedButton()

        if clicked is btn_replace:
            self._user_presets = presets
            self._font_rules = rules
        elif clicked is btn_merge:
            self._merge_presets(presets)
            self._merge_rules(rules)
        else:
            return  # Abbrechen

        save_user_presets(self._user_presets)
        save_font_rules(self._font_rules)
        self._rebuild_presets()
        self._rebuild_rules()
        self._refresh_suggestions(self.text_input.text())
        self.status_label.setText(self.t(
            "st_imported", p=len(presets), r=len(rules)))

    # --- Hilfen für den Import ----------------------------------------
    def _as_int(self, value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _sanitize_presets(self, raw):
        """Macht importierte Presets robust (fehlende Felder auffüllen)."""
        out = []
        if not isinstance(raw, list):
            return out
        for p in raw:
            if not isinstance(p, dict) or not p.get("name"):
                continue
            kws = p.get("keywords", [])
            out.append({
                "name": str(p.get("name", "")).strip(),
                "font": str(p.get("font", "")),
                "size": self._as_int(p.get("size"), DEFAULTS["size"]),
                "fill": str(p.get("fill", DEFAULTS["fill"])),
                "outline": str(p.get("outline", DEFAULTS["outline"])),
                "outline_px": self._as_int(p.get("outline_px"),
                                           DEFAULTS["outline_px"]),
                "bold": bool(p.get("bold", False)),
                "italic": bool(p.get("italic", False)),
                "keywords": ([str(k).strip().lower() for k in kws if str(k).strip()]
                             if isinstance(kws, list) else []),
                "user": True,
            })
        return out

    def _sanitize_rules(self, raw):
        """Macht importierte Font-Regeln robust; verwirft unvollständige."""
        out = []
        if not isinstance(raw, list):
            return out
        for r in raw:
            if not isinstance(r, dict):
                continue
            kws = r.get("keywords", [])
            fonts = r.get("fonts", [])
            if not isinstance(kws, list) or not isinstance(fonts, list):
                continue
            keywords = [str(k).strip().lower() for k in kws if str(k).strip()]
            fontlist = [str(f).strip() for f in fonts if str(f).strip()]
            if not keywords or not fontlist:
                continue
            out.append({
                "group": str(r.get("group", "")).strip(),
                "keywords": keywords,
                "fonts": fontlist,
            })
        return out

    def _merge_presets(self, imported):
        """Fügt importierte Presets hinzu; gleicher Name ersetzt das alte."""
        names = {p["name"] for p in imported}
        self._user_presets = [p for p in self._user_presets
                              if p.get("name") not in names]
        self._user_presets.extend(imported)

    def _merge_rules(self, imported):
        """Fügt importierte Regeln hinzu, ohne exakte Duplikate."""
        def sig(r):
            return ((r.get("group") or ""),
                    tuple(r.get("keywords", [])),
                    tuple(r.get("fonts", [])))
        existing = {sig(r) for r in self._font_rules}
        for r in imported:
            if sig(r) not in existing:
                self._font_rules.append(r)
                existing.add(sig(r))
