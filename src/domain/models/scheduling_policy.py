from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Optional


class ScheduleKind(str, Enum):
    IMMEDIATE = "immediate"
    AT = "at"
    EVERY = "every"
    CONTINUOUS = "continuous"


@dataclass(frozen=True)
class SchedulingPolicy:
    kind: ScheduleKind
    at: Optional[datetime] = None
    interval: Optional[timedelta] = None
    max_executions: Optional[int] = None
    condition: Optional[Callable[[], bool]] = None