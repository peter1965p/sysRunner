import asyncio
from python_on_whales import docker
from python_on_whales.exceptions import DockerException

class DockerNode:
    def __init__(self, logger, events):
        self.logger = logger
        self.events = events

        try:
            # Testverbindung
            docker.version()
            self.logger.info("DockerNode: python-on-whales verbunden")
        except DockerException as e:
            self.logger.info(f"DockerNode: Fehler beim Verbinden → {e}")

    # ---------------------------------------------------------
    # Container-Liste
    # ---------------------------------------------------------
    async def list_containers(self, all=False):
        loop = asyncio.get_event_loop()

        def run():
            return docker.ps(all=all)

        containers = await loop.run_in_executor(None, run)

        result = [
            {
                "id": c.id[:12],
                "name": c.name,
                "status": c.state.status,
                "image": c.image
            }
            for c in containers
        ]

        self.events.emit("docker.containers", result)
        return result

    # ---------------------------------------------------------
    # Container starten
    # ---------------------------------------------------------
    async def start(self, name):
        await self._action(name, docker.start, "start")

    # ---------------------------------------------------------
    # Container stoppen
    # ---------------------------------------------------------
    async def stop(self, name):
        await self._action(name, docker.stop, "stop")

    # ---------------------------------------------------------
    # Container neu starten
    # ---------------------------------------------------------
    async def restart(self, name):
        await self._action(name, docker.restart, "restart")

    # ---------------------------------------------------------
    # Gemeinsame Action-Logik
    # ---------------------------------------------------------
    async def _action(self, name, fn, action):
        loop = asyncio.get_event_loop()

        def run():
            fn(name)

        try:
            await loop.run_in_executor(None, run)
            self.logger.info(f"DockerNode: {action} → {name}")
            self.events.emit(f"docker.{action}", {"name": name})
        except Exception as e:
            self.logger.info(f"DockerNode: Fehler bei {action} → {e}")

    # ---------------------------------------------------------
    # Logs streamen
    # ---------------------------------------------------------
    async def logs(self, name):
        loop = asyncio.get_event_loop()

        def run():
            return docker.logs(name, follow=True, stream=True)

        log_stream = await loop.run_in_executor(None, run)

        for line in log_stream:
            text = line.decode("utf-8").rstrip()
            self.events.emit("docker.log", {"name": name, "line": text})
            await asyncio.sleep(0)
