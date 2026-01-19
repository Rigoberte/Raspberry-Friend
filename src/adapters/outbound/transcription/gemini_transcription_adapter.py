from pathlib import Path
from google.genai import types as genai_types

from src.domain.ports.outbound.transcription_ports import TranscriptionPort
from src.adapters.outbound.ai_chatbot.gemini_adapter import GeminiAdapter
from src.domain.ports.outbound.ai_chatbot_ports import AI_ChatBotPort

class GeminiTranscriptionAdapter(TranscriptionPort):
    """Transcribe audio usando Google Gemini."""

    def __init__(self) -> None:
        self._ai: AI_ChatBotPort = GeminiAdapter()

    def transcribe(self, audio_path: str) -> dict[str, str | bool]:
        path = Path(audio_path or "").expanduser()
        if not path.exists() or not path.is_file():
            return {"success": False, "message": f"No se encontró el archivo: {path}"}

        try:
            audio_bytes = path.read_bytes()
            audio_part = genai_types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")

            response = self._ai.generate_text([
                audio_part,
                "Transcribe the audio to plain text. Return only the transcript.",
            ]) 

            return response
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "message": f"Error transcribiendo: {exc}"}