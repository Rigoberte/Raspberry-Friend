from datetime import datetime
from pathlib import Path
from typing import Optional
import numpy as np
import time

import sounddevice as sd
import soundfile as sf

from src.domain.ports.outbound.microphone_ports import MicrophonePort


class MicrophoneAdapter(MicrophonePort):
    """Adaptador de micrófono usando sounddevice + soundfile.
    
    Proporciona grabación de audio bloqueante y no-bloqueante con validación
    y manejo robusto de errores.
    """

    def __init__(
            self,
            output_dir: Optional[str] = None,
            sample_rate: int = 44100,
            channels: int = 1,
        ) -> None:
        if sample_rate <= 0:
            raise ValueError("sample_rate debe ser mayor que 0")
        if channels <= 0:
            raise ValueError("channels debe ser mayor que 0")

        self.sample_rate = sample_rate
        self.channels = channels
        self.output_dir = Path(output_dir or "user_data/media")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Para grabación interactiva (press/release)
        self._recording = False
        self._audio_stream = None
        self._recorded_frames = []

    def is_available(self) -> bool:
        """Verifica si hay un micrófono disponible.
        
        Returns:
            True si hay al menos un micrófono con canal de entrada, False en caso contrario
        """
        try:
            devices: list[dict] = sd.query_devices()
            return any((dev.get("max_input_channels", 0) or 0) > 0 for dev in devices)
        except Exception:
            return False

    def record(self, duration_sec: float) -> dict[str, str | bool]:
        """Realiza una grabación de audio de duración fija (bloqueante).
        
        Args:
            duration_sec: Duración de la grabación en segundos
            
        Returns:
            Dict con las claves:
                - success: bool indicando si fue exitosa
                - message: str con detalles del resultado
                - path: str (solo si success=True) con la ruta del archivo
        """
        if duration_sec <= 0:
            return {"success": False, "message": "Duration must be greater than 0 seconds."}

        if duration_sec > 600:
            return {"success": False, "message": "Duration too long (max 600s)."}

        try:
            self.start_recording()
            time.sleep(duration_sec)
            recording_result = self.stop_recording()
            
            if not recording_result.get("success", False):
                return recording_result
            
            file_path = recording_result["path"]

            return {
                "success": True,
                "message": f"Audio recorded successfully: {file_path}",
                "path": str(file_path),
            }
        except Exception as e:  # noqa: BLE001
            return {
                "success": False,
                "message": f"Error recording audio: {e}",
            }

    def start_recording(self) -> dict[str, str | bool]:
        """Inicia grabación no-bloqueante mediante callback.
        
        Debe llamarse desde eventos de GUI (ej: mouse/touch press).
        
        Returns:
            Dict con las claves:
                - success: bool indicando si la grabación se inició
                - message: str con detalles del resultado
        """
        if self._recording:
            return {"success": False, "message": "There is already an ongoing recording."}
        
        if not self.is_available():
            return {"success": False, "message": "No microphone detected."}
        
        try:
            self._recording = True
            self._recorded_frames = []
            
            sd.default.samplerate = self.sample_rate
            sd.default.channels = self.channels
            
            def audio_callback(indata, frames, time_obj, status):
                """Callback ejecutado cada bloque de audio capturado."""
                if status:
                    pass
                self._recorded_frames.append(indata.copy())
            
            self._audio_stream = sd.InputStream(
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype="float32",
                callback=audio_callback,
                blocksize=2048
            )
            self._audio_stream.start()
            
            return {"success": True, "message": "Recording started"}
        
        except Exception as e:
            self._recording = False
            return {"success": False, "message": f"Error starting recording: {e}"}

    def stop_recording(self) -> dict[str, str | bool]:
        """
        Stops the recording and saves the file.
        Should be called from _on_listen_release in the GUI.
        
        Returns:
            Dict with success, message, and path of the recorded file
        """
        if not self._recording:
            return {"success": False, "message": "No ongoing recording"}
        
        try:
            if self._audio_stream:
                self._audio_stream.stop()
                self._audio_stream.close()
                self._audio_stream = None
            
            if not self._recorded_frames:
                return {
                    "success": False,
                    "message": "No audio captured"
                }
            
            audio_data = np.concatenate(self._recorded_frames, axis=0)

            audio_file_result = self._create_audio_file(audio_data)
            
            if not audio_file_result.get("success", False):
                return audio_file_result
            
            file_path = audio_file_result["path"]
            
            return {
                "success": True,
                "message": f"Audio recorded successfully: {file_path}",
                "path": str(file_path)
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error stopping recording: {e}"
            }
        
        finally:
            self._recording = False
            self._recorded_frames = []

    def _create_audio_file(self, audio_data: np.ndarray) -> dict[str, str | bool]:
        if audio_data.size == 0:
            return {"success": False, "message": "Audio data is empty."}

        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.output_dir / f"audio_{ts}.wav"
            sf.write(file_path, audio_data, self.sample_rate)

            return {
                "success": True,
                "message": f"Audio file created successfully: {file_path}",
                "path": str(file_path),
            }
        except Exception as e:  # noqa: BLE001
            return {
                "success": False,
                "message": f"Error creating audio file: {e}",
            }