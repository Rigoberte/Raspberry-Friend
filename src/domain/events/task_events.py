from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

@dataclass(frozen=True, slots=True)
class TaskEvent:
    """Evento base del dominio para tareas."""
    task_id: str
    command_name: str
    occurred_at: datetime

@dataclass(frozen=True, slots=True)
class TaskQueued(TaskEvent):
    """Evento emitido cuando una tarea es encolada."""
    pass

@dataclass(frozen=True, slots=True)
class TaskStarted(TaskEvent):
    """Evento emitido cuando una tarea comienza su ejecución."""
    pass

@dataclass(frozen=True, slots=True)
class TaskCompleted(TaskEvent):
    """Evento emitido cuando una tarea se completa exitosamente."""
    success: bool = True
    message: Optional[str] = None
    output: Optional[Any] = None

@dataclass(frozen=True, slots=True)
class TaskFailed(TaskEvent):
    """Evento emitido cuando una tarea falla."""
    error_message: str = ""
    details: Optional[dict] = None

@dataclass(frozen=True, slots=True)
class TaskCancelled(TaskEvent):
    """Evento emitido cuando una tarea es cancelada."""
    reason: str = "cancelled"