import numpy as np

from src.adapters.inbound.gui.gui_window import GUIWindow
from src.adapters.inbound.gui.presenters.console_presenter import ConsolePresenter
from src.adapters.inbound.voice_command.voice_command_adapter import VoiceCommandAdapter
from src.domain.ports.outbound.microphone_ports import MicrophonePort
from src.domain.ports.outbound.camera_ports import CameraPort

from src.application.use_cases.execute_command_use_case import ExecuteCommandUseCase
from src.application.services.assistant_service import AssistantService
from src.domain.ports.outbound.event_bus_ports import EventBusPort
from src.domain.ports.outbound.logger_ports import LoggerPort
from src.adapters.outbound.logger.gui_logger_adapter import GUILoggerAdapter
from src.application.services.task_event_logger import LoggerLevel

class GUIAdapter:
    def __init__(
                self,
                assistant_service: AssistantService,
                event_bus: EventBusPort,
                title: str,
                width: int,
                height: int
            ) -> None:
        
        self.assistant_service: AssistantService = assistant_service
        self.event_bus: EventBusPort = event_bus
        self.voice_command_adapter: VoiceCommandAdapter = None  # Se conectará después # TODO: SACAR SETTER con Null Pattern Object
        self._mic_adapter: MicrophonePort = None  # Para grabación interactiva # TODO: SACAR SETTER con Null Pattern Object
        self._last_recording_path: str = None  # Path del último archivo grabado
        self.camera_adapter: CameraPort = None  # Se conectará después
        
        self.window: GUIWindow = GUIWindow(
            title=title,
            width=width,
            height=height,
            on_command=None  # Se conectará después
        )
        
        self.logger: LoggerPort = GUILoggerAdapter(gui_window=self.window, level=LoggerLevel.INFO)
        
        execute_command_uc = ExecuteCommandUseCase(
            self.assistant_service,
            self.logger
        )
        
        self.presenter = ConsolePresenter(
            execute_command_uc,
            self.event_bus,
            self.logger
        )
        
        self.presenter.attach_view(self.window)
        
        self.window.on_command = self.presenter.handle_user_input

        self.logger.info("Bienvenido a Raspberry Friend")
        self.logger.info("Escribe un comando para comenzar (ej: 'echo Hola')")
    
    def set_camera_adapter(self, camera_adapter: CameraPort) -> None:
        """
        Conectar el camera adapter y establecer callbacks.
        Esto mantiene la arquitectura desacoplada.
        """
        self.camera_adapter = camera_adapter
        
        # Conectar callbacks de frames y modo
        self.camera_adapter.set_frame_callback(self.display_camera_frame)
        self.camera_adapter.set_mode_change_callback(self._on_camera_mode_changed)
        
        # Conectar callback del joystick a los controles del pan/tilt
        self.window.set_pan_tilt_control_callback(self._on_joystick_control)
    
    def display_camera_frame(self, frame: np.ndarray) -> None:
        try:
            frame_copy = frame.copy()
        except Exception:
            frame_copy = frame
        self.window.root.after(0, lambda f=frame_copy: self.window.display_camera_frame(f))

    def clear_camera_display(self) -> None:
        self.window.clear_camera_display()
    
    def _on_camera_mode_changed(self, mode: str) -> None:
        """
        Callback llamado cuando el camera adapter cambia de modo.
        Muestra/oculta el joystick según el modo.
        """
        if mode == "manual":
            self.window.show_pan_tilt_controls()
        elif mode == "auto":
            self.window.hide_pan_tilt_controls()
        elif mode is None:  # Cámara detenida
            self.window.hide_pan_tilt_controls()
    
    def _on_joystick_control(self, pan_dir: int, tilt_dir: int) -> None:
        """
        Callback del joystick para controlar los servos.
        Mantiene la lógica del control pan/tilt fuera de la GUI.
        """
        if not self.camera_adapter:
            return
        
        if not hasattr(self.camera_adapter, 'pan_tilt_controller'):
            return #camera_adapter no tiene pan_tilt_controller
        
        pan_tilt = self.camera_adapter.pan_tilt_controller
        
        # Pan (izquierda/derecha)
        if pan_dir == -1:
            pan_tilt.move_pan_left()
        elif pan_dir == 1:
            pan_tilt.move_pan_right()
        
        # Tilt (arriba/abajo)
        if tilt_dir == 1:
            pan_tilt.move_tilt_up()
        elif tilt_dir == -1:
            pan_tilt.move_tilt_down()

    def set_voice_command_adapter(self, voice_command_adapter: VoiceCommandAdapter, mic_adapter: MicrophonePort) -> None:
        self.voice_command_adapter = voice_command_adapter
        
        self._mic_adapter = mic_adapter
        
        self.window.on_start_recording = self.start_recording
        self.window.on_stop_recording = self.stop_recording
        self.window.on_listen_recording_done = self._handle_voice_recording_done

    def start_recording(self) -> None:
        if not self._mic_adapter:
            return
        
        result = self._mic_adapter.start_recording()
        if not result.get("success"):
            self.logger.warning(f"Error iniciando grabación: {result.get('message', '')}")

    def stop_recording(self) -> dict:
        if not self._mic_adapter:
            return {"success": False}
        
        result = self._mic_adapter.stop_recording()
        if result.get("success"):
            self._last_recording_path = result.get("path")
        return result

    def _handle_voice_recording_done(self) -> None:
        if not self.voice_command_adapter or not self._last_recording_path:
            self.logger.error("Error: No hay archivo grabado")
            return
        
        try:
            result = self.voice_command_adapter.interpret_voice_command(self._last_recording_path)

            if result["success"]:
                transcript = result.get("transcript")
                if transcript:
                    self.logger.info(f"📝 Transcripción: {transcript}")
                self.logger.info(result["message"])
            else:
                self.logger.info(result["message"])
                
        except Exception as e:
            self.logger.error(f"Error procesando grabación: {str(e)}")

    def run(self) -> None:
        self.window.run()

    def close(self) -> None:
        self.window.close()
