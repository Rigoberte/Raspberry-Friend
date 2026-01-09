import time

from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult


class WaitSkill(RobotSkill):
    def __init__(self):
        super().__init__({"wait": "Wait for a specified duration in seconds."})
        
    def handle(self, command: Command) -> CommandResult:
        try:
            duration = float(command.get_args().get("text", 0))
            time.sleep(duration)
            return CommandResult(True, f"Waited for {duration} seconds.")
        except (ValueError, TypeError):
            return CommandResult(False, "Invalid or missing 'duration' argument for wait command.")