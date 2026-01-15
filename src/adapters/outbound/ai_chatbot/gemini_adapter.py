from typing import Optional

from src.domain.ports.outbound.ai_chatbot_ports import AI_ChatBotPort


class GeminiAdapter(AI_ChatBotPort):
    """
    Implementación de AI_ChatBotPort usando la librería google-genai.
    Diseñado para poder reemplazarse por otro proveedor (e.g., ChatGPT) sin
    cambiar el resto de la aplicación.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-001",
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._client = None

    def generate_text(self, prompt: str) -> dict[str, str | bool]:
        if not prompt or not prompt.strip():
            return {
                "success": False,
                "message": "El prompt no puede estar vacío. Ejemplo: 'gemini escribe un poema'.",
            }

        try:
            client = self._get_client()
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "message": f"Error configurando Gemini: {exc}"}

        try:
            response = client.models.generate_content(
                model=self.model,
                contents=[prompt],
            )

            text_chunks: list[str] = []

            candidates = getattr(response, "candidates", []) or []
            for candidate in candidates:
                content = getattr(candidate, "content", None)
                parts = getattr(content, "parts", None) if content else None
                if not parts:
                    continue
                for part in parts:
                    text = getattr(part, "text", None)
                    if text:
                        text_chunks.append(text)

            if not text_chunks and hasattr(response, "text"):
                maybe_text = getattr(response, "text")
                if maybe_text:
                    text_chunks.append(str(maybe_text))

            message = "\n".join(text_chunks).strip() or "Gemini no devolvió contenido."
            return {"success": True, "message": message}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "message": f"Error llamando a Gemini: {exc}"}

    def _get_client(self):
        if self._client is not None:
            return self._client

        # Admitir Enum u otros tipos y convertirlos a string
        api_key = self.api_key
        if api_key is not None and hasattr(api_key, "value"):
            api_key = api_key.value
        if not isinstance(api_key, str):
            api_key = str(api_key) if api_key is not None else ""
        if not api_key.strip():
            raise ValueError(
                "Falta la API key de Gemini. Define GOOGLE_API_KEY (recomendado) o GOOGLE_GENAI_API_KEY, o pásala al adapter."
            )

        try:
            from google import genai
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(
                "Dependencia google-genai no instalada. Ejecuta 'pip install google-genai'."
            ) from exc

        self._client = genai.Client(api_key=api_key.strip())
        return self._client
