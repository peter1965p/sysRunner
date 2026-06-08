import asyncio
import os
import shutil
from pathlib import Path


class FSNode:
    def __init__(self, logger, events):
        self.logger = logger
        self.events = events

    # ---------------------------------------------------------
    # Directory Listing
    # ---------------------------------------------------------
    async def list_dir(self, path: str):
        loop = asyncio.get_event_loop()

        def run():
            p = Path(path)
            if not p.exists():
                return []
            entries = []
            for item in p.iterdir():
                entries.append({
                    "name": item.name,
                    "path": str(item),
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else None
                })
            return entries

        result = await loop.run_in_executor(None, run)
        self.events.emit("fs.list", {"path": path, "entries": result})
        return result

    # ---------------------------------------------------------
    # Datei lesen
    # ---------------------------------------------------------
    async def read_file(self, path: str):
        loop = asyncio.get_event_loop()

        def run():
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        try:
            content = await loop.run_in_executor(None, run)
            self.events.emit("fs.read", {"path": path, "content": content})
            return content
        except Exception as e:
            self.logger.error(f"FSNode: Fehler beim Lesen → {e}")
            return None

    # ---------------------------------------------------------
    # Datei löschen
    # ---------------------------------------------------------
    async def delete(self, path: str):
        loop = asyncio.get_event_loop()

        def run():
            p = Path(path)
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                shutil.rmtree(p)

        try:
            await loop.run_in_executor(None, run)
            self.logger.info(f"FSNode: gelöscht → {path}")
            self.events.emit("fs.delete", {"path": path})
        except Exception as e:
            self.logger.error(f"FSNode: Fehler beim Löschen → {e}")

    # ---------------------------------------------------------
    # Datei kopieren
    # ---------------------------------------------------------
    async def copy(self, src: str, dst: str):
        loop = asyncio.get_event_loop()

        def run():
            shutil.copy2(src, dst)

        try:
            await loop.run_in_executor(None, run)
            self.logger.info(f"FSNode: kopiert → {src} → {dst}")
            self.events.emit("fs.copy", {"src": src, "dst": dst})
        except Exception as e:
            self.logger.error(f"FSNode: Fehler beim Kopieren → {e}")

    # ---------------------------------------------------------
    # Datei verschieben
    # ---------------------------------------------------------
    async def move(self, src: str, dst: str):
        loop = asyncio.get_event_loop()

        def run():
            shutil.move(src, dst)

        try:
            await loop.run_in_executor(None, run)
            self.logger.info(f"FSNode: verschoben → {src} → {dst}")
            self.events.emit("fs.move", {"src": src, "dst": dst})
        except Exception as e:
            self.logger.error(f"FSNode: Fehler beim Verschieben → {e}")
