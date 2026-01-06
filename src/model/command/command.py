# src/raspberry_friend/model/command.py
from typing import Dict

class Command:
    """Represents a command to be executed by the Robot."""
    def __init__(self, name: str, args: Dict[str, str]):
        self.__name__ = name
        self.__args__ = args

    def get_name(self) -> str:
        return str(self.__name__)

    def get_args(self) -> Dict[str, str]:
        return dict(self.__args__)

class CommandResult:
    """Immutable result returned after executing a command."""
    def __init__(self, success: bool, message: str):
        self.success = success
        self.message = message