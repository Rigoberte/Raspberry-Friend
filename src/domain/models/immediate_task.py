from src.domain.models.task import Task
from src.domain.models.task_status import TaskStatus
from src.domain.models.command import Command

from datetime import datetime


class ImmediateTask(Task):
    """
    A task that executes immediately when processed by the scheduler.
    This is the default task type for synchronous command execution.
    """
    
    def __init__(self, command: Command, priority: int = 0) -> None:
        super().__init__(command, priority)
    
    def should_execute(self, now: datetime) -> bool:
        return self.is_pending()
    
    def next_run_at(self, now: datetime) -> datetime | None:
        return now if self.is_pending() else None
    
    def on_execution_complete(self) -> None:
        self._status = TaskStatus.COMPLETED
        self._done_event.set()  # Signal that task is done