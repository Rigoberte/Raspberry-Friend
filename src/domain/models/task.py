from abc import ABC, abstractmethod
from uuid import uuid4
import threading
from datetime import datetime, timezone, timedelta
from typing import Protocol

from src.domain.models.command import Command, CommandResult
from src.domain.models.task_status import TaskStatus
from src.domain.events.task_events import (
    TaskQueued,
    TaskStarted,
    TaskCompleted,
    TaskFailed,
    TaskCancelled
)

class CommandHandler(Protocol):
    def handle(self, command: Command) -> CommandResult: ...

class Task(ABC):
    def __init__(self, command: Command, priority: int = 0) -> None:
        self._id: str = str(uuid4())
        self._command: Command = command
        self._priority: int = priority
        
        self._status: TaskStatus = TaskStatus.PENDING
        self._result: CommandResult | None = None
        
        self._done_event = threading.Event() 
        self._state_lock = threading.Lock()

        self._created_at: datetime = datetime.now(timezone(timedelta(hours=-3)))
        
        self._domain_events: list = []

    @abstractmethod
    def should_execute(self, now: datetime) -> bool:
        """
        Determines if the task should be executed now.
        Each task type implements its own logic.
        """
        raise NotImplementedError()

    @abstractmethod
    def next_run_at(self, now: datetime) -> datetime | None:
        """When should the scheduler wake up next for this task? None if irrelevant/done."""
        raise NotImplementedError()

    @abstractmethod
    def on_execution_complete(self) -> None:
        """
        Called after task execution completes.
        Each task type defines what happens next (complete, reschedule, etc.)
        """
        raise NotImplementedError()
    
    @abstractmethod
    def get_type_of_task(self) -> str:
        """
        Returns a string representing the type of the task.
        """
        raise NotImplementedError()
    
    def get_id(self) -> str:
        return self._id
    
    def get_command(self) -> Command:
        return self._command
    
    def get_result(self) -> CommandResult:
        return self._result
    
    def collect_domain_events(self) -> list:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def _emit_event(self, event) -> None:
        self._domain_events.append(event)

    def execute(self, dispatcher: CommandHandler) -> None:
        with self._state_lock:
            if self._status != TaskStatus.EXECUTING:
                return
        
        self._emit_event(
            TaskStarted(
                task_id=self._id,
                command_name=self._command.get_name(),
                occurred_at=datetime.now(timezone(timedelta(hours=-3)))
            )
        )
        
        try:
            result = dispatcher.handle(self._command)
            self._result = result

            if result.is_successful():
                self.on_execution_complete()
                
                self._emit_event(
                    TaskCompleted(
                        task_id=self._id,
                        command_name=self._command.get_name(),
                        occurred_at=datetime.now(timezone(timedelta(hours=-3))),
                        success=True,
                        message=result.get_message(),
                        output=result.get_data()
                    )
                )
            else:
                self.__fail__(result)
        except Exception as e:
            error_result = CommandResult(
                success=False,
                message=f"Error ejecutando tarea: {str(e)}"
            )
            self.__fail__(error_result)
            return
        
    def try_claim(self) -> bool:
        with self._state_lock:
            if self.is_pending():
                self._status = TaskStatus.EXECUTING
                return True
            return False
        
    def stop(self) -> None: #TODO: revisar
        if not self.is_pending():
            raise ValueError(f"Cannot stop task with status {self._status}")
        self._status = TaskStatus.COMPLETED
        self._done_event.set()  # Signal completion

    def is_pending(self) -> bool:
        return self._status == TaskStatus.PENDING

    def is_done(self) -> bool:
        return self._status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
    
    def wait(self, timeout: float | None = None) -> bool:
        return self._done_event.wait(timeout)
    
    def cancel(self) -> None:
        with self._state_lock:
            if self.is_done():
                return
            
            self._status = TaskStatus.CANCELLED
            self._result = CommandResult(False, "Task cancelled")
            self._done_event.set()
            
            self._emit_event(
                TaskCancelled(
                    task_id=self._id,
                    command_name=self._command.get_name(),
                    occurred_at=datetime.now(timezone(timedelta(hours=-3))),
                    reason="Task cancelled by user"
                )
            )

    def __fail__(self, result: CommandResult) -> None:
        with self._state_lock:
            self._status = TaskStatus.FAILED
            self._result = result
            self._done_event.set()
            
            self._emit_event(
                TaskFailed(
                    task_id=self._id,
                    command_name=self._command.get_name(),
                    occurred_at=datetime.now(timezone(timedelta(hours=-3))),
                    error_message=result.get_message() if result else "Unknown error",
                    details={"success": False}
                )
            )