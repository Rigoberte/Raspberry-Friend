import os
from pathlib import Path
from typing import Optional

from src.domain.ports.outbound.transcription_ports import TranscriptionPort


class GeminiTranscriptionAdapter(TranscriptionPort):
    """Transcribe audio usando Google Gemini."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash",
    ) -> None:
        env_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
        self.api_key = api_key or env_key or ""
        self.model = model
        self._client = None

    def transcribe(self, audio_path: str) -> dict[str, str | bool]:
        path = Path(audio_path or "").expanduser()
        if not path.exists() or not path.is_file():
            return {"success": False, "message": f"No se encontró el archivo: {path}"}

        try:
            client = self._get_client()
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "message": f"Error configurando Gemini: {exc}"}

        try:
            from google.genai import types as genai_types
        except Exception as exc:  # noqa: BLE001
            return {
                "success": False,
                "message": "Dependencia google-genai no instalada o corrupta. Ejecuta 'pip install google-genai'.",
            }

        try:
            audio_bytes = path.read_bytes()
            audio_part = genai_types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")

            response = client.models.generate_content(
                model=self.model,
                contents=[
                    audio_part,
                    "Transcribe the audio to plain text. Return only the transcript.",
                ],
            )

            text_parts: list[str] = []
            candidates = getattr(response, "candidates", []) or []
            for cand in candidates:
                content = getattr(cand, "content", None)
                parts = getattr(content, "parts", None) if content else None
                if not parts:
                    continue
                for part in parts:
                    txt = getattr(part, "text", None)
                    if txt:
                        text_parts.append(txt)

            if not text_parts and hasattr(response, "text"):
                maybe_text = getattr(response, "text")
                if maybe_text:
                    text_parts.append(str(maybe_text))

            transcript = "\n".join(text_parts).strip() or "(sin texto)"
            return {"success": True, "message": transcript, "path": str(path)}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "message": f"Error transcribiendo: {exc}"}

    def _get_client(self):
        if self._client is not None:
            return self._client

        api_key = self.api_key
        if api_key is not None and hasattr(api_key, "value"):
            api_key = api_key.value
        if not isinstance(api_key, str):
            api_key = str(api_key) if api_key is not None else ""
        api_key = api_key.strip()
        if not api_key:
            raise ValueError("Falta la API key de Gemini. Define GOOGLE_API_KEY o pásala al adapter.")

        try:
            from google import genai
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(
                "Dependencia google-genai no instalada. Ejecuta 'pip install google-genai'."
            ) from exc

        self._client = genai.Client(api_key=api_key)
        return self._client
