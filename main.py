import asyncio
from core.logging import LogEngine
from core.tasks import TaskEngine, Task
from core.events import EventBus
from core.registry import NodeRegistry
from nodes.docker_node import DockerNode
from nodes.fs_node import FSNode
from nodes.runner_node import RunnerNode
from nodes.db_node import DBNode


async def main():
    log = LogEngine()
    events = EventBus()
    registry = NodeRegistry()
    tasks = TaskEngine(log)

    log.info("SysRunner Core gestartet")

    # Worker starten
    asyncio.create_task(tasks.worker())

    # FS-Node registrieren

    fs = FSNode(log, events)
    registry.register("fs", fs)

    await fs.list_dir("/home/")

    # Runner-Node registrieren

    runner = RunnerNode(log, events)
    registry.register("runner", runner)

    # Beispiel: ls -la ausführen
    await runner.run("ls -la")

    # DB-Node registrieren
    db_node = DBNode(log, events)
    registry.register("db", db_node)

    await db_node.connect("sqlite:///test.db")
    await db_node.list_tables()

    # Docker-Node registrieren
    docker_node = DockerNode(log, events)
    registry.register("docker", docker_node)

    # Docker: Container-Liste abrufen
    await docker_node.list_containers()

    # Beispiel-Task
    async def demo():
        await asyncio.sleep(1)
        log.info("Demo-Task ausgeführt")

    await tasks.add(Task(name="demo", coro=demo))

    # Core am Leben halten
    await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
