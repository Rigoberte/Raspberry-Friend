from dataclasses import dataclass
from typing import Callable, Any

from src.domain.models.command import Command, CommandResult

@dataclass(frozen=True)
class WorkflowStep:
    name: str
    command: Callable[[dict[str, Any]], Command]
    on_success: Callable[[dict[str, Any], CommandResult], None] = lambda ctx, res: None