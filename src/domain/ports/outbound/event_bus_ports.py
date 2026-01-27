from abc import ABC, abstractmethod
from typing import Callable, Type, TypeVar

T = TypeVar("T")

class EventBusPort(ABC):
    """
    Puerto para el EventBus en la capa de dominio.
    Define el contrato que debe cumplir cualquier implementación de EventBus.
    """
    
    @abstractmethod
    def publish(self, event: object) -> None:
        """Publica un evento en el bus."""
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, event_type: Type[T], handler: Callable[[T], None]) -> None:
        """Suscribe un handler a un tipo de evento."""
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """Detiene el procesamiento del bus de eventos."""
        raise NotImplementedError
