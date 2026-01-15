from pathlib import Path

from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.transcription_ports import TranscriptionPort


class TranscribeSkill(RobotSkill):
    """Skill que transcribe un archivo WAV usando el servicio configurado."""

    def __init__(self, stt_service: TranscriptionPort):
        super().__init__({"transcribe": "Transcribe un archivo WAV a texto."})
        self._stt = stt_service

    def handle(self, command: Command) -> CommandResult:
        args = command.get_args() or {}
        text = str(args.get("text", "")).strip()
        if not text:
            return CommandResult(
                success=False,
                message="Debes indicar la ruta del WAV. Ej: 'transcribe user_data/media/recording.wav'",
            )

        path = Path(text).expanduser()
        result = self._stt.transcribe(str(path))
        if not result.get("success", False):
            return CommandResult(success=False, message=str(result.get("message", "No se pudo transcribir")))

        transcript = str(result.get("message", "")).strip()
        data = {"transcript": transcript, "path": result.get("path", str(path))}
        return CommandResult(success=True, message=transcript, data=data)
