from abc import ABC, abstractmethod
from typing import Callable, Any

class TaskExecutorPort(ABC):
    """
    Puerto para la ejecución asíncrona de tareas.
    Define el contrato para cualquier implementación de executor (ThreadPoolExecutor, ProcessPoolExecutor, etc.)
    """
    
    @abstractmethod
    def submit(self, fn: Callable, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def shutdown(self, wait: bool = True, cancel_futures: bool = False) -> None:
        raise NotImplementedError
