from typing import Optional
import numpy as np

from src.adapters.inbound.gui.gui_window import GUIWindow, MessageType
from src.adapters.inbound.gui.presenters.console_presenter import ConsolePresenter
from src.adapters.inbound.voice_command.voice_command_adapter import VoiceCommandAdapter
from src.domain.ports.outbound.microphone_ports import MicrophonePort

from src.application.use_cases.execute_command_use_case import ExecuteCommandUseCase
from src.application.services.assistant_service import AssistantService
from src.domain.ports.outbound.event_bus_ports import EventBusPort
from src.domain.ports.outbound.logger_ports import LoggerPort

from src.application.events.event_bus import NoOpEventBus

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
        event_bus: EventBusPort = NoOpEventBus(),
        title: str = "Raspberry Friend",
        width: int = 900,
        height: int = 700
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
        self.assistant_service: AssistantService = assistant_service
        self.event_bus: EventBusPort = event_bus
        self.voice_command_adapter: VoiceCommandAdapter = None  # Se conectará después # TODO: SACAR SETTER con Null Pattern Object
        self._mic_adapter: MicrophonePort = None  # Para grabación interactiva # TODO: SACAR SETTER con Null Pattern Object
        self._last_recording_path = None  # Path del último archivo grabado
        
        self.window = GUIWindow(
            title=title,
            width=width,
            height=height,
            on_command=None  # Se conectará después
        )
        
        # Crear logger adaptado a la GUI
        self.logger = GUILoggerAdapter(self.window)
        
        # Crear presenter con casos de uso
        self._setup_presenter()
        
        # Conectar vista al presenter
        self.window.on_command = self.presenter.handle_user_input
    
    def _setup_presenter(self) -> None:
        """Configura el presenter con sus dependencias."""
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

    def set_voice_command_adapter(self, voice_command_adapter: VoiceCommandAdapter, mic_adapter: MicrophonePort) -> None:
        """
        Conecta el adaptador de comandos por voz al GUI.
        
        Args:
            voice_command_adapter: VoiceCommandAdapter para escuchar comandos
            mic_adapter: MicrophonePort para grabación interactiva
        """
        self.voice_command_adapter = voice_command_adapter
        # Guardar referencia al micrófono para grabación interactiva
        self._mic_adapter = mic_adapter
        # Conectar callbacks para grabación interactiva (press/release)
        self.window.on_start_recording = self.start_recording
        self.window.on_stop_recording = self.stop_recording
        self.window.on_listen_recording_done = self._handle_voice_recording_done

    def start_recording(self) -> None:
        """
        Inicia grabación de audio interactivamente.
        Se llama cuando se presiona el botón.
        """
        if not self._mic_adapter:
            return
        
        result = self._mic_adapter.start_recording()
        if not result.get("success"):
            self.display_message(f"⚠️ Error iniciando grabación: {result.get('message', '')}", MessageType.WARNING)

    def stop_recording(self) -> dict:
        """
        Detiene grabación de audio interactivamente.
        Se llama cuando se suelta el botón.
        
        Returns:
            Dict con información de la grabación
        """
        if not self._mic_adapter:
            return {"success": False}
        
        result = self._mic_adapter.stop_recording()
        if result.get("success"):
            self._last_recording_path = result.get("path")
        return result

    def _handle_voice_recording_done(self) -> None:
        """
        Maneja el fin de grabación interactiva (cuando se suelta el botón).
        Procesa el archivo grabado con transcripción e interpretación.
        """
        if not self.voice_command_adapter or not self._last_recording_path:
            self.display_message("❌ Error: No hay archivo grabado", MessageType.ERROR)
            return
        
        try:
            result = self.voice_command_adapter.interpret_voice_command(self._last_recording_path)

            if result["success"]:
                transcript = result.get("transcript")
                if transcript:
                    self.display_message(f"📝 Transcripción: {transcript}", MessageType.INFO)
                self.display_message(result["message"], MessageType.SUCCESS)
            else:
                self.display_message(result["message"], MessageType.ERROR)
                
        except Exception as e:
            self.display_message(f"❌ Error procesando grabación: {str(e)}", MessageType.ERROR)

    def run(self) -> None:
        """Inicia la GUI."""
        self.window.run()

    def close(self) -> None:
        """Cierra la GUI."""
        self.window.close()
