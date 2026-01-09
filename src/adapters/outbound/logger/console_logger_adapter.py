from __future__ import annotations
from typing import Any, Mapping, Optional

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import ANSI

from src.domain.ports.outbound.logger_ports import LoggerPort

class ConsoleLoggerAdapter(LoggerPort):
    def __init__(self, level: str = "INFO") -> None:
        self._level = level.upper()

    def _should_log(self, level: str) -> bool:
        order = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
        return order[level] >= order.get(self._level, 20)

    def _fmt(self, level: str, message: str, extra: Optional[Mapping[str, Any]]) -> str:
        if extra:
            extras = " ".join(f"{k}={v}" for k, v in extra.items())
            return f"{level} {message} ({extras})"
        return f"{level} {message}"
    
    def log(self, message):
        self.info(message)

    def debug(self, message: str, *, extra=None) -> None:
        if self._should_log("DEBUG"):
            print_formatted_text(ANSI(self._fmt("[DEBUG]", message, extra)))

    def info(self, message: str, *, extra=None) -> None:
        if self._should_log("INFO"):
            print_formatted_text(ANSI(self._fmt("[INFO]", message, extra)))

    def warning(self, message: str, *, extra=None) -> None:
        if self._should_log("WARNING"):
            print_formatted_text(ANSI(self._fmt("[WARN]", message, extra)))

    def error(self, message: str, *, extra=None) -> None:
        if self._should_log("ERROR"):
            print_formatted_text(ANSI(self._fmt("[ERROR]", message, extra)))
