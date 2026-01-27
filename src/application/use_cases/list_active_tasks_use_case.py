"""
Caso de uso para listar tareas activas.
"""
from src.domain.models.task import Task
from src.application.services.assistant_service import AssistantService


class ListActiveTasksUseCase:
    """
    Caso de uso que lista todas las tareas activas en el sistema.
    """
    
    def __init__(self, assistant_service: AssistantService):
        """
        Inicializa el caso de uso.
        
        Args:
            assistant_service: Servicio de asistente
        """
        self._assistant = assistant_service
    
    def execute(self) -> list[Task]:
        """
        Obtiene la lista de tareas activas.
        
        Returns:
            Lista de tareas activas
        """
        return self._assistant.get_active_tasks()
