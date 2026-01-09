from datetime import datetime, timedelta
import threading
from src.domain.models.task import Task
from src.domain.models.task_status import TaskStatus
from src.domain.models.command import Command, CommandResult
from src.application.use_cases.skills.skill import RobotSkill


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
        self._next_execution: datetime = datetime.now() + check_interval
        
        self._max_executions: int | None = max_executions
        self._execution_count: int = 0

        self._execution_event = threading.Event()  # Signals each execution
    
    def should_execute(self) -> bool:
        if self._max_executions and self._execution_count >= self._max_executions:
            return False
        return datetime.now() >= self._next_execution and self.is_pending()
    
    def on_execution_complete(self) -> None:
        self._execution_count += 1
        self._execution_event.set()  # Signal this execution is done
        
        # Check if we've reached max executions
        if self._max_executions and self._execution_count >= self._max_executions:
            self._status = TaskStatus.COMPLETED
            self._done_event.set()  # Signal final completion
        else:
            # Schedule next execution
            self._next_execution = datetime.now() + self._check_interval
            self._status = TaskStatus.PENDING
            # Clear execution event for next round
            self._execution_event.clear()