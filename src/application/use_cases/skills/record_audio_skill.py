from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.microphone_ports import MicrophonePort


class RecordAudioSkill(RobotSkill):
    """Skill que graba audio desde el micrófono a un archivo WAV."""

    def __init__(self, mic_service: MicrophonePort, default_seconds: float = 5.0) -> None:
        super().__init__({"record-audio": "Graba audio desde el micrófono en un archivo WAV."})
        self._mic = mic_service
        self._default_seconds = default_seconds

    def handle(self, command: Command) -> CommandResult:
        args = command.get_args() or {}
        text = str(args.get("text", "")).strip()

        duration = self._default_seconds
        if text:
            first_token = text.split()[0]
            try:
                maybe_duration = float(first_token)
                if maybe_duration > 0:
                    duration = min(maybe_duration, 600.0)
            except ValueError:
                pass  # si no es número, usa el default

        result = self._mic.record(duration)
        if not result.get("success", False):
            return CommandResult(success=False, message=str(result.get("message", "No se pudo grabar audio")))

        path = result.get("path", "")
        message = result.get("message", "Grabación completada")
        extra = {"path": path} if path else {}
        return CommandResult(success=True, message=message, data=extra)
