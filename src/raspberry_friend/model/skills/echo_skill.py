from src.raspberry_friend.model.robot import RobotSkill, Command, CommandResult

class EchoSkill(RobotSkill):
    """Skill that echoes back the text provided in the command."""
    
    def can_handle(self, command: Command) -> bool:
        """
        Determines if this skill can handle the given command.
        Only handles 'echo' command.
        """
        return command.name.lower() == "echo"

    def handle(self, command: Command) -> CommandResult:
        """
        Returns a CommandResult with the text from the command.
        """
        text = command.args.get("text", "")
        return CommandResult(success=True, message=text)