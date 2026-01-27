from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PlaybackStarted:
    """Evento emitido cuando comienza la reproducción."""
    path: str
    track: str
    duration_ms: int
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class PlaybackStopped:
    """Evento emitido cuando se detiene la reproducción."""
    path: str
    track: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class PlaybackStateChanged:
    """Evento emitido cuando cambia el estado de reproduccion."""
    path: str
    track: str
    is_playing: bool
    position_ms: int
    duration_ms: int
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class PlaybackProgress:
    """Evento periodico con el progreso de la reproduccion."""
    path: str
    track: str
    position_ms: int
    duration_ms: int
    occurred_at: datetime
