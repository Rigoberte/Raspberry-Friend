"""
Caso de uso para ejecutar comandos del usuario.
Orquesta el parsing, validación y ejecución de comandos.
"""
from src.domain.models.command import Command
from src.domain.ports.outbound.logger_ports import LoggerPort
from src.application.services.assistant_service import AssistantService


class ExecuteCommandUseCase:
    """
    Caso de uso que maneja la ejecución de comandos del usuario.
    Desacopla la interfaz (GUI/CLI) de los servicios de aplicación.
    """
    
    def __init__(
        self,
        assistant_service: AssistantService,
        logger: LoggerPort
    ):
        """
        Inicializa el caso de uso.
        
        Args:
            assistant_service: Servicio de asistente
            logger: Logger para registrar operaciones
        """
        self._assistant = assistant_service
        self._logger = logger
    
    def execute(self, command_name: str, args: dict[str, str] | None = None) -> None:
        """
        Ejecuta un comando con los argumentos dados.
        
        Args:
            command_name: Nombre del comando a ejecutar
            args: Argumentos del comando (opcional)
            
        Raises:
            ValueError: Si el comando es inválido
        """
        if not command_name or not command_name.strip():
            raise ValueError("El nombre del comando no puede estar vacío")
        
        command_name = command_name.strip()
        args = args or {}
        
        self._logger.debug(f"Ejecutando comando: {command_name} con args: {args}")
        
        try:
            command = Command(command_name, args)
            self._assistant.handle_command(command)
            self._logger.debug(f"Comando '{command_name}' procesado exitosamente")
            
        except Exception as e:
            self._logger.error(f"Error al ejecutar comando '{command_name}': {str(e)}")
            raise
