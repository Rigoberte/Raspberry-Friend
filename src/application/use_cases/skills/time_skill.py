from datetime import datetime, timezone, timedelta
from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult

class TimeSkill(RobotSkill):
    def __init__(self):
        super().__init__({"time": "Get the current time."})
    
    def handle(self, command: Command) -> CommandResult:
        """Return a CommandResult with the current time as HH:MM string."""
        now = datetime.now(timezone(timedelta(hours=-3))).strftime("%H:%M")
        return CommandResult(True, f"Current time is {now}")
