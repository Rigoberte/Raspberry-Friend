# src/raspberry_friend/model/command.py
from typing import Dict

class Command:
    """Represents a command to be executed by the Robot."""
    def __init__(self, name: str, args: Dict[str, str]):
        self.name = name
        self.args = args

class CommandResult:
    """Immutable result returned after executing a command."""
    def __init__(self, success: bool, message: str):
        self.success = success
        self.message = message