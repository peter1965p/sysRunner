from pathlib import Path


class ThemeNode:
    """
    Verwaltet QSS-Themes für SysRunner.
    Sucht in ui/themes/ nach .qss Dateien.
    Sendet 'theme.changed' Event mit name + css Payload.
    """

    def __init__(self, logger, events, themes_dir: str = "ui/themes"):
        self.logger     = logger
        self.events     = events
        self.themes_dir = Path(themes_dir)
        self.current: str | None = None

    def list_themes(self) -> list[str]:
        """Gibt alle verfügbaren Theme-Namen (ohne .qss) zurück."""
        if not self.themes_dir.exists():
            self.logger.warning(
                f"ThemeNode: Themes-Verzeichnis nicht gefunden → {self.themes_dir}")
            return []
        return sorted(f.stem for f in self.themes_dir.glob("*.qss"))

    def load_theme(self, name: str) -> str | None:
        """Lädt ein Theme, gibt CSS zurück, feuert Event."""
        path = self.themes_dir / f"{name}.qss"
        if not path.exists():
            self.logger.warning(f"ThemeNode: Theme nicht gefunden → {path}")
            return None
        css = path.read_text(encoding="utf-8")
        self.current = name
        self.logger.info(f"ThemeNode: Theme geladen → {name}")
        self.events.emit("theme.changed", {"name": name, "css": css})
        return css

    def reload_current(self) -> str | None:
        """Aktuelles Theme neu laden."""
        if self.current:
            return self.load_theme(self.current)
        return None