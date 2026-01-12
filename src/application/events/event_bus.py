from __future__ import annotations

import threading
from dataclasses import dataclass
from queue import Queue, Empty
from typing import Callable, DefaultDict, Type, TypeVar
from collections import defaultdict
import traceback

T = TypeVar("T")

Handler = Callable[[object], None]

class EventBus:
    def publish(self, event: object) -> None:
        raise NotImplementedError

    def subscribe(self, event_type: Type[T], handler: Callable[[T], None]) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError
    
class NoOpEventBus(EventBus):
    def publish(self, event: object) -> None:
        return

    def subscribe(self, event_type: Type[T], handler: Callable[[T], None]) -> None:
        return

    def stop(self) -> None:
        return


class InMemoryEventBus(EventBus):
    def __init__(self) -> None:
        self._handlers: DefaultDict[type, list[Handler]] = defaultdict(list)
        self._lock = threading.Lock()

        self._q: Queue[object] = Queue()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=False)
        self._thread.start()

    def subscribe(self, event_type: Type[T], handler: Callable[[T], None]) -> None:
        with self._lock:
            self._handlers[event_type].append(handler)

    def publish(self, event: object) -> None:
        self._q.put(event)

    def _loop(self) -> None:
        while self._running:
            try:
                event = self._q.get(timeout=0.2)
            except Empty:
                continue

            with self._lock:
                handlers = list(self._handlers.get(type(event), []))

            for h in handlers:
                try:
                    h(event)
                except Exception as e:
                    traceback.print_exc()

            self._q.task_done()

    def stop(self) -> None:
        self._running = False
        self._thread.join()
