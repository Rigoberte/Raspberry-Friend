from domain.models.command import Command
from src.ports.inbound.command.commandResult import CommandResult

def handle(command: Command) -> CommandResult:
    return CommandResult(success=True, message="Hello from assistant_api")