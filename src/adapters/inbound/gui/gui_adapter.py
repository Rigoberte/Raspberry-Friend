from typing import Optional
import numpy as np

from src.adapters.inbound.gui.gui_window import GUIWindow, MessageType
from src.adapters.inbound.gui.presenters.console_presenter import ConsolePresenter
from src.application.use_cases.execute_command_use_case import ExecuteCommandUseCase
from src.application.services.assistant_service import AssistantService
from src.domain.ports.outbound.event_bus_ports import EventBusPort
from src.domain.ports.outbound.logger_ports import LoggerPort


class GUILoggerAdapter(LoggerPort):
    """Adaptador que implementa LoggerPort y envía logs a la GUI."""

    def __init__(self, gui_window: GUIWindow):
        """
        Inicializa el adaptador de logger para la GUI.

        Args:
            gui_window: Ventana GUI donde mostrar los logs
        """
        self.gui_window = gui_window

    def debug(self, message: str, **kwargs) -> None:
        """
        Registra un mensaje de debug en la GUI.

        Args:
            message: Mensaje a registrar
            **kwargs: Argumentos adicionales (ignorados)
        """
        self.gui_window.add_output(message, MessageType.INFO)

    def info(self, message: str, **kwargs) -> None:
        """
        Registra un mensaje de info en la GUI.

        Args:
            message: Mensaje a registrar
            **kwargs: Argumentos adicionales (ignorados)
        """
        self.gui_window.add_output(message, MessageType.SUCCESS)

    def warning(self, message: str, **kwargs) -> None:
        """
        Registra un mensaje de advertencia en la GUI.

        Args:
            message: Mensaje a registrar
            **kwargs: Argumentos adicionales (ignorados)
        """
        self.gui_window.add_output(message, MessageType.WARNING)

    def error(self, message: str, **kwargs) -> None:
        """
        Registra un mensaje de error en la GUI.

        Args:
            message: Mensaje a registrar
            **kwargs: Argumentos adicionales (ignorados)
        """
        self.gui_window.add_output(message, MessageType.ERROR)



class GUIAdapter:
    """
    Adaptador que conecta la interfaz gráfica con los servicios de la aplicación.
    Usa el patrón Presenter para separar lógica de vista.
    """

    def __init__(
        self,
        assistant_service: AssistantService,
        event_bus: Optional[EventBusPort] = None,
        title: str = "Raspberry Friend",
        width: int = 900,
        height: int = 700,
    ):
        """
        Inicializa el adaptador GUI con arquitectura MVP.

        Args:
            assistant_service: Servicio de asistente para procesar comandos
            event_bus: Bus de eventos para suscribirse a logs
            title: Título de la ventana
            width: Ancho de la ventana
            height: Alto de la ventana
        """
        self.assistant_service = assistant_service
        self.event_bus = event_bus
        
        # Crear ventana GUI
        self.window = GUIWindow(
            title=title,
            width=width,
            height=height,
            on_command=None,  # Se conectará después
        )
        
        # Crear logger adaptado a la GUI
        self.logger = GUILoggerAdapter(self.window)
        
        # Crear presenter con casos de uso
        self._setup_presenter()
        
        # Conectar vista al presenter
        self.window.on_command = self.presenter.handle_user_input
    
    def _setup_presenter(self) -> None:
        """Configura el presenter con sus dependencias."""
        if not self.event_bus:
            from src.application.events.event_bus import NoOpEventBus
            self.event_bus = NoOpEventBus()
        
        # Crear caso de uso
        execute_command_uc = ExecuteCommandUseCase(
            self.assistant_service,
            self.logger
        )
        
        # Crear presenter
        self.presenter = ConsolePresenter(
            execute_command_uc,
            self.event_bus,
            self.logger
        )
        
        # Conectar vista al presenter
        self.presenter.attach_view(self.window)

    def display_message(self, message: str, message_type: str = MessageType.INFO) -> None:
        """
        Muestra un mensaje en la consola.

        Args:
            message: Mensaje a mostrar
            message_type: Tipo de mensaje para colorear
        """
        self.window.add_output(message, message_type)

    def display_camera_frame(self, frame: np.ndarray) -> None:
        """
        Muestra un frame de cámara en la ventana principal.
        Asegura actualización en el hilo de Tkinter.

        Args:
            frame: Array numpy con el frame (BGR de OpenCV o RGB)
        """
        try:
            # Clonar frame para evitar mutaciones entre hilos
            frame_copy = frame.copy()
        except Exception:
            frame_copy = frame
        # Ejecutar en el hilo principal de Tkinter
        self.window.root.after(0, lambda f=frame_copy: self.window.display_camera_frame(f))

    def clear_camera_display(self) -> None:
        """Limpia la pantalla de cámara."""
        self.window.clear_camera_display()

    def run(self) -> None:
        """Inicia la GUI."""
        self.window.run()

    def close(self) -> None:
        """Cierra la GUI."""
        self.window.close()
