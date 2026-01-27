from abc import ABC, abstractmethod


class TranscriptionPort(ABC):
    """Abstracción para transcribir audio a texto."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> dict[str, str | bool]:
        """
        Transcribe un archivo de audio.

        Returns:
            dict con claves:
                success: bool
                message: texto transcrito o error
                path: ruta del audio usado (opcional)
        """
        raise NotImplementedError
