"""
PlaybackMonitorSkill: publica eventos de progreso de reproducción.
"""
from datetime import datetime

from src.application.use_cases.skills.skill import RobotSkill
from src.domain.events.music_events import PlaybackProgress
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.event_bus_ports import EventBusPort
from src.domain.ports.outbound.music_player_ports import MusicPlayerPort


class PlaybackMonitorSkill(RobotSkill):
    """
    Skill interna que monitorea el progreso de reproducción y publica eventos.
    No es llamada directamente por el usuario, sino por tareas continuas.
    """

    def __init__(self, player: MusicPlayerPort, event_bus: EventBusPort):
        super().__init__({"monitor-playback": "Monitor playback progress and publish events."})
        self._player = player
        self._event_bus = event_bus

    def handle(self, command: Command) -> CommandResult:
        if command.get_name() == "monitor-playback":
            return self._monitor_playback(command)
        
        return CommandResult(False, f"Unknown command: {command.get_name()}")

    def _monitor_playback(self, command: Command) -> CommandResult:
        args = command.get_args()
        path = args.get("path", "")
        track = args.get("track", "")
        duration_ms = int(args.get("duration_ms", 0))

        if not self._player.is_busy():
            return CommandResult(
                success=False,
                message="Playback stopped, monitoring should end."
            )

        position_ms = int(self._player.get_pos() or 0)

        position_s = position_ms / 1000 if position_ms else 0
        duration_s = duration_ms / 1000 if duration_ms else 0

        event = PlaybackProgress(
            path=path,
            track=track,
            position_ms=position_ms,
            duration_ms=duration_ms,
            occurred_at=datetime.now(),
        )
        self._event_bus.publish(event)

        return CommandResult(
            success=True,
            message=f"Progress: {position_s}s / {duration_s}s"
        )
