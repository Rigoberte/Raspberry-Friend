from src.domain.models.command import Command
from src.application.use_cases.skills.skill import RobotSkill, UnknownSkill

class SkillRegistry:
    def __init__(self) -> None:
        self._by_command: dict[str, RobotSkill] = {}
    
    def register(self, skill: RobotSkill) -> None:
        for command in skill.supported_commands():
            if command in self._by_command:
                raise ValueError(f"Command '{command}' is already registered to another skill.")
            self._by_command[command] = skill
    
    def get_skill(self, command: Command) -> RobotSkill: # TODO: Remove getter
        return self._by_command.get(command.get_name(), UnknownSkill())
    
    def list_skills(self) -> list[str]:
        return sorted(self._by_command.keys())