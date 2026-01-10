from datetime import datetime, timedelta, timezone
from typing import Callable

from src.application.services.skill_registry import SkillRegistry
from src.application.services.task_scheduler import TaskScheduler
from src.domain.models.command import Command
from src.domain.models.command import CommandResult
from src.domain.models.task import Task
from src.domain.models.immediate_task import ImmediateTask
from src.domain.models.scheduled_task import ScheduledTask
from src.domain.models.recurring_task import RecurringTask
from src.domain.models.continuous_task import ContinuousTask

class AssistantService:
    def __init__(self, registry: SkillRegistry, scheduler: TaskScheduler) -> None:
        self._registry = registry
        self._scheduler = scheduler
    
    def handle_command(self, command: Command) -> CommandResult:
        """
        match command.type:
            case "immediate":
                task = ImmediateTask(command)
            case "scheduled":
                task = ScheduledTask(command)
            case "recurring":
                task = RecurringTask(command)
            case "continuous":
                task = ContinuousTask(command)
        """
        #task = ImmediateTask(command)
        task = ScheduledTask(command, datetime.now(timezone.utc) + timedelta(seconds=1))

        self._scheduler.add_task(task)

        return task.get_result() or CommandResult(False, "Task finished without result")

    def create_immediate_command(self, command: Command) -> Task:
        task = ImmediateTask(command)
        self._scheduler.add_task(task)
        return task

    def create_schedule_command(self, command: Command, scheduled_time: datetime) -> Task:
        task = ScheduledTask(command, scheduled_time)
        self._scheduler.add_task(task)
        return task

    def create_schedule_recurring(self, command: Command, interval: timedelta, max_executions: int | None = None) -> Task:
        task = RecurringTask(command, interval, max_executions)
        self._scheduler.add_task(task)
        return task

    def create_schedule_continuous(self, command: Command, check_interval: timedelta, condition: Callable[[], bool], max_executions: int | None = None) -> Task:
        task = ContinuousTask(command, check_interval, condition, max_executions)
        self._scheduler.add_task(task)
        return task
    
    def get_active_tasks(self) -> list[Task]:
        return self._scheduler.list_tasks()
    
    def list_skills(self) -> list[str]:
        return self._registry.list_skills()
    
    def stop(self) -> None:
        self._scheduler.stop()