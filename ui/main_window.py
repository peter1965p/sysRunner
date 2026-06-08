"""
SysRunner – main_window.py  v2
Norton Commander / Midnight Commander Style
──────────────────────────────────────────────────────────────
NEU:
  • Echte eingebettete Terminal-Konsole (QProcess / bash)
  • Drag & Drop zwischen Panels  (Shift = verschieben)
  • Vollständige F1–F10 Funktionen
  • Rechtsklick-Kontextmenü
  • Umbenennen, Ordner erstellen, Löschen, Kopieren, Verschieben
  • Pfad-History mit Pfeil-rauf / -runter im Terminal
  • Eigenschaften-Dialog
"""

from __future__ import annotations

import datetime
import os
import shutil
import stat

from PySide6.QtCore  import Qt, QDir, QModelIndex, QTimer, QProcess, QPoint, QUrl, QMimeData
from PySide6.QtGui   import QAction, QDrag, QTextCursor
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QDialog, QFileSystemModel,
    QFrame, QHBoxLayout, QHeaderView, QInputDialog, QLabel,
    QLineEdit, QMainWindow, QMenu, QMessageBox,
    QPlainTextEdit, QPushButton, QSizePolicy,
    QSplitter, QStatusBar, QTextEdit, QTreeView,
    QVBoxLayout, QWidget,
)

# ──────────────────────────────────────────────────────────────
#  Farbpalette  (Norton Commander Classic)
# ──────────────────────────────────────────────────────────────
NC_BG           = "#0000AA"
NC_PANEL_BG     = "#0000AA"
NC_PANEL_BORDER = "#00AAAA"
NC_TEXT_BRIGHT  = "#FFFFFF"
NC_HEADER       = "#FFFF00"
NC_SELECTED_BG  = "#00AAAA"
NC_SELECTED_FG  = "#000000"
NC_TITLE_BG     = "#00AAAA"
NC_TITLE_FG     = "#000000"
NC_INACTIVE_BG  = "#005577"
NC_CMD_BG       = "#000000"
NC_LOG_FG       = "#00FF88"
NC_FKEY_BG      = "#000088"
NC_FKEY_NUM     = "#FFFF00"
NC_FKEY_TXT     = "#FFFFFF"
NC_MENU_BG      = "#00AAAA"
NC_MENU_FG      = "#000000"
NC_MENU_SEL     = "#FFFFFF"
NC_INPUT_BG     = "#000033"

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {NC_BG};
    color: {NC_TEXT_BRIGHT};
    font-family: "Courier New", "Lucida Console", monospace;
    font-size: 13px;
}}
QMenuBar {{
    background-color: {NC_BG}; color: {NC_HEADER};
    font-family: "Courier New", monospace; font-size: 13px;
    border-bottom: 1px solid {NC_PANEL_BORDER};
    spacing: 4px; padding: 2px 4px;
}}
QMenuBar::item {{ background: transparent; padding: 2px 10px; color: {NC_HEADER}; }}
QMenuBar::item:selected, QMenuBar::item:pressed {{
    background-color: {NC_MENU_BG}; color: {NC_MENU_FG};
}}
QMenu {{
    background-color: {NC_MENU_BG}; color: {NC_MENU_FG};
    border: 1px solid {NC_PANEL_BORDER};
    font-family: "Courier New", monospace; font-size: 13px;
}}
QMenu::item:selected {{ background-color: {NC_BG}; color: {NC_MENU_SEL}; }}
QMenu::separator {{ height: 1px; background: {NC_PANEL_BORDER}; margin: 2px 4px; }}

QFrame#panel_frame {{ border: 1px solid {NC_PANEL_BORDER}; background-color: {NC_PANEL_BG}; }}

QLabel#panel_title {{
    background-color: {NC_TITLE_BG}; color: {NC_TITLE_FG};
    font-family: "Courier New", monospace; font-size: 13px; font-weight: bold;
    padding: 1px 8px; qproperty-alignment: AlignCenter;
}}

QTreeView {{
    background-color: {NC_PANEL_BG}; color: {NC_TEXT_BRIGHT};
    border: none;
    font-family: "Courier New", "Lucida Console", monospace; font-size: 13px;
    selection-background-color: {NC_SELECTED_BG}; selection-color: {NC_SELECTED_FG};
    show-decoration-selected: 1; alternate-background-color: {NC_PANEL_BG}; outline: none;
}}
QTreeView::item {{ padding: 1px 2px; border: none; }}
QTreeView::item:hover {{ background-color: #0055CC; color: {NC_TEXT_BRIGHT}; }}
QTreeView::item:selected {{
    background-color: {NC_SELECTED_BG}; color: {NC_SELECTED_FG}; font-weight: bold;
}}
QTreeView::branch {{ background-color: {NC_PANEL_BG}; }}

QHeaderView {{ background-color: {NC_PANEL_BG}; font-family: "Courier New", monospace; font-size: 13px; }}
QHeaderView::section {{
    background-color: {NC_PANEL_BG}; color: {NC_HEADER};
    border: none; border-bottom: 1px solid {NC_PANEL_BORDER};
    padding: 2px 4px; font-weight: bold;
}}

QSplitter::handle {{ background-color: {NC_PANEL_BORDER}; width: 1px; }}

QPlainTextEdit#terminal_output {{
    background-color: {NC_CMD_BG}; color: {NC_LOG_FG};
    font-family: "Courier New", monospace; font-size: 12px;
    border: none;
    selection-background-color: {NC_SELECTED_BG};
}}

QLineEdit#terminal_input {{
    background-color: {NC_INPUT_BG}; color: {NC_LOG_FG};
    font-family: "Courier New", monospace; font-size: 13px;
    border: none; border-top: 1px solid {NC_PANEL_BORDER};
    padding: 2px 6px;
    selection-background-color: {NC_SELECTED_BG};
}}

QStatusBar {{
    background-color: {NC_CMD_BG}; color: #AAAAAA;
    font-family: "Courier New", monospace; font-size: 12px;
    border-top: 1px solid {NC_PANEL_BORDER};
}}
QStatusBar::item {{ border: none; }}

QScrollBar:vertical {{ background: {NC_PANEL_BG}; width: 10px; border: none; }}
QScrollBar::handle:vertical {{ background: {NC_PANEL_BORDER}; min-height: 20px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{ background: {NC_PANEL_BG}; height: 10px; border: none; }}
QScrollBar::handle:horizontal {{ background: {NC_PANEL_BORDER}; min-width: 20px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}

QLabel#path_label {{
    background-color: {NC_PANEL_BG}; color: {NC_PANEL_BORDER};
    font-family: "Courier New", monospace; font-size: 11px;
    padding: 1px 4px; border-top: 1px solid {NC_PANEL_BORDER};
}}

QFrame#fkey_bar {{ background-color: {NC_CMD_BG}; border-top: 1px solid {NC_PANEL_BORDER}; }}

QDialog {{
    background-color: {NC_MENU_BG}; color: {NC_MENU_FG};
    font-family: "Courier New", monospace; font-size: 13px;
}}
QDialog QLabel {{ color: {NC_MENU_FG}; }}
QDialog QLineEdit {{
    background: {NC_BG}; color: {NC_TEXT_BRIGHT};
    border: 1px solid {NC_PANEL_BORDER};
    font-family: "Courier New", monospace; font-size: 13px; padding: 2px 4px;
}}
QDialog QPushButton {{
    background: {NC_BG}; color: {NC_TEXT_BRIGHT};
    border: 1px solid {NC_PANEL_BORDER};
    font-family: "Courier New", monospace; font-size: 13px;
    padding: 3px 14px; min-width: 60px;
}}
QDialog QPushButton:hover {{ background: #0055CC; }}
QMessageBox, QInputDialog {{
    background-color: {NC_MENU_BG};
    font-family: "Courier New", monospace; font-size: 13px;
}}
"""


# ──────────────────────────────────────────────────────────────
#  Drag-fähiger TreeView
# ──────────────────────────────────────────────────────────────
class DnDTreeView(QTreeView):
    """QTreeView mit Drag & Drop und Kontextmenü."""

    def __init__(self, parent_window: "MainWindow", side: str):
        super().__init__()
        self._pw   = parent_window
        self._side = side
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.CopyAction)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pw._set_active(self._side)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        self._pw._show_context_menu(event.globalPos(), self._side)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            super().dropEvent(event)
            return

        model = (self._pw.fs_model_left if self._side == "left"
                 else self._pw.fs_model_right)
        idx = self.indexAt(event.position().toPoint())
        dest = (model.filePath(idx)
                if idx.isValid() and model.isDir(idx)
                else model.rootPath())

        do_move = bool(event.modifiers() & Qt.ShiftModifier)

        for url in event.mimeData().urls():
            src = url.toLocalFile()
            dst = os.path.join(dest, os.path.basename(src))
            try:
                if do_move:
                    shutil.move(src, dst)
                    self._pw.append_log(f"[D&D] Verschoben: {src} → {dst}")
                else:
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                    self._pw.append_log(f"[D&D] Kopiert: {src} → {dst}")
            except Exception as e:
                self._pw.append_log(f"[FEHLER] D&D: {e}")

        event.acceptProposedAction()
        self._pw._reload_models()


# ──────────────────────────────────────────────────────────────
#  Breadcrumb-Navigationsleiste
# ──────────────────────────────────────────────────────────────
class BreadcrumbBar(QWidget):
    """Pfad als klickbare Segmente: /  >  home  >  peter  >  Dev"""

    def __init__(self, navigate_cb, parent=None):
        super().__init__(parent)
        self._navigate_cb = navigate_cb
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 1, 4, 1)
        self._layout.setSpacing(0)
        self.setStyleSheet(
            f"background:{NC_PANEL_BG};"
            f"border-top:1px solid {NC_PANEL_BORDER};")
        self._layout.addStretch()

    def set_path(self, path: str):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        parts = [p for p in path.split("/") if p]
        self._add_segment("/", "/")

        accumulated = ""
        for part in parts:
            accumulated += "/" + part
            sep = QLabel(" ›")
            sep.setStyleSheet(
                f"color:{NC_PANEL_BORDER};background:{NC_PANEL_BG};"
                f"font-family:'Courier New',monospace;font-size:11px;padding:0 1px;")
            self._layout.addWidget(sep)
            self._add_segment(part, accumulated)

        self._layout.addStretch()

    def set_navigate_cb(self, cb):
        self._navigate_cb = cb

    def _add_segment(self, label: str, target_path: str):
        btn = QPushButton(label)
        btn.setFlat(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            f"QPushButton {{"
            f"  color:{NC_PANEL_BORDER};background:{NC_PANEL_BG};"
            f"  font-family:'Courier New',monospace;font-size:11px;"
            f"  border:none;padding:1px 3px;"
            f"}}"
            f"QPushButton:hover {{"
            f"  color:{NC_TEXT_BRIGHT};background:#0055CC;"
            f"  border-radius:2px;"
            f"}}")
        btn.clicked.connect(lambda checked=False, p=target_path: self._navigate_cb(p))
        self._layout.addWidget(btn)


# ──────────────────────────────────────────────────────────────
#  Panel-Builder  (mit Breadcrumb)
# ──────────────────────────────────────────────────────────────
def _build_panel(tree: DnDTreeView, side: str) -> tuple[QFrame, QLabel, "BreadcrumbBar"]:
    frame = QFrame()
    frame.setObjectName("panel_frame")
    vbox = QVBoxLayout(frame)
    vbox.setContentsMargins(2, 2, 2, 2)
    vbox.setSpacing(0)

    title = QLabel(f" {side} ")
    title.setObjectName("panel_title")
    vbox.addWidget(title)

    # ".." Zeile über dem Tree — wird per navigate_cb verdrahtet
    dotdot_btn = QPushButton("  📁  ..")
    dotdot_btn.setFlat(True)
    dotdot_btn.setCursor(Qt.PointingHandCursor)
    dotdot_btn.setObjectName("dotdot_btn")
    dotdot_btn.setStyleSheet(
        f"QPushButton#dotdot_btn {{"
        f"  text-align:left;"
        f"  background:{NC_PANEL_BG};color:{NC_TEXT_BRIGHT};"
        f"  font-family:'Courier New',monospace;font-size:13px;"
        f"  border:none;border-bottom:1px solid {NC_PANEL_BORDER};"
        f"  padding:2px 6px;"
        f"}}"
        f"QPushButton#dotdot_btn:hover {{ background:#0055CC; }}")
    vbox.addWidget(dotdot_btn)

    vbox.addWidget(tree)

    breadcrumb = BreadcrumbBar(lambda p: None)
    vbox.addWidget(breadcrumb)

    return frame, title, breadcrumb, dotdot_btn


# ──────────────────────────────────────────────────────────────
#  Eigenschaften-Dialog
# ──────────────────────────────────────────────────────────────
class PropertiesDialog(QDialog):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Eigenschaften")
        self.setMinimumWidth(440)
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        def row(key: str, val: str):
            lbl = QLabel(f"<b>{key}:</b>  {val}")
            lbl.setTextFormat(Qt.RichText)
            layout.addWidget(lbl)

        row("Pfad",  path)
        row("Name",  os.path.basename(path))
        row("Typ",   "Verzeichnis" if os.path.isdir(path) else "Datei")
        try:
            st   = os.stat(path)
            sz   = st.st_size
            size = (f"{sz/1024/1024:.2f} MB" if sz > 1048576
                    else f"{sz/1024:.1f} KB"  if sz > 1024
                    else f"{sz} Bytes")
            row("Größe",   size)
            row("Geändert", datetime.datetime.fromtimestamp(st.st_mtime)
                .strftime("%d.%m.%Y %H:%M:%S"))
            row("Rechte",  oct(stat.S_IMODE(st.st_mode)))
        except Exception as e:
            row("Fehler",  str(e))

        btn = QPushButton("Schließen")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)


# ──────────────────────────────────────────────────────────────
#  Theme-Manager Dialog
# ──────────────────────────────────────────────────────────────
class ThemeManagerDialog(QDialog):
    """
    Zeigt alle verfügbaren Themes an, erlaubt Vorschau und Anwenden.
    Verwendet ThemeNode für Laden und EventBus für Live-Wechsel.
    """

    PREVIEWS = {
        "norton_commander": "🖥️  Norton Commander Classic\nRetro DOS Blau/Cyan/Gelb",
        "dark":             "🌑  Dark Modern\nDunkles IDE-Theme (VS Code Stil)",
        "midnight_commander": "💚  Midnight Commander\nGrünes Terminal-Klassiker-Theme",
    }

    def __init__(self, theme_node, app, parent=None):
        super().__init__(parent)
        self._theme_node = theme_node
        self._app        = app
        self._original   = theme_node.current  # für Abbrechen

        self.setWindowTitle("🎨  Theme-Manager")
        self.setMinimumSize(520, 380)
        self._build()
        self._populate()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(16, 16, 16, 12)

        # Titel
        title = QLabel("Theme-Manager")
        title.setStyleSheet(
            "font-size:16px;font-weight:bold;color:#FFFF00;"
            "background:transparent;padding:0;")
        root.addWidget(title)

        sub = QLabel("Theme auswählen und sofort vorschauen — Änderungen gelten live.")
        sub.setStyleSheet("color:#AAAAAA;font-size:11px;background:transparent;")
        root.addWidget(sub)

        # Splitter: Liste links, Info rechts
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(4)

        # Theme-Liste
        list_frame = QFrame()
        list_frame.setObjectName("panel_frame")
        lf_layout = QVBoxLayout(list_frame)
        lf_layout.setContentsMargins(4, 4, 4, 4)
        lf_layout.setSpacing(4)

        list_lbl = QLabel(" Verfügbare Themes ")
        list_lbl.setObjectName("panel_title")
        lf_layout.addWidget(list_lbl)

        from PySide6.QtWidgets import QListWidget
        self._list = QListWidget()
        self._list.setStyleSheet(
            "QListWidget { background:#0000AA; color:#FFFFFF; border:none;"
            "font-family:'Courier New',monospace; font-size:13px; }"
            "QListWidget::item:selected { background:#00AAAA; color:#000000; }"
            "QListWidget::item:hover { background:#0055CC; }")
        self._list.currentTextChanged.connect(self._on_preview)
        lf_layout.addWidget(self._list)
        splitter.addWidget(list_frame)

        # Info-Panel rechts
        info_frame = QFrame()
        info_frame.setObjectName("panel_frame")
        if_layout = QVBoxLayout(info_frame)
        if_layout.setContentsMargins(4, 4, 4, 4)
        if_layout.setSpacing(4)

        info_lbl = QLabel(" Vorschau ")
        info_lbl.setObjectName("panel_title")
        if_layout.addWidget(info_lbl)

        self._info = QPlainTextEdit()
        self._info.setObjectName("terminal_output")
        self._info.setReadOnly(True)
        if_layout.addWidget(self._info)

        # Mini-Vorschaufenster (gefärbter Block)
        self._preview_box = QLabel("◼ ◼ ◼  Panel Links      ◼ ◼ ◼  Panel Rechts\n"
                                   "  Name          Size Type   Name          Size Type\n"
                                   "  Documents      DIR        Downloads      DIR\n"
                                   "  file.txt      1 KB txt    readme.md     2 KB md\n"
                                   "\n  /home/user                /home/user/Dev")
        self._preview_box.setStyleSheet(
            "font-family:'Courier New',monospace;font-size:11px;"
            "background:#000088;color:#AAFFAA;padding:6px;border:1px solid #00AAAA;")
        self._preview_box.setWordWrap(False)
        if_layout.addWidget(self._preview_box)

        splitter.addWidget(info_frame)
        splitter.setSizes([180, 320])
        root.addWidget(splitter)

        # Knöpfe
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._btn_apply = QPushButton("✔  Anwenden")
        self._btn_apply.clicked.connect(self._apply)
        btn_row.addWidget(self._btn_apply)

        btn_cancel = QPushButton("✖  Abbrechen")
        btn_cancel.clicked.connect(self._cancel)
        btn_row.addWidget(btn_cancel)

        btn_row.addStretch()

        self._current_label = QLabel("")
        self._current_label.setStyleSheet("color:#00FF88;font-size:11px;background:transparent;")
        btn_row.addWidget(self._current_label)

        root.addLayout(btn_row)

        # Aktuelles Theme anzeigen
        if self._theme_node.current:
            self._current_label.setText(f"Aktiv: {self._theme_node.current}")

    def _populate(self):
        themes = self._theme_node.list_themes()
        if not themes:
            self._list.addItem("(keine Themes gefunden)")
            return
        for t in sorted(themes):
            self._list.addItem(t)
        # Aktuelles Theme vorauswählen
        current = self._theme_node.current or ""
        for i in range(self._list.count()):
            if self._list.item(i).text() == current:
                self._list.setCurrentRow(i)
                break

    def _on_preview(self, name: str):
        """Sofort anwenden als Live-Vorschau."""
        if not name or name.startswith("("):
            return
        css = self._theme_node.load_theme(name)
        if css and self._app:
            self._app.setStyleSheet(css)

        desc = self.PREVIEWS.get(name, f"Theme: {name}\nKeine Beschreibung verfügbar.")
        self._info.setPlainText(desc)
        self._current_label.setText(f"Vorschau: {name}")

    def _apply(self):
        item = self._list.currentItem()
        if item and not item.text().startswith("("):
            self._original = item.text()
            self._current_label.setText(f"Aktiv: {self._original}")
        self.accept()

    def _cancel(self):
        """Theme auf Original zurücksetzen."""
        if self._original:
            css = self._theme_node.load_theme(self._original)
            if css and self._app:
                self._app.setStyleSheet(css)
        self.reject()


# ──────────────────────────────────────────────────────────────
#  Haupt-Fenster
# ──────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):

    FKEYS = [
        ("1",  "Hilfe"),
        ("2",  "Benutze"),
        ("3",  "Anz."),
        ("4",  "Bearb."),
        ("5",  "Kopie"),
        ("6",  "UmbBew"),
        ("7",  "VerzEr"),
        ("8",  "Lösche"),
        ("9",  "Menü"),
        ("10", "Beend."),
    ]

    def __init__(self, log_engine=None, app=None, events=None, theme_node=None):
        super().__init__()
        self.app         = app
        self.events      = events
        self._theme_node = theme_node
        self._active_panel  = "left"
        self._show_hidden   = False
        self._cmd_history: list[str] = []
        self._cmd_hist_idx  = -1
        self._cwd = os.path.expanduser("~")

        self.setWindowTitle("SysRunner")
        self.resize(1400, 860)
        # Stylesheet kommt via ThemeNode; Fallback falls keiner übergeben
        if not theme_node:
            self.setStyleSheet(STYLESHEET)
        # Live-Theme-Wechsel via EventBus
        if self.events:
            self.events.on("theme.changed", self._on_theme_changed)

        self._build_menu()
        self._build_ui()
        self._setup_fs_models()
        self._connect_signals()
        self._patch_history_keys()

        if log_engine:
            log_engine.set_ui_callback(self.append_log)

        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

        self._set_active("left")
        self.left_tree.setFocus()

    # ── Menü ─────────────────────────────────
    def _build_menu(self):
        mb = self.menuBar()

        mf = mb.addMenu("&Datei")
        mf.addAction(QAction("Neu…",    self, shortcut="Ctrl+N"))
        mf.addAction(QAction("Öffnen…", self, shortcut="Ctrl+O"))
        mf.addSeparator()
        mf.addAction(QAction("Beenden", self, shortcut="Alt+F4",
                             triggered=self.close))

        mv = mb.addMenu("&Ansicht")
        mv.addAction(QAction("Neu laden", self, shortcut="Ctrl+R",
                             triggered=self._reload_models))

        mt = mb.addMenu("&Terminal")
        mt.addAction(QAction("Leeren", self, triggered=self._clear_terminal))
        mt.addAction(QAction("Ins aktive Panel-Verzeichnis wechseln", self,
                             shortcut="Ctrl+T", triggered=self._cd_active))

        ms = mb.addMenu("&Einstellungen")
        ms.addAction(QAction("🎨  Theme-Manager…", self,
                             shortcut="Ctrl+Shift+T",
                             triggered=self._show_theme_manager))
        ms.addSeparator()
        ms.addAction(QAction("Versteckte Dateien", self,
                             checkable=True,
                             triggered=self._toggle_hidden))

        mh = mb.addMenu("&Hilfe")
        mh.addAction(QAction("Über SysRunner", self, triggered=self._show_about))

    # ── UI ───────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(4, 4, 4, 0)
        root.setSpacing(4)

        # Datei-Panels
        hsplit = QSplitter(Qt.Horizontal)
        hsplit.setHandleWidth(2)
        hsplit.setChildrenCollapsible(False)

        self.left_tree  = DnDTreeView(self, "left")
        self.right_tree = DnDTreeView(self, "right")
        for t in (self.left_tree, self.right_tree):
            t.setUniformRowHeights(True)
            t.setAlternatingRowColors(False)
            t.setSelectionBehavior(QAbstractItemView.SelectRows)
            t.setSelectionMode(QAbstractItemView.ExtendedSelection)
            t.setEditTriggers(QAbstractItemView.NoEditTriggers)
            t.setSortingEnabled(True)
            t.setAnimated(False)
            t.setIndentation(14)
            t.header().setStretchLastSection(False)
            t.header().setSectionResizeMode(QHeaderView.Interactive)

        lf, self.left_title,  self.left_bread,  self._dotdot_left  = _build_panel(self.left_tree,  "Links")
        rf, self.right_title, self.right_bread, self._dotdot_right = _build_panel(self.right_tree, "Rechts")
        # Breadcrumb-Callbacks verdrahten
        self.left_bread.set_navigate_cb(lambda p: self._navigate_to(p, "left"))
        self.right_bread.set_navigate_cb(lambda p: self._navigate_to(p, "right"))
        # ".." Buttons verdrahten
        self._dotdot_left.clicked.connect(lambda: self._go_up("left"))
        self._dotdot_right.clicked.connect(lambda: self._go_up("right"))
        hsplit.addWidget(lf)
        hsplit.addWidget(rf)
        hsplit.setSizes([700, 700])
        root.addWidget(hsplit, stretch=4)

        # Terminal-Bereich
        tf = QFrame()
        tf.setObjectName("panel_frame")
        tl = QVBoxLayout(tf)
        tl.setContentsMargins(2, 2, 2, 2)
        tl.setSpacing(0)

        tt = QLabel(" Terminal ")
        tt.setObjectName("panel_title")
        tl.addWidget(tt)

        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setObjectName("terminal_output")
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setMaximumHeight(140)
        tl.addWidget(self.terminal_output)

        # Eingabezeile
        irow = QHBoxLayout()
        irow.setContentsMargins(0, 0, 0, 0)
        irow.setSpacing(0)
        self._prompt_label = QLabel(f" {self._cwd} $ ")
        self._prompt_label.setStyleSheet(
            f"color:{NC_LOG_FG};background:{NC_CMD_BG};"
            f"font-family:'Courier New',monospace;font-size:13px;"
            f"padding:2px 4px;border-top:1px solid {NC_PANEL_BORDER};")
        irow.addWidget(self._prompt_label)

        self.terminal_input = QLineEdit()
        self.terminal_input.setObjectName("terminal_input")
        self.terminal_input.setPlaceholderText(
            "Befehl eingeben… (Enter = ausführen, Pfeil ↑↓ = History)")
        irow.addWidget(self.terminal_input)
        tl.addLayout(irow)

        root.addWidget(tf, stretch=1)

        # F-Tasten-Leiste
        fbar = QFrame()
        fbar.setObjectName("fkey_bar")
        fb_layout = QHBoxLayout(fbar)
        fb_layout.setContentsMargins(2, 2, 2, 2)
        fb_layout.setSpacing(2)
        for num, label in self.FKEYS:
            lbl = QLabel(
                f"<span style='color:{NC_FKEY_NUM};font-weight:bold'>{num}</span>"
                f"<span style='color:{NC_FKEY_TXT}'>{label}</span>")
            lbl.setTextFormat(Qt.RichText)
            lbl.setStyleSheet(
                f"background:{NC_FKEY_BG};border:1px solid {NC_PANEL_BORDER};"
                f"padding:1px 5px;font-family:'Courier New',monospace;font-size:12px;")
            fb_layout.addWidget(lbl)
        root.addWidget(fbar)

        # Statusleiste
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._status_left  = QLabel("")
        self._status_clock = QLabel("")
        self.status_bar.addWidget(self._status_left, stretch=1)
        self.status_bar.addPermanentWidget(self._status_clock)

        # QProcess
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_proc_out)
        self._process.finished.connect(self._on_proc_done)

    # ── Filesystem-Modelle ───────────────────
    def _setup_fs_models(self):
        root  = "/"
        flags = QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot
        if self._show_hidden:
            flags |= QDir.Hidden

        self.fs_model_left = QFileSystemModel()
        self.fs_model_left.setRootPath(root)
        self.fs_model_left.setFilter(flags)
        self.left_tree.setModel(self.fs_model_left)
        self.left_tree.setRootIndex(self.fs_model_left.index(root))
        self._col_widths(self.left_tree)

        self.fs_model_right = QFileSystemModel()
        self.fs_model_right.setRootPath(root)
        self.fs_model_right.setFilter(flags)
        self.right_tree.setModel(self.fs_model_right)
        self.right_tree.setRootIndex(self.fs_model_right.index(root))
        self._col_widths(self.right_tree)

        self.left_bread.set_path(root)
        self.right_bread.set_path(root)
        self._connect_tree_signals()

    def _col_widths(self, tree: DnDTreeView):
        h = tree.header()
        h.resizeSection(0, 230)
        h.resizeSection(1, 80)
        h.resizeSection(2, 70)
        h.resizeSection(3, 130)

    # ── Signale ──────────────────────────────
    def _connect_signals(self):
        self.terminal_input.returnPressed.connect(self._run_command)

    def _connect_tree_signals(self):
        self.left_tree.activated.connect(
            lambda idx: self._on_activated(idx, "left"))
        self.right_tree.activated.connect(
            lambda idx: self._on_activated(idx, "right"))
        self.left_tree.selectionModel().currentChanged.connect(
            lambda cur, _: self._on_sel_changed(cur, "left"))
        self.right_tree.selectionModel().currentChanged.connect(
            lambda cur, _: self._on_sel_changed(cur, "right"))

    # ── Panel-Fokus ──────────────────────────
    def _set_active(self, side: str):
        self._active_panel = side
        a = (f"background:{NC_TITLE_BG};color:{NC_TITLE_FG};font-weight:bold;"
             f"font-family:'Courier New',monospace;font-size:13px;"
             f"padding:1px 8px;qproperty-alignment:AlignCenter;")
        i = (f"background:{NC_INACTIVE_BG};color:#AAAAAA;"
             f"font-family:'Courier New',monospace;font-size:13px;"
             f"padding:1px 8px;qproperty-alignment:AlignCenter;")
        self.left_title.setStyleSheet( a if side == "left"  else i)
        self.right_title.setStyleSheet(a if side == "right" else i)

    def _active_model(self) -> QFileSystemModel:
        return self.fs_model_left if self._active_panel == "left" else self.fs_model_right

    def _active_tree(self) -> DnDTreeView:
        return self.left_tree if self._active_panel == "left" else self.right_tree

    def _opposite_dir(self) -> str:
        return (self.fs_model_right.rootPath() if self._active_panel == "left"
                else self.fs_model_left.rootPath())

    def _selected_paths(self, side: str) -> list[str]:
        tree  = self.left_tree  if side == "left" else self.right_tree
        model = self.fs_model_left if side == "left" else self.fs_model_right
        return [model.filePath(i) for i in tree.selectedIndexes() if i.column() == 0]

    # ── Navigation ───────────────────────────
    def _go_up(self, side: str):
        """Eine Verzeichnisebene höher navigieren."""
        model = self.fs_model_left if side == "left" else self.fs_model_right
        current = model.rootPath()
        parent = os.path.dirname(current.rstrip("/")) or "/"
        if parent and os.path.isdir(parent):
            self._navigate_to(parent, side)

    def _navigate_to(self, path: str, side: str):
        """Direkte Navigation zu einem Pfad (Breadcrumb-Klick oder ..)."""
        model  = self.fs_model_left  if side == "left" else self.fs_model_right
        tree   = self.left_tree      if side == "left" else self.right_tree
        bread  = self.left_bread     if side == "left" else self.right_bread
        dotdot = self._dotdot_left   if side == "left" else self._dotdot_right
        if os.path.isdir(path):
            model.setRootPath(path)
            tree.setRootIndex(model.index(path))
            bread.set_path(path)
            # ".." ausblenden wenn wir im Root sind
            dotdot.setVisible(os.path.normpath(path) != "/")
            if self._active_panel == side:
                self._cwd = path
                self._update_prompt()
            self.append_log(f"[{side.upper()}] → {path}")

    def _on_activated(self, index: QModelIndex, side: str):
        model = self.fs_model_left if side == "left" else self.fs_model_right
        tree  = self.left_tree     if side == "left" else self.right_tree
        bread = self.left_bread    if side == "left" else self.right_bread
        path  = model.filePath(index)
        if model.isDir(index):
            # ".." → eine Ebene hoch
            parent = os.path.dirname(path) if path == model.rootPath() else path
            model.setRootPath(path)
            tree.setRootIndex(model.index(path))
            bread.set_path(path)
            self._cwd = path
            self._update_prompt()
            self.append_log(f"[{side.upper()}] → {path}")
        else:
            self.append_log(f"[{side.upper()}] Datei: {path}")

    def _on_sel_changed(self, current: QModelIndex, side: str):
        if not current.isValid():
            return
        model = self.fs_model_left if side == "left" else self.fs_model_right
        path  = model.filePath(current)
        try:
            st = os.stat(path)
            info = (f"{path}   {st.st_size:,} Bytes"
                    if not os.path.isdir(path) else f"{path}   <DIR>")
        except Exception:
            info = path
        self._status_left.setText(info)

    # ── Kontextmenü ──────────────────────────
    def _show_context_menu(self, gpos: QPoint, side: str):
        paths  = self._selected_paths(side)
        single = paths[0] if len(paths) == 1 else None
        menu   = QMenu(self)

        if single:
            name = os.path.basename(single)
            if os.path.isdir(single):
                menu.addAction(f"📂  Öffnen: {name}",
                               lambda p=single, s=side: self._on_activated(
                                   (self.fs_model_left if s == "left"
                                    else self.fs_model_right).index(p), s))
            else:
                menu.addAction(f"👁️  Anzeigen: {name}  (F3)", self._f3_view)
                menu.addAction(f"✏️  Bearbeiten: {name}  (F4)", self._f4_edit)
            menu.addSeparator()

        menu.addAction("📋  Kopieren → gegenüber  (F5)",
                       lambda: self._f5_copy(side))
        menu.addAction("✂️  Verschieben → gegenüber  (F6)",
                       lambda: self._f6_move(side))
        menu.addSeparator()
        menu.addAction("📁  Neuer Ordner  (F7)", self._f7_mkdir)
        menu.addAction("🗑️  Löschen  (F8)",      lambda: self._f8_delete(side))
        menu.addSeparator()

        if single:
            menu.addAction("✏️  Umbenennen", lambda p=single: self._rename(p))
            menu.addAction("ℹ️  Eigenschaften",
                           lambda p=single: PropertiesDialog(p, self).exec())
            menu.addSeparator()

        menu.addAction("📋  Pfad in Zwischenablage",
                       lambda: QApplication.clipboard().setText(
                           single or self._active_model().rootPath()))
        menu.addAction("💻  Im Terminal öffnen",
                       lambda: self._cd_to(
                           single if single and os.path.isdir(single)
                           else (os.path.dirname(single) if single else
                                 self._active_model().rootPath())))
        menu.exec(gpos)

    # ── F-Tasten ─────────────────────────────
    def _f1_help(self):
        QMessageBox.information(self, "F1 – Hilfe",
            "Tab        Panel wechseln\n"
            "F3         Datei anzeigen\n"
            "F4         Datei bearbeiten\n"
            "F5         Kopieren → gegenüber\n"
            "F6         Verschieben → gegenüber\n"
            "F7         Neues Verzeichnis\n"
            "F8         Löschen\n"
            "F9         Menüleiste\n"
            "F10        Beenden\n"
            "Ctrl+R     Ansicht neu laden\n"
            "Ctrl+T     Terminal: Panel-Verz. wechseln\n"
            "Shift+Drag D&D verschieben (sonst kopieren)")

    def _f2_user_menu(self):
        m = QMenu(self)
        m.addAction("Anzeigen    F3", self._f3_view)
        m.addAction("Bearbeiten  F4", self._f4_edit)
        m.addAction("Kopieren    F5", lambda: self._f5_copy(self._active_panel))
        m.addAction("Verschieben F6", lambda: self._f6_move(self._active_panel))
        m.addAction("Neuer Ordner F7", self._f7_mkdir)
        m.addAction("Löschen     F8", lambda: self._f8_delete(self._active_panel))
        m.exec(self.mapToGlobal(QPoint(0, self.height() - 60)))

    def _f3_view(self):
        paths = self._selected_paths(self._active_panel)
        if not paths or os.path.isdir(paths[0]):
            return
        path = paths[0]
        try:
            with open(path, "r", errors="replace") as f:
                content = f.read(65536)
            dlg = QDialog(self)
            dlg.setWindowTitle(f"Anzeigen: {os.path.basename(path)}")
            dlg.resize(700, 500)
            lay = QVBoxLayout(dlg)
            te = QPlainTextEdit(content)
            te.setReadOnly(True)
            te.setObjectName("terminal_output")
            lay.addWidget(te)
            btn = QPushButton("Schließen")
            btn.clicked.connect(dlg.accept)
            lay.addWidget(btn, alignment=Qt.AlignRight)
            dlg.exec()
        except Exception as e:
            self.append_log(f"[FEHLER] F3: {e}")

    def _f4_edit(self):
        paths = self._selected_paths(self._active_panel)
        if not paths:
            return
        path = paths[0]
        for editor in ["xdg-open", "kate", "gedit", "mousepad", "nano", "vim"]:
            if shutil.which(editor):
                QProcess.startDetached(editor, [path])
                self.append_log(f"[F4] '{editor}' → {path}")
                return
        self.append_log("[FEHLER] F4: Kein Editor gefunden.")

    def _f5_copy(self, side: str):
        paths = self._selected_paths(side)
        if not paths:
            return self.append_log("[F5] Nichts ausgewählt.")
        dest = (self.fs_model_right.rootPath() if side == "left"
                else self.fs_model_left.rootPath())
        if QMessageBox.question(
                self, "Kopieren",
                f"{len(paths)} Objekt(e) kopieren nach:\n{dest}?",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        for src in paths:
            dst = os.path.join(dest, os.path.basename(src))
            try:
                shutil.copytree(src, dst) if os.path.isdir(src) else shutil.copy2(src, dst)
                self.append_log(f"[F5] Kopiert: {os.path.basename(src)}")
            except Exception as e:
                self.append_log(f"[FEHLER] F5: {e}")
        self._reload_models()

    def _f6_move(self, side: str):
        paths = self._selected_paths(side)
        if not paths:
            return self.append_log("[F6] Nichts ausgewählt.")
        dest = (self.fs_model_right.rootPath() if side == "left"
                else self.fs_model_left.rootPath())
        if QMessageBox.question(
                self, "Verschieben",
                f"{len(paths)} Objekt(e) verschieben nach:\n{dest}?",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        for src in paths:
            dst = os.path.join(dest, os.path.basename(src))
            try:
                shutil.move(src, dst)
                self.append_log(f"[F6] Verschoben: {os.path.basename(src)}")
            except Exception as e:
                self.append_log(f"[FEHLER] F6: {e}")
        self._reload_models()

    def _f7_mkdir(self):
        cwd  = self._active_model().rootPath()
        name, ok = QInputDialog.getText(
            self, "Neuer Ordner", f"Name des neuen Ordners in:\n{cwd}")
        if ok and name.strip():
            new_path = os.path.join(cwd, name.strip())
            try:
                os.makedirs(new_path, exist_ok=True)
                self.append_log(f"[F7] Erstellt: {new_path}")
                self._reload_models()
            except Exception as e:
                self.append_log(f"[FEHLER] F7: {e}")

    def _f8_delete(self, side: str):
        paths = self._selected_paths(side)
        if not paths:
            return self.append_log("[F8] Nichts ausgewählt.")
        names = "\n".join(os.path.basename(p) for p in paths[:8])
        if len(paths) > 8:
            names += f"\n… und {len(paths)-8} weitere"
        if QMessageBox.warning(
                self, "Löschen",
                f"Endgültig löschen?\n\n{names}",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        for p in paths:
            try:
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
                self.append_log(f"[F8] Gelöscht: {os.path.basename(p)}")
            except Exception as e:
                self.append_log(f"[FEHLER] F8: {e}")
        self._reload_models()

    def _f9_menu(self):
        acts = self.menuBar().actions()
        if acts:
            self.menuBar().setActiveAction(acts[0])

    # ── Umbenennen ───────────────────────────
    def _rename(self, path: str):
        old  = os.path.basename(path)
        new, ok = QInputDialog.getText(self, "Umbenennen", "Neuer Name:", text=old)
        if ok and new.strip() and new != old:
            try:
                os.rename(path, os.path.join(os.path.dirname(path), new.strip()))
                self.append_log(f"[REN] {old} → {new}")
                self._reload_models()
            except Exception as e:
                self.append_log(f"[FEHLER] Umbenennen: {e}")

    # ── Terminal ─────────────────────────────
    def _update_prompt(self):
        short = self._cwd.replace(os.path.expanduser("~"), "~")
        self._prompt_label.setText(f" {short} $ ")

    def _run_command(self):
        cmd = self.terminal_input.text().strip()
        if not cmd:
            return
        self._cmd_history.append(cmd)
        self._cmd_hist_idx = len(self._cmd_history)
        self.terminal_input.clear()

        # cd ist built-in
        if cmd.startswith("cd") and (len(cmd) == 2 or cmd[2] == " "):
            target = cmd[3:].strip() if len(cmd) > 3 else os.path.expanduser("~")
            target = os.path.expanduser(target)
            if not os.path.isabs(target):
                target = os.path.join(self._cwd, target)
            target = os.path.normpath(target)
            if os.path.isdir(target):
                self._cwd = target
                self._update_prompt()
                self._term_print(f"$ cd {cmd[3:] if len(cmd) > 3 else '~'}\n→ {target}\n")
            else:
                self._term_print(f"cd: {target}: Verzeichnis nicht gefunden\n")
            return

        if cmd in ("clear", "cls"):
            self.terminal_output.clear()
            return

        self._term_print(f"$ {cmd}\n")
        if self._process.state() != QProcess.NotRunning:
            self._process.kill()
            self._process.waitForFinished(300)
        self._process.setWorkingDirectory(self._cwd)
        self._process.start("bash", ["-c", cmd])

    def _on_proc_out(self):
        data = self._process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self._term_print(data)

    def _on_proc_done(self, code: int, _):
        if code != 0:
            self._term_print(f"[Exit: {code}]\n")

    def _term_print(self, text: str):
        c = self.terminal_output.textCursor()
        c.movePosition(QTextCursor.MoveOperation.End)
        self.terminal_output.setTextCursor(c)
        self.terminal_output.insertPlainText(text)
        self.terminal_output.ensureCursorVisible()

    def _clear_terminal(self):
        self.terminal_output.clear()

    def _cd_active(self):
        self._cd_to(self._active_model().rootPath())

    def _cd_to(self, path: str):
        if os.path.isdir(path):
            self._cwd = path
            self._update_prompt()
            self._term_print(f"$ cd {path}\n")
            self.terminal_input.setFocus()

    def append_log(self, msg: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._term_print(f"[{ts}] {msg}\n")

    # ── Hilfsmethoden ────────────────────────
    def _reload_models(self):
        l = self.fs_model_left.rootPath()
        r = self.fs_model_right.rootPath()
        self._setup_fs_models()
        for model, tree, bread, path in (
            (self.fs_model_left,  self.left_tree,  self.left_bread,  l),
            (self.fs_model_right, self.right_tree, self.right_bread, r),
        ):
            model.setRootPath(path)
            tree.setRootIndex(model.index(path))
            bread.set_path(path)

    def _toggle_hidden(self, checked: bool):
        self._show_hidden = checked
        self._reload_models()

    def _show_about(self):
        QMessageBox.about(self, "Über SysRunner",
                          "<b>SysRunner v2.0</b><br>"
                          "Norton Commander Style Dateimanager<br>"
                          "PySide6")

    def _update_clock(self):
        self._status_clock.setText(
            datetime.datetime.now().strftime("  %H:%M  "))

    # ── History-Navigation im Terminal ───────
    def _patch_history_keys(self):
        orig = self.terminal_input.keyPressEvent

        def patched(event):
            key = event.key()
            if key == Qt.Key_Up and self._cmd_history:
                self._cmd_hist_idx = max(0, self._cmd_hist_idx - 1)
                self.terminal_input.setText(self._cmd_history[self._cmd_hist_idx])
            elif key == Qt.Key_Down:
                self._cmd_hist_idx = min(len(self._cmd_history),
                                         self._cmd_hist_idx + 1)
                self.terminal_input.setText(
                    self._cmd_history[self._cmd_hist_idx]
                    if self._cmd_hist_idx < len(self._cmd_history) else "")
            else:
                orig(event)

        self.terminal_input.keyPressEvent = patched

    # ── Theme-Integration ────────────────────
    def _on_theme_changed(self, data: dict):
        """EventBus-Callback: wird von ThemeNode gefeuert."""
        css = data.get("css", "")
        if self.app:
            self.app.setStyleSheet(css)
        self.append_log(f"[THEME] Gewechselt zu: {data.get('name', '?')}")

    def _show_theme_manager(self):
        if not self._theme_node:
            QMessageBox.warning(self, "Theme-Manager",
                                "Kein ThemeNode verfügbar.\n"
                                "Bitte qt_main.py prüfen.")
            return
        dlg = ThemeManagerDialog(self._theme_node, self.app, self)
        dlg.exec()

    # ── Tastatur-Shortcuts ───────────────────
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Tab:
            if self._active_panel == "left":
                self._set_active("right")
                self.right_tree.setFocus()
            else:
                self._set_active("left")
                self.left_tree.setFocus()
            return
        if key == Qt.Key_Backspace:
            self._go_up(self._active_panel)
            return
        dispatch = {
            Qt.Key_F1:  self._f1_help,
            Qt.Key_F2:  self._f2_user_menu,
            Qt.Key_F3:  self._f3_view,
            Qt.Key_F4:  self._f4_edit,
            Qt.Key_F5:  lambda: self._f5_copy(self._active_panel),
            Qt.Key_F6:  lambda: self._f6_move(self._active_panel),
            Qt.Key_F7:  self._f7_mkdir,
            Qt.Key_F8:  lambda: self._f8_delete(self._active_panel),
            Qt.Key_F9:  self._f9_menu,
            Qt.Key_F10: self.close,
        }
        if key in dispatch:
            dispatch[key]()
            return
        super().keyPressEvent(event)