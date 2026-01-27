"""
Presenter para la consola de comandos.
Maneja la lógica de presentación y eventos de la consola.
"""
from typing import Protocol
from src.domain.ports.outbound.event_bus_ports import EventBusPort
from src.domain.ports.outbound.logger_ports import LoggerPort
from src.domain.events.task_events import TaskCompleted, TaskFailed, TaskQueued, TaskStarted
from src.domain.events.music_events import PlaybackProgress, PlaybackStarted, PlaybackStopped
from src.application.services.task_event_logger import TaskEventLogger
from src.application.services.music_event_logger import MusicEventLogger, LoggerLevel
from src.application.use_cases.execute_command_use_case import ExecuteCommandUseCase
from src.application.services.command_parser import CommandParser


class ConsoleView(Protocol):
    """
    Protocolo que define la interfaz de la vista de consola.
    Cualquier implementación de consola debe cumplir este contrato.
    """
    def add_output(self, message: str, message_type: str) -> None:
        """Agrega un mensaje a la salida de la consola."""
        ...
    
    def clear_output(self) -> None:
        """Limpia la salida de la consola."""
        ...


class ConsolePresenter:
    """
    Presenter que maneja la lógica de la consola.
    Desacopla la vista (GUI) de los casos de uso y servicios.
    """
    
    def __init__(
        self,
        execute_command_uc: ExecuteCommandUseCase,
        event_bus: EventBusPort,
        logger: LoggerPort
    ):
        """
        Inicializa el presenter.
        
        Args:
            execute_command_uc: Caso de uso para ejecutar comandos
            event_bus: Bus de eventos para suscribirse
            logger: Logger para la vista
        """
        self._execute_command_uc = execute_command_uc
        self._event_bus = event_bus
        self._logger = logger
        self._parser = CommandParser()
        self._view: ConsoleView | None = None
        
        self._setup_event_subscriptions()
        logger.info("Inicializando Raspberry Friend...")
    
    def attach_view(self, view: ConsoleView) -> None:
        """
        Conecta una vista al presenter.
        
        Args:
            view: Vista que implementa ConsoleView
        """
        self._view = view
    
    def _setup_event_subscriptions(self) -> None:
        """Configura las suscripciones a eventos del sistema."""
        # Logger de tareas
        task_logger = TaskEventLogger(self._logger)
        self._event_bus.subscribe(TaskQueued, task_logger.on_task_queued)
        self._event_bus.subscribe(TaskStarted, task_logger.on_task_started)
        self._event_bus.subscribe(TaskCompleted, task_logger.on_task_completed)
        self._event_bus.subscribe(TaskFailed, task_logger.on_task_failed)
        
        # Logger de música
        music_logger = MusicEventLogger(self._logger, level=LoggerLevel.INFO)
        self._event_bus.subscribe(PlaybackStarted, music_logger.on_playback_started)
        self._event_bus.subscribe(PlaybackStopped, music_logger.on_playback_stopped)
        self._event_bus.subscribe(PlaybackProgress, music_logger.on_progress)
    
    def handle_user_input(self, user_input: str) -> None:
        """
        Procesa la entrada del usuario.
        
        Args:
            user_input: Texto ingresado por el usuario
        """
        if not user_input or not user_input.strip():
            return
        
        try:
            # Parsear comando
            command_name, args = self._parser.parse_with_args(user_input)
            
            # Ejecutar comando
            self._execute_command_uc.execute(command_name, args)
            
        except ValueError as e:
            self._logger.error(f"Error de validación: {str(e)}")
        except Exception as e:
            self._logger.error(f"Error inesperado: {str(e)}")
    
    def clear_console(self) -> None:
        """Limpia la consola."""
        if self._view:
            self._view.clear_output()
