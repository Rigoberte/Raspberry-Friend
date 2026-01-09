from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.models.command import CommandResult

@dataclass(frozen=True, slots=True)
class TaskEvent:
    task_id: str
    command_name: str
    occurred_at: datetime

@dataclass(frozen=True, slots=True)
class TaskQueued(TaskEvent):
    pass

@dataclass(frozen=True, slots=True)
class TaskStarted(TaskEvent):
    pass

@dataclass(frozen=True, slots=True)
class TaskCompleted(TaskEvent):
    result: Optional[CommandResult] = None

@dataclass(frozen=True, slots=True)
class TaskFailed(TaskEvent):
    result: Optional[CommandResult] = None

@dataclass(frozen=True, slots=True)
class TaskCancelled(TaskEvent):
    reason: str = "cancelled"