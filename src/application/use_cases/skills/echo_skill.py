from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult

class EchoSkill(RobotSkill):
    def supported_commands(self) -> list[str]:
        return ["echo"]

    def handle(self, command: Command) -> CommandResult:
        text = command.get_args().get("text", "")
        return CommandResult(success=True, message=text)