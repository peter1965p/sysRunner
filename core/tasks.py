import asyncio
from dataclasses import dataclass

@dataclass
class Task:
    name: str
    coro: callable
    status: str = "pending"

class TaskEngine:
    def __init__(self, logger):
        self.queue = asyncio.Queue()
        self.logger = logger

    async def add(self, task: Task):
        await self.queue.put(task)
        self.logger.info(f"Task queued: {task.name}")

    async def worker(self):
        while True:
            task = await self.queue.get()
            task.status = "running"
            self.logger.info(f"Task started: {task.name}")

            try:
                await task.coro()
                task.status = "done"
                self.logger.info(f"Task finished: {task.name}")
            except Exception as e:
                task.status = "error"
                self.logger.info(f"Task failed: {task.name} → {e}")

            self.queue.task_done()
