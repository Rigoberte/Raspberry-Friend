from __future__ import annotations

import threading
from dataclasses import dataclass
from queue import Queue, Empty
from typing import Callable, DefaultDict, Type, TypeVar
from collections import defaultdict
import traceback

from src.domain.ports.outbound.event_bus_ports import EventBusPort

T = TypeVar("T")

Handler = Callable[[object], None]

class NoOpEventBus(EventBusPort):
    def publish(self, event: object) -> None:
        return

    def subscribe(self, event_type: Type[T], handler: Callable[[T], None]) -> None:
        return

    def stop(self) -> None:
        return


class InMemoryEventBus(EventBusPort):
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
                # Bloqueo indefinido sin polling: solo se despierta cuando hay evento
                event = self._q.get(timeout=None)
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
        # Enviar evento centinela para despertar el thread
        self._q.put(None)
        self._thread.join()
