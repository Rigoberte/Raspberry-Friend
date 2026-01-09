from datetime import datetime, timedelta
from typing import Callable
import threading
from src.domain.models.task import Task
from src.domain.models.task_status import TaskStatus
from src.domain.models.command import Command
from src.application.use_cases.skills.skill import RobotSkill


class ContinuousTask(Task):
    """
    A task that continuously monitors a condition and executes when the condition is met.
    The task remains active and checks the condition at regular intervals.
    Example: Monitor temperature and alert if > 30°C, Check disk space every 5 minutes
    """
    
    def __init__(self, 
                command: Command, 
                check_interval: timedelta, 
                condition_checker: Callable[[], bool],
                max_executions: int | None = None, 
                priority: int = 0) -> None:
        
        super().__init__(command, priority)
        
        self._check_interval: timedelta = check_interval
        self._next_execution: datetime = datetime.now() + check_interval
        
        self._max_executions: int | None = max_executions
        self._execution_count: int = 0
        
        self._condition_checker: Callable[[], bool] = condition_checker
        
        self._execution_event = threading.Event()  # Signals each execution
    
    def should_execute(self) -> bool:
        """
        Execute if:
        1. It's time for the next check
        2. The condition is met
        3. Not exceeded max executions
        """
        if not self.is_pending():
            return False
        
        if self._max_executions and self._execution_count >= self._max_executions:
            return False
        
        if datetime.now() < self._next_execution:
            return False
        
        self._next_execution = datetime.now() + self._check_interval
        
        try:
            return self._condition_checker()
        except Exception:
            # If condition checker fails, don't execute
            return False
    
    def on_execution_complete(self) -> None:
        self._execution_count += 1
        self._execution_event.set()  # Signal this execution is done
        
        if self._max_executions and self._execution_count >= self._max_executions:
            self._status = TaskStatus.COMPLETED
            self._done_event.set()  # Signal final completion
        else:
            self._status = TaskStatus.PENDING
            self._execution_event.clear()
