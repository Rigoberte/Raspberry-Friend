from datetime import datetime, timedelta, timezone
import threading
from src.domain.models.task import Task
from src.domain.models.task_status import TaskStatus
from src.domain.models.command import Command


class RecurringTask(Task):
    """
    A task that executes repeatedly at a fixed interval.
    Example: Check weather every 30 minutes, Report status every hour
    """
    
    def __init__(self, 
                command: Command, 
                check_interval: timedelta, 
                max_executions: int | None = None, 
                priority: int = 0) -> None:
        
        super().__init__(command, priority)

        self._check_interval: timedelta = check_interval
        self._next_execution: datetime = datetime.now(timezone(timedelta(hours=-3))) + check_interval
        
        self._max_executions: int | None = max_executions
        self._execution_count: int = 0

        self._execution_event = threading.Event()  # Signals each execution
    
    def should_execute(self, now: datetime) -> bool:
        if self._max_executions and self._execution_count >= self._max_executions:
            return False
        return now >= self._next_execution and self.is_pending()
    
    def next_run_at(self, now: datetime) -> datetime | None:
        if self._max_executions and self._execution_count >= self._max_executions:
            return None
        return self._next_execution if self.is_pending() else None
    
    def on_execution_complete(self) -> None:
        self._execution_count += 1
        if self._max_executions and self._execution_count >= self._max_executions:
            self._status = TaskStatus.COMPLETED
            self._done_event.set()  # Signal that task is done
        else:
            self._status = TaskStatus.PENDING
            self._next_execution = datetime.now(timezone(timedelta(hours=-3))) + self._check_interval
            self._execution_event.set()  # Signal that execution occurred

    def get_type_of_task(self) -> str:
        return "Recurring Task"