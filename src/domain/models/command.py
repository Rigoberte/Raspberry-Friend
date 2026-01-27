from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Any, Optional, Dict

def normalize_command_name(name: str) -> str:
    return name.strip().lower()

@dataclass(frozen=True, slots=True)
class Command:
    _name: str
    _args: Mapping[str, Any]
    
    def __post_init__(self):
        object.__setattr__(self, '_name', normalize_command_name(self._name))
        object.__setattr__(self, '_args', MappingProxyType(self._args))
    
    def get_name(self) -> str:
        return str(self._name)

    def get_args(self) -> Mapping[str, Any]:
        return dict(self._args)

class CommandResult:
    def __init__(self, success: bool, message: str, data: Optional[Dict[str, Any]] = None):
        self._success = success
        self._message = message
        self._data = data or {}

    def is_successful(self) -> bool:
        return bool(self._success)
    
    def get_message(self) -> str:
        return str(self._message)
    
    def get_data(self) -> Dict[str, Any]:
        return dict(self._data)