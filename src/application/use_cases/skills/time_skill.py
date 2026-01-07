from datetime import datetime
from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult

class TimeSkill(RobotSkill):
    def supported_commands(self) -> list[str]:
        return ["time"]

    def handle(self, command: Command) -> CommandResult:
        """Return a CommandResult with the current time as HH:MM string."""
        now = datetime.now().strftime("%H:%M")
        return CommandResult(True, f"Current time is {now}")
