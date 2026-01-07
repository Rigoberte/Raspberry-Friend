from src.application.services.skill_registry import SkillRegistry
from src.domain.models.task import Task

import threading
import time

class TaskScheduler:
    def __init__(self) -> None:
        self._tasks_queue = []  # Queue of pending tasks
        self._lock = threading.Lock()  # Lock for thread-safe access to queue
        self._running = False  # Flag to control the background thread
        self._thread = None  # Background thread reference

        self.__start__()

    def has_tasks(self) -> bool:
        with self._lock:
            return len(self._tasks_queue) > 0
    
    def add_task(self, task: Task) -> None:
        with self._lock:
            self._tasks_queue.append(task)

    def remove_task(self, task: Task) -> None:
        with self._lock:
            if task in self._tasks_queue:
                self._tasks_queue.remove(task)
    
    def __start__(self) -> None:
        if self._running:
            return  # Already running
        
        self._running = True
        self._thread = threading.Thread(target=self.__run_loop__, daemon=True)
        self._thread.start()

    """
    def __stop__(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)  # Wait max 5 seconds
            self._thread = None
    """

    def __run_loop__(self) -> None:
        while self._running:
            if self.has_tasks():
                self.__run_one_round__()
            else:
                time.sleep(0.01)  # Small sleep to avoid busy-waiting

    def __run_one_round__(self) -> None:
        with self._lock:
            tasks_to_process = [t for t in self._tasks_queue if t.is_pending()]
        
        for task in tasks_to_process:
            self.__run_task__(task)
            self.remove_task(task)

    def __run_task__(self, task: Task) -> None:
        if not task.is_pending():
            return

        task.start()