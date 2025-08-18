# src/raspberry_friend/model/robot.py
from typing import List
from src.raspberry_friend.model.skill import RobotSkill, NullSkill
from src.raspberry_friend.model.command import Command, CommandResult

class Robot:
    """Main Robot class that manages skills and dispatches commands."""
    def __init__(self):
        self.skills: List[RobotSkill] = []

    def register(self, skill: RobotSkill):
        """Register a new skill."""
        self.skills.append(skill)

    def dispatch(self, command: Command) -> CommandResult:
        """Dispatch a command to the first skill that can handle it."""
        for skill in self.skills:
            if skill.can_handle(command):
                return skill.handle(command)
        return NullSkill().handle(command)