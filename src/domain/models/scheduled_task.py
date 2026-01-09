from datetime import datetime
from src.domain.models.task import Task
from src.domain.models.task_status import TaskStatus
from src.domain.models.command import Command

class ScheduledTask(Task):
    """
    A task that executes at a specific time in the future.
    Example: Play music at 6:00 PM, Send reminder at 10:00 AM
    """
    
    def __init__(self, 
            command: Command, 
            scheduled_time: datetime, 
            priority: int = 0) -> None:
        super().__init__(command, priority)
        self._scheduled_time: datetime = scheduled_time
    
    def should_execute(self, now: datetime) -> bool:
        return now >= self._scheduled_time and self.is_pending()
    
    def next_run_at(self, now: datetime) -> datetime | None:
        return self._scheduled_time if self.is_pending() else None
    
    def on_execution_complete(self) -> None:
        self._status = TaskStatus.COMPLETED
        self._done_event.set()  # Signal that task is done