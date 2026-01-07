from src.domain.models.command import Command
from src.application.use_cases.skills.skill import RobotSkill, NullSkill

class SkillRegistry:
    def __init__(self) -> None:
        self._skills: list[RobotSkill] = []
    
    def register(self, skill: RobotSkill) -> None:
        self._skills.append(skill)
    
    def get_skill(self, command: Command) -> RobotSkill: # TODO: Remove getter
        for skill in self._skills:
            if skill.can_handle(command):
                return skill
        return NullSkill()
    
    def list_skills(self) -> list[str]:
        commands = []
        for skill in self._skills:
            commands.extend(skill.supported_commands())
        return sorted(commands)