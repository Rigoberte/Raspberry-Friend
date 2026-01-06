from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult

class EchoSkill(RobotSkill):
    """Skill that echoes back the text provided in the command."""
    
    def can_handle(self, command: Command) -> bool:
        """
        Determines if this skill can handle the given command.
        Only handles 'echo' command.
        """
        return command.get_name().lower() == "echo"

    def handle(self, command: Command) -> CommandResult:
        """
        Returns a CommandResult with the text from the command.
        """
        text = command.get_args().get("text", "")
        return CommandResult(success=True, message=text)