# src/raspberry_friend/model/skill.py
from src.model.command.command import Command, CommandResult

class RobotSkill:
    """Interface for all Robot Skills."""
    def can_handle(self, command: Command) -> bool:
        raise NotImplementedError()

    def handle(self, command: Command) -> CommandResult:
        raise NotImplementedError()

class NullSkill(RobotSkill):
    """Null Object for RobotSkill when no skill matches."""
    def can_handle(self, command: Command) -> bool:
        return False

    def handle(self, command: Command) -> CommandResult:
        return CommandResult(False, f"No skill found to handle command '{command.get_name()}'")