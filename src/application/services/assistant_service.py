from src.application.services.skill_registry import SkillRegistry
from src.application.services.task_scheduler import TaskScheduler
from src.domain.models.command import Command
from src.domain.models.command import CommandResult
from src.domain.models.task import Task

class AssistantService:
    def __init__(self, registry: SkillRegistry, scheduler: TaskScheduler) -> None:
        self._registry = registry
        self._scheduler = scheduler
    
    def handle_command(self, command: Command) -> CommandResult:
        handler = self._registry.get_skill(command)
        
        task = Task(command, handler)
        
        self._scheduler.add_task(task)
        
        task.wait()
        
        return task.get_result()
    
    def list_skills(self) -> list[str]:
        return self._registry.list_skills()