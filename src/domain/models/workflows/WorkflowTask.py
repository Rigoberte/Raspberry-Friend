from typing import Any
from datetime import datetime

from src.domain.models.task import Task
from src.domain.models.task_status import TaskStatus
from src.domain.models.command import CommandResult
from src.domain.models.workflows.WorkFlowStep import WorkflowStep
from src.domain.models.command import Command

class WorkflowTask(Task): # Composite
    def __init__(self, steps: list[WorkflowStep], initial_context: dict[str, Any] | None = None, priority: int = 0):
        super().__init__(Command("workflow", {}), priority)

        self._steps = steps
        self._ctx: dict[str, Any] = dict(initial_context or {})

    def should_execute(self, now: datetime) -> bool:
        return self.is_pending()

    def next_run_at(self, now: datetime):
        return now if self.is_pending() else None

    def on_execution_complete(self) -> None:
        self._status = TaskStatus.COMPLETED
        self._done_event.set()

    def execute(self, dispatcher) -> None:
        try:
            for step in self._steps:
                cmd = step.command(self._ctx)
                res = dispatcher.handle(cmd)

                if not res.is_successful():
                    self._result = res
                    self._status = TaskStatus.FAILED
                    self._done_event.set()
                    return

                step.on_success(self._ctx, res)

            self._result = CommandResult(True, "Workflow completed", data=self._ctx)
            self.on_execution_complete()

        except Exception as e:
            self._result = CommandResult(False, f"Workflow error: {e}")
            self._status = TaskStatus.FAILED
            self._done_event.set()

    def get_type_of_task(self) -> str:
        return "Workflow"