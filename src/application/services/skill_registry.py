from typing import Protocol
from src.domain.models.command import Command, CommandResult
from src.application.use_cases.skills.skill import RobotSkill

class SkillRegistry:
    def __init__(self) -> None:
        self._skills: list[RobotSkill] = []
    
    def register(self, skill: RobotSkill) -> None:
        self._skills.append(skill)
    
    def get(self, command: Command) -> RobotSkill | None:
        for skill in self._skills:
            if skill.can_handle(command):
                return skill
        return None
    
    def list(self) -> list[str]:
        # Lista todos los comandos de todos los skills
        commands = []
        for skill in self._skills:
            commands.extend(skill.supported_commands())
        return sorted(commands)