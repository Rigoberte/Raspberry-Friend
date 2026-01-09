from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult

class EchoSkill(RobotSkill):
    def __init__(self):
        super().__init__({"echo": "Echo the provided text."})

    def handle(self, command: Command) -> CommandResult:
        text = command.get_args().get("text", "")
        return CommandResult(success=True, message=text)