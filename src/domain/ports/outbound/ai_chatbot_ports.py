from abc import ABC, abstractmethod
from typing import Union

class AI_ChatBotPort(ABC):
    """
    Abstracción de cliente Gemini/LLM para permitir reemplazo futuro.
    """

    @abstractmethod
    def generate_text(self, prompt: Union[str, list]) -> dict[str, str | bool]:
        """
        Genera texto a partir de un prompt.

        Args:
            prompt: Instrucción o pregunta para el modelo, en formato de str o audios.

        Returns:
            Diccionario con las claves:
                - success: bool indicando si la petición fue exitosa.
                - message: str con el contenido devuelto o el error.
        """
        raise NotImplementedError