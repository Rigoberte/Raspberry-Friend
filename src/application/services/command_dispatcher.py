from src.application.services.skill_registry import SkillRegistry
from src.domain.models.command import Command
from src.domain.models.command import CommandResult

class CommandDispatcher:
    def __init__(self, registry: SkillRegistry):
        self._registry = registry

    def handle(self, command: Command) -> CommandResult:
        skill = self._registry.get_skill(command)
        return skill.handle(command)