from datetime import datetime
from pathlib import Path
from typing import Optional

import sounddevice as sd
import soundfile as sf

from src.domain.ports.outbound.microphone_ports import MicrophonePort


class SoundDeviceMicrophoneAdapter(MicrophonePort):
    """Adaptador de micrófono usando sounddevice + soundfile."""

    def __init__(
        self,
        output_dir: Optional[str] = None,
        sample_rate: int = 44100,
        channels: int = 1,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.output_dir = Path(output_dir or "user_data/media")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        try:
            devices = sd.query_devices()
            return any((dev.get("max_input_channels", 0) or 0) > 0 for dev in devices)
        except Exception:
            return False

    def record(self, duration_sec: float) -> dict[str, str | bool]:
        if duration_sec <= 0:
            return {"success": False, "message": "La duración debe ser mayor que 0 segundos."}

        # Limitar a 10 minutos para seguridad
        if duration_sec > 600:
            return {"success": False, "message": "Duración demasiado larga (máx 600s)."}

        if not self.is_available():
            return {
                "success": False,
                "message": "No se detectó ningún micrófono disponible. Conecta uno e inténtalo nuevamente.",
            }

        try:
            # Configurar defaults
            sd.default.samplerate = self.sample_rate
            sd.default.channels = self.channels

            frames = int(duration_sec * self.sample_rate)
            audio = sd.rec(frames, samplerate=self.sample_rate, channels=self.channels, dtype="float32")
            sd.wait()

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.output_dir / f"recording_{ts}.wav"
            sf.write(file_path, audio, self.sample_rate)

            return {
                "success": True,
                "message": f"Audio grabado correctamente: {file_path}",
                "path": str(file_path),
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "success": False,
                "message": f"Error grabando audio: {exc}",
            }
