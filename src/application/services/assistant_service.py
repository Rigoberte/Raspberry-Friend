from src.application.services.skill_registry import SkillRegistry
from src.domain.models.command import Command
from src.domain.models.command import CommandResult

class AssistantService:
    """Servicio principal que coordina skills a través del registry."""
    
    def __init__(self, registry: SkillRegistry) -> None:
        self._registry = registry
    
    def handle_command(self, command: Command) -> CommandResult:
        """Busca el skill adecuado y ejecuta el comando."""
        handler = self._registry.get(command)
        
        if not handler:
            return CommandResult(
                success=False, 
                message=f"Skill '{command.get_name()}' no encontrado"
            )
        
        return handler.handle(command)
    
    def list_skills(self) -> list[str]:
        """Retorna lista de skills disponibles."""
        return self._registry.list()