from enum import Enum
from uuid import uuid4
import threading
from src.domain.models.command import Command, CommandResult
from src.application.use_cases.skills.skill import RobotSkill

class TaskStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    def __init__(self, command: Command, handler: RobotSkill) -> None:
        self._id: str = str(uuid4())
        self._command: Command = command
        self._handler: RobotSkill = handler
        self._status: TaskStatus = TaskStatus.PENDING
        self._result: CommandResult | None = None
        self._priority: int = 0  # TODO: task priority for scheduling
        self._done_event = threading.Event()  # Event for efficient waiting

    def get_id(self) -> str:
        return str(self._id)

    def get_command(self) -> Command:
        return self._command

    def get_status(self) -> TaskStatus:
        return self._status

    def get_result(self) -> CommandResult | None:
        return self._result

    def start(self) -> None:
        if self._status != TaskStatus.PENDING:
            return # Only start if pending
        self._status = TaskStatus.EXECUTING

        try:
            result = self._handler.handle(self._command)

            if result.is_successful():
                self.__complete__(result)
            else:
                self.__fail__(result)
        except Exception as e:
            # Capturar errores inesperados
            error_result = CommandResult(
                success=False,
                message=f"Error ejecutando tarea: {str(e)}"
            )
            self.__fail__(error_result)
            return

    def __complete__(self, result: CommandResult) -> None:
        if self._status != TaskStatus.EXECUTING:
            raise ValueError(f"Cannot complete task with status {self._status}")
        self._status = TaskStatus.COMPLETED
        self._result = result
        self._done_event.set()  # Signal completion

    def __fail__(self, result: CommandResult) -> None:
        if self._status != TaskStatus.EXECUTING:
            raise ValueError(f"Cannot fail task with status {self._status}")
        self._status = TaskStatus.FAILED
        self._result = result
        self._done_event.set()  # Signal completion (with error)

    def is_pending(self) -> bool:
        return self._status == TaskStatus.PENDING

    def is_executing(self) -> bool:
        return self._status == TaskStatus.EXECUTING

    def is_completed(self) -> bool:
        return self._status == TaskStatus.COMPLETED

    def is_failed(self) -> bool:
        return self._status == TaskStatus.FAILED

    def is_done(self) -> bool:
        return self.is_completed() or self.is_failed()

    def wait(self, timeout: float | None = None) -> bool:
        return self._done_event.wait(timeout)

    def __repr__(self) -> str:
        return f"Task({self._id}, cmd={self._command.get_name()}, status={self._status.value})"
