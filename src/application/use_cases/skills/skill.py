from abc import ABC, abstractmethod
from src.domain.models.command import Command, CommandResult

class RobotSkill(ABC):
    def __init__(self, commands: dict[str, str]) -> None:
        self._commands = commands

    def can_handle(self, command: Command) -> bool:
        return command.get_name().lower() in self._commands.keys()
    
    def supported_commands(self) -> list[str]:
        return list(self._commands.keys())

    @abstractmethod
    def handle(self, command: Command) -> CommandResult:
        raise NotImplementedError()

class NullSkill(RobotSkill):
    def __init__(self) -> None:
        super().__init__({})

    def handle(self, command: Command) -> CommandResult:
        return CommandResult(False, f"No skill found to handle command '{command.get_name()}'")