import heapq
import threading
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional

from src.domain.ports.outbound.event_bus_ports import EventBusPort
from src.domain.ports.outbound.task_executor_ports import TaskExecutorPort
from src.domain.events.task_events import TaskQueued
from src.application.services.command_dispatcher import CommandDispatcher
from src.domain.models.task import Task

@dataclass(order=True, frozen=True)
class __HeapItem__:
    run_at: datetime
    neg_priority: int
    seq: int
    task_id: str
    version: int


class TaskScheduler:
    def __init__(
        self,
        dispatcher: CommandDispatcher,
        event_bus: EventBusPort,
        executor: TaskExecutorPort,
    ) -> None:
        self._dispatcher = dispatcher
        self._event_bus = event_bus
        self._executor = executor

        self._condition = threading.Condition()
        self._is_running = False
        self._thread: Optional[threading.Thread] = None

        self._tasks_by_id: dict[str, Task] = {}
        self._cancelled_task_ids: set[str] = set()

        self._heap: list[__HeapItem__] = []
        self._task_version: dict[str, int] = {}
        self._seq = 0

        self.start()

    def start(self) -> None:
        with self._condition:
            if self._is_running:
                return

            self._is_running = True
            self._thread = threading.Thread(target=self.__run_loop__, daemon=False)
            self._thread.start()

    def stop(self) -> None:
        with self._condition:
            self._is_running = False
            self._condition.notify_all()

        if self._thread:
            self._thread.join()
            self._thread = None

        self._executor.shutdown(wait=True, cancel_futures=False)

    def has_tasks(self) -> bool:
        with self._condition:
            return bool(self._tasks_by_id)

    def list_tasks(self) -> list[Task]:
        with self._condition:
            return list(self._tasks_by_id.values())

    def add_task(self, task: Task) -> None:
        task_id = task.get_id()

        with self._condition:
            self._tasks_by_id[task_id] = task
            self._cancelled_task_ids.discard(task_id)

            self._task_version[task_id] = self._task_version.get(task_id, 0)

            self.__schedule_task__(task, now=self.__datetime_now__())
            self._condition.notify()

        self._event_bus.publish( 
            TaskQueued(
                task_id=task.get_id(),
                command_name=task.get_command().get_name(),
                occurred_at=self.__datetime_now__(),
            )
        )

    def remove_task(self, task: Task) -> None:
        task_id = task.get_id()
        with self._condition:
            self._cancelled_task_ids.add(task_id)
            self._tasks_by_id.pop(task_id, None)
            self._condition.notify()

    def __run_loop__(self) -> None:
        while True:
            with self._condition:
                if not self._is_running:
                    return

                self.__discard_invalid_heap_tops__()

                if not self._heap:
                    self._condition.wait()
                    continue

                now = self.__datetime_now__()
                next_item = self._heap[0]

                if next_item.run_at > now:
                    timeout = (next_item.run_at - now).total_seconds()
                    self._condition.wait(timeout=max(0.0, timeout))
                    continue

                heapq.heappop(self._heap)

                task = self._tasks_by_id.get(next_item.task_id)
                if task is None:
                    continue
                if task.is_done():
                    self.__drop_task__(next_item.task_id)
                    continue

                if not task.should_execute(now):
                    self.__bump_version__(next_item.task_id)
                    self.__schedule_task__(task, now=now)
                    continue

                if task.try_claim():
                    self._executor.submit(self.__execute_task__, task)

    def __schedule_task__(self, task: Task, now: datetime) -> None:
        task_id = task.get_id()

        if task_id in self._cancelled_task_ids or task.is_done():
            return

        if task.should_execute(now):
            run_at = now
        else:
            run_at = task.next_run_at(now)
            if run_at is None:
                return

        priority = self.__task_priority__(task)
        version = self._task_version.get(task_id, 0)

        self._seq += 1
        heapq.heappush(
            self._heap,
            __HeapItem__(
                run_at=run_at,
                neg_priority=-priority,
                seq=self._seq,
                task_id=task_id,
                version=version,
            ),
        )

    def __discard_invalid_heap_tops__(self) -> None:
        while self._heap:
            top = self._heap[0]
            current_version = self._task_version.get(top.task_id)

            if current_version is None or top.task_id in self._cancelled_task_ids:
                heapq.heappop(self._heap)
                continue

            if top.version != current_version:
                heapq.heappop(self._heap)
                continue

            task = self._tasks_by_id.get(top.task_id)
            if task is None:
                heapq.heappop(self._heap)
                continue

            if task.is_done():
                heapq.heappop(self._heap)
                self.__drop_task__(top.task_id)
                continue

            return

    def __bump_version__(self, task_id: str) -> None:
        self._task_version[task_id] = self._task_version.get(task_id, 0) + 1

    def __drop_task__(self, task_id: str) -> None:
        self._tasks_by_id.pop(task_id, None)
        self._task_version.pop(task_id, None)
        self._cancelled_task_ids.discard(task_id)

    def __task_priority__(self, task: Task) -> int:
        return int(getattr(task, "priority", getattr(task, "_priority", 0)))

    def __execute_task__(self, task: Task) -> None:
        try:
            task.execute(self._dispatcher)
        except Exception as e:
            pass
        finally:
            domain_events = task.collect_domain_events()
            
            for event in domain_events:
                self._event_bus.publish(event)
            
            with self._condition:
                task_id = task.get_id()

                if task_id in self._cancelled_task_ids:
                    self.__drop_task__(task_id)
                elif task.is_done():
                    self.__drop_task__(task_id)
                else:
                    self.__bump_version__(task_id)
                    self.__schedule_task__(task, now=self.__datetime_now__())

                self._condition.notify()

    @staticmethod
    def __datetime_now__() -> datetime:
        return datetime.now(timezone(timedelta(hours=-3)))