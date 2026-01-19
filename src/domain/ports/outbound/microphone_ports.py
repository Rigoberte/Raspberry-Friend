from abc import ABC, abstractmethod


class MicrophonePort(ABC):
    """Abstracción para captura de audio desde un micrófono."""

    @abstractmethod
    def is_available(self) -> bool:
        """Devuelve True si hay algún dispositivo de entrada disponible."""
        raise NotImplementedError

    @abstractmethod
    def record(self, duration_sec: float) -> dict[str, str | bool]:
        """
        Graba audio por la cantidad de segundos indicada.

        Returns:
            dict con claves:
                success: bool
                message: str descriptivo
                path: ruta del archivo generado (si success)
        """
        raise NotImplementedError

    @abstractmethod
    def start_recording(self) -> dict[str, str | bool]:
        """
        Inicia grabación no-bloqueante (debe llamarse desde eventos GUI).

        Returns:
            dict con claves:
                success: bool
                message: str descriptivo
        """
        raise NotImplementedError
    
    @abstractmethod
    def stop_recording(self) -> dict[str, str | bool]:
        """
        Detiene la grabación iniciada con start_recording.

        Returns:
            dict con claves:
                success: bool
                message: str descriptivo
        """
        raise NotImplementedError
