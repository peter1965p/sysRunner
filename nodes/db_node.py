import asyncio
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

class DBNode:
    def __init__(self, logger, events):
        self.logger = logger
        self.events = events
        self.engine = None

    # ---------------------------------------------------------
    # Verbindung herstellen
    # ---------------------------------------------------------
    async def connect(self, url: str):
        loop = asyncio.get_event_loop()

        def run():
            self.engine = create_engine(url, future=True)

        try:
            await loop.run_in_executor(None, run)
            self.logger.info(f"DBNode: Verbunden mit {url}")
            self.events.emit("db.connected", {"url": url})
        except SQLAlchemyError as e:
            self.logger.error(f"DBNode: Fehler bei Verbindung → {e}")

    # ---------------------------------------------------------
    # Tabellen auflisten
    # ---------------------------------------------------------
    async def list_tables(self):
        if not self.engine:
            return []

        loop = asyncio.get_event_loop()

        def run():
            inspector = inspect(self.engine)
            return inspector.get_table_names()

        tables = await loop.run_in_executor(None, run)
        self.events.emit("db.tables", tables)
        return tables

    # ---------------------------------------------------------
    # Spalten einer Tabelle
    # ---------------------------------------------------------
    async def list_columns(self, table: str):
        if not self.engine:
            return []

        loop = asyncio.get_event_loop()

        def run():
            inspector = inspect(self.engine)
            return inspector.get_columns(table)

        columns = await loop.run_in_executor(None, run)
        self.events.emit("db.columns", {"table": table, "columns": columns})
        return columns

    # ---------------------------------------------------------
    # Daten-Preview (LIMIT 100)
    # ---------------------------------------------------------
    async def preview(self, table: str, limit: int = 100):
        if not self.engine:
            return []

        loop = asyncio.get_event_loop()

        def run():
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM {table} LIMIT {limit}"))
                return [dict(row) for row in result]

        rows = await loop.run_in_executor(None, run)
        self.events.emit("db.preview", {"table": table, "rows": rows})
        return rows

    # ---------------------------------------------------------
    # SQL ausführen
    # ---------------------------------------------------------
    async def query(self, sql: str):
        if not self.engine:
            return []

        loop = asyncio.get_event_loop()

        def run():
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                try:
                    return [dict(row) for row in result]
                except:
                    return []

        rows = await loop.run_in_executor(None, run)
        self.events.emit("db.query", {"sql": sql, "rows": rows})
        return rows
