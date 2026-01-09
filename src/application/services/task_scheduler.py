import threading
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

from src.application.events.event_bus import EventBus
from src.application.events.task_events import TaskQueued, TaskStarted, TaskCompleted, TaskFailed

from src.domain.models.task import Task
from src.application.services.command_dispatcher import CommandDispatcher

class TaskScheduler:
    def __init__(self, dispatcher: CommandDispatcher, event_bus: EventBus, max_workers: int) -> None:
        self._dispatcher = dispatcher
        self._event_bus = event_bus
        self._tasks: list[Task] = [] 

        self._lock = threading.Lock()  # Lock for thread-safe access
        self._cv = threading.Condition(self._lock) 
        
        self._running = False  # Flag to control the background thread
        self._thread = None  # Background thread reference
        self._executor = ThreadPoolExecutor(max_workers=max_workers)  # For concurrent task execution

        self.__start__()

    def has_tasks(self) -> bool:
        with self._lock:
            return len(self._tasks) > 0
    
    def add_task(self, task: Task) -> None:
        with self._cv:
            self._tasks.append(task)
            self._cv.notify()

        self._event_bus.publish(
            TaskQueued(
                task_id=task.get_id(), 
                command_name=task.get_command().get_name(), 
                occurred_at=datetime.now(timezone.utc)
            )
        )

    def remove_task(self, task: Task) -> None:
        with self._cv:
            if task in self._tasks:
                self._tasks.remove(task)
            self._cv.notify()
    
    def get_all_tasks(self) -> list[Task]:
        with self._lock:
            return list(self._tasks)
    
    def stop(self) -> None:
        with self._cv:
            self._running = False
            self._cv.notify()

        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None

    def __start__(self) -> None:
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self.__run_loop__, daemon=True)
        self._thread.start()

    def __run_loop__(self) -> None:
        while True:
            with self._cv:
                if not self._running:
                    return

                self._tasks = [t for t in self._tasks if not t.is_done()]

                now = datetime.now(timezone.utc)
                due: list[Task] = []
                next_wakeup: datetime | None = None

                for t in self._tasks:
                    if t.should_execute(now):
                        due.append(t)
                    else:
                        nra = t.next_run_at(now)
                        if nra is not None:
                            next_wakeup = nra if next_wakeup is None else min(next_wakeup, nra)

                due.sort(key=lambda x: x._priority, reverse=True)

                for t in due:
                    if t.try_claim():
                        self._event_bus.publish(
                            TaskStarted(
                                task_id=t.get_id(),
                                command_name=t.get_command().get_name(),
                                occurred_at=datetime.now(timezone.utc)
                            )
                        )
                        self._executor.submit(self.__execute_task__, t)

                if not self._tasks:
                    self._cv.wait()
                else:
                    if next_wakeup is None:
                        self._cv.wait()
                    else:
                        timeout = max(0.0, (next_wakeup - now).total_seconds())
                        self._cv.wait(timeout=timeout)

    def __execute_task__(self, task: Task) -> None:
        task.execute(self._dispatcher)
        
        result = task.get_result()
        if result and result.is_successful():
            self._event_bus.publish(TaskCompleted(
                task_id=task.get_id(),
                command_name=task.get_command().get_name(),
                occurred_at=datetime.now(timezone.utc),
                result=result,
            ))
        else:
            self._event_bus.publish(TaskFailed(
                task_id=task.get_id(),
                command_name=task.get_command().get_name(),
                occurred_at=datetime.now(timezone.utc),
                result=result,
            ))

        with self._cv: # Wake Scheduler
            self._cv.notify()