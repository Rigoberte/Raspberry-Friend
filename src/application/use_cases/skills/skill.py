from abc import ABC, abstractmethod
from src.domain.models.command import Command, CommandResult

class RobotSkill(ABC):
    """Interface for all Robot Skills."""
    def can_handle(self, command: Command) -> bool:
        return command.get_name().lower() in self.supported_commands()
    
    @abstractmethod
    def supported_commands(self) -> list[str]:
        pass

    @abstractmethod
    def handle(self, command: Command) -> CommandResult:
        raise NotImplementedError()

class NullSkill(RobotSkill):
    def supported_commands(self) -> list[str]:
        return []

    def handle(self, command: Command) -> CommandResult:
        return CommandResult(False, f"No skill found to handle command '{command.get_name()}'")