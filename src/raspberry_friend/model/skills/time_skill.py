from datetime import datetime
from src.raspberry_friend.model.skill import RobotSkill
from src.raspberry_friend.model.command import Command, CommandResult

class TimeSkill(RobotSkill):
    """Skill that returns the current time."""

    def can_handle(self, command: Command) -> bool:
        """Return True if command is 'time'."""
        return command.name.lower() == "time"

    def handle(self, command: Command) -> CommandResult:
        """Return a CommandResult with the current time as HH:MM string."""
        now = datetime.now().strftime("%H:%M")
        return CommandResult(True, f"Current time is {now}")
