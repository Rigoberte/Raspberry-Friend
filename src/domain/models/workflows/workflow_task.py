from typing import Any
from datetime import datetime

from src.domain.models.task import Task
from src.domain.models.task_status import TaskStatus
from src.domain.models.command import CommandResult
from src.domain.models.workflows.workflow_step import WorkflowStep
from src.domain.models.command import Command

from src.domain.events.task_events import TaskStarted, TaskCompleted, TaskFailed
from datetime import datetime, timezone

class WorkflowTask(Task): # Composite
    def __init__(
            self, 
            steps: list[WorkflowStep], 
            initial_context: dict[str, Any] | None = None, 
            priority: int = 0
        ):
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
        with self._state_lock:
            if self._status != TaskStatus.EXECUTING:
                return
        
        self._emit_event(
            TaskStarted(
                task_id=self._id,
                command_name="workflow",
                occurred_at=datetime.now(timezone.utc)
            )
        )
        
        try:
            for step in self._steps:
                cmd = step.command(self._ctx)
                res = dispatcher.handle(cmd)

                if not res.is_successful():
                    self._result = res
                    self._status = TaskStatus.FAILED
                    self._done_event.set()
                    
                    self._emit_event(
                        TaskFailed(
                            task_id=self._id,
                            command_name="workflow",
                            occurred_at=datetime.now(timezone.utc),
                            error_message=res.get_message(),
                            details={"context": self._ctx}
                        )
                    )
                    return

                step.on_success(self._ctx, res)

            self._result = CommandResult(True, "Workflow completed", data=self._ctx)
            self.on_execution_complete()
            
            self._emit_event(
                TaskCompleted(
                    task_id=self._id,
                    command_name="workflow",
                    occurred_at=datetime.now(timezone.utc),
                    success=True,
                    message="Workflow completed",
                    output=self._ctx
                )
            )

        except Exception as e:
            self._result = CommandResult(False, f"Workflow error: {e}")
            self._status = TaskStatus.FAILED
            self._done_event.set()
            
            self._emit_event(
                TaskFailed(
                    task_id=self._id,
                    command_name="workflow",
                    occurred_at=datetime.now(timezone.utc),
                    error_message=f"Workflow error: {e}",
                    details={}
                )
            )

    def get_type_of_task(self) -> str:
        return "Workflow"