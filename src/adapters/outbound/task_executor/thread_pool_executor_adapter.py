from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor
from typing import Callable, Any

from src.domain.ports.outbound.task_executor_ports import TaskExecutorPort


class ThreadPoolExecutorAdapter(TaskExecutorPort):
    """
    Adaptador de infraestructura para ThreadPoolExecutor.
    Implementa el puerto TaskExecutorPort usando ThreadPoolExecutor de Python.
    """
    
    def __init__(self, max_workers: int = 5) -> None:
        self._executor = _ThreadPoolExecutor(max_workers=max_workers)
    
    def submit(self, fn: Callable, *args: Any, **kwargs: Any) -> Any:
        """Envía una función para ser ejecutada de forma asíncrona."""
        return self._executor.submit(fn, *args, **kwargs)
    
    def shutdown(self, wait: bool = True, cancel_futures: bool = False) -> None:
        """Apaga el executor."""
        self._executor.shutdown(wait=wait, cancel_futures=cancel_futures)
