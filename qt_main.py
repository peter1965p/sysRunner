print("QT STARTET…")

from PySide6.QtWidgets import QApplication
from core.logging  import LogEngine
from core.events   import EventBus
from core.registry import NodeRegistry
from nodes.theme_node import ThemeNode
from ui.main_window   import MainWindow


def main():
    app      = QApplication([])
    log      = LogEngine()
    events   = EventBus()
    registry = NodeRegistry()

    # ── ThemeNode initialisieren ──────────────────────────────
    theme = ThemeNode(log, events, themes_dir="ui/themes")
    registry.register("theme", theme)

    # Standard-Theme beim Start laden
    # Reihenfolge: norton_commander → dark → erstes verfügbares
    start_theme = None
    available   = theme.list_themes()

    for preferred in ("norton_commander", "dark"):
        if preferred in available:
            start_theme = preferred
            break

    if not start_theme and available:
        start_theme = available[0]

    if start_theme:
        css = theme.load_theme(start_theme)
        if css:
            app.setStyleSheet(css)
    else:
        log.warning("Kein Theme gefunden – Fallback auf internes Stylesheet")

    # ── Hauptfenster ─────────────────────────────────────────
    win = MainWindow(
        log_engine=log,
        app=app,
        events=events,
        theme_node=theme,      # ThemeNode übergeben für Theme-Manager
    )
    win.show()
    app.exec()


if __name__ == "__main__":
    main()