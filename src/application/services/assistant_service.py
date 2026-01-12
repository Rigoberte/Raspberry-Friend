from src.application.services.skill_registry import SkillRegistry
from src.application.services.task_scheduler import TaskScheduler
from src.domain.models.command import Command
from src.domain.models.task import Task

from src.application.services.scheduling_policy_parser import SchedulingPolicyParser
from src.application.services.command_to_task import CommandToTask

class AssistantService:
    def __init__(self, registry: SkillRegistry, scheduler: TaskScheduler) -> None:
        self._registry = registry
        self._scheduler = scheduler
        self._policy_parser = SchedulingPolicyParser()
        self._command_to_task = CommandToTask(self._policy_parser)
    
    def handle_command(self, command: Command) -> None:
        task = self._command_to_task.build(command)
        self._scheduler.add_task(task)
        return 
    
    def get_active_tasks(self) -> list[Task]:
        return self._scheduler.list_tasks()
    
    def list_skills(self) -> list[str]:
        return self._registry.list_skills()
    
    def stop(self) -> None:
        self._scheduler.stop()