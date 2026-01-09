from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Any, Optional

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

@dataclass(frozen=True, slots=True)
class CommandResult:
    success: bool
    message: str
    code: str = "OK"
    details: Optional[Any] = None

    def is_successful(self) -> bool:
        return bool(self.success)
    
    def get_message(self) -> str:
        return str(self.message)