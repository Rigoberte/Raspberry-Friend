from typing import Dict

class Command:
    def __init__(self, name: str, slots: Dict[str, str]):
        self._name = name
        self._args = slots

    def get_name(self) -> str:
        return str(self._name)

    def get_args(self) -> Dict[str, str]:
        return dict(self._args)

class CommandResult:
    def __init__(self, success: bool, message: str):
        self._success = success
        self._message = message

    def is_successful(self) -> bool:
        return bool(self._success)
    
    def get_message(self) -> str:
        return str(self._message)