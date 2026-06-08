import asyncio
import subprocess
from pathlib import Path


class RunnerNode:
    def __init__(self, logger, events):
        self.logger = logger
        self.events = events

    # ---------------------------------------------------------
    # Command ausführen (mit Live-Output)
    # ---------------------------------------------------------
    async def run(self, cmd: str, cwd: str = None):
        self.logger.info(f"RunnerNode: Starte → {cmd}")

        process = await asyncio.create_subprocess_shell(
            cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Live-Output streamen
        asyncio.create_task(self._stream_output(process.stdout, "stdout"))
        asyncio.create_task(self._stream_output(process.stderr, "stderr"))

        exit_code = await process.wait()

        self.logger.info(f"RunnerNode: Beendet → {cmd} (Exit {exit_code})")
        self.events.emit("runner.exit", {"cmd": cmd, "exit_code": exit_code})

        return exit_code

    # ---------------------------------------------------------
    # Output-Streamer
    # ---------------------------------------------------------
    async def _stream_output(self, stream, stream_type: str):
        while True:
            line = await stream.readline()
            if not line:
                break

            text = line.decode("utf-8").rstrip()
            self.events.emit("runner.output", {
                "type": stream_type,
                "line": text
            })

    # ---------------------------------------------------------
    # Datei/Skript ausführen
    # ---------------------------------------------------------
    async def run_script(self, path: str):
        p = Path(path)
        if not p.exists():
            self.logger.error(f"RunnerNode: Script nicht gefunden → {path}")
            return -1

        if p.suffix == ".py":
            return await self.run(f"python {path}")

        if p.suffix in [".sh", ".bash"]:
            return await self.run(f"bash {path}")

        # Fallback: direkt ausführen
        return await self.run(str(path))

