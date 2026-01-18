from src.domain.ports.outbound.tts_ports import TTSPort
import pyttsx3
import threading


class Pyttsx3TTSAdapter(TTSPort):
    """
    Text-to-Speech adapter using pyttsx3 library.
    Works offline and is compatible with Raspberry Pi.
    Uses threading with per-speech engine initialization to handle pyttsx3's limitations.
    """
    
    def __init__(self, rate: int = 150, volume: float = 0.9, language: str = "es") -> None:
        """
        Initialize the TTS adapter.
        
        Args:
            rate: Speech rate in words per minute (default: 150)
            volume: Volume level between 0.0 and 1.0 (default: 0.9)
            language: Language code for the voice (default: "es" for Spanish)
        """
        self._rate = rate
        self._volume = volume
        if language == "es":
            self._voice_id = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-MX_SABINA_11.0'
        elif language == "en":
            self._voice_id = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
        else:
            raise ValueError("Unsupported language. Supported languages are 'es' and 'en'.")
        
        self._is_initialized = True
        self._is_speaking = False
        self._speech_thread = None
        self._lock = threading.Lock()
    
    def _speak_in_thread(self, text: str) -> None:
        """
        Run speech in a separate thread with a fresh engine instance.
        This is necessary because pyttsx3's runAndWait() has issues in daemon threads.
        
        Args:
            text: The text to be spoken
        """
        try:
            # Crear una nueva instancia del motor para cada reproducción
            # Esto evita los bugs de pyttsx3 con el event loop
            engine = pyttsx3.init()
            engine.setProperty('rate', self._rate)
            engine.setProperty('volume', self._volume)
            engine.setProperty('voice', self._voice_id)
            # Reproducir el texto
            engine.say(text)
            engine.runAndWait()
            
        except Exception as e:
            print(f"Error during speech: {e}")
        finally:
            self._is_speaking = False
    
    def speak(self, text: str) -> dict[str, str | bool]:
        """
        Convert text to speech and play the audio.
        
        Args:
            text: The text to be spoken
            
        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        if not self._is_initialized:
            return {
                "success": False,
                "error-message": "TTS engine not initialized"
            }
        
        if not text or not text.strip():
            return {
                "success": False,
                "error-message": "Text cannot be empty"
            }
        
        try:
            # Esperar a que termine el audio anterior
            if self._is_speaking and self._speech_thread:
                self._speech_thread.join(timeout=30)
            
            self._is_speaking = True
            
            # Crear e iniciar un nuevo thread para la reproducción
            self._speech_thread = threading.Thread(
                target=self._speak_in_thread,
                args=(text,),
                daemon=False
            )
            self._speech_thread.start()
            
            return {
                "success": True,
                "error-message": ""
            }
        except Exception as e:
            self._is_speaking = False
            return {
                "success": False,
                "error-message": f"Error during speech: {str(e)}"
            }
        
    def stop(self) -> dict[str, str | bool]:
        """
        Stop any ongoing speech.
        
        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        if not self._is_initialized:
            return {
                "success": False,
                "error-message": "TTS engine not initialized"
            }
        
        try:
            self._is_speaking = False
            return {
                "success": True,
                "error-message": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error-message": f"Error stopping speech: {str(e)}"
            }
    
    def is_speaking(self) -> bool:
        """
        Check if TTS is currently speaking.
        
        Returns:
            bool: True if speaking, False otherwise
        """
        return self._is_speaking
    
    def set_rate(self, rate: int) -> dict[str, str | bool]:
        """
        Set the speech rate (words per minute).
        
        Args:
            rate: Speed in words per minute (typically 100-200)
            
        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        if not self._is_initialized:
            return {
                "success": False,
                "error-message": "TTS engine not initialized"
            }
        
        try:
            self._rate = rate
            return {
                "success": True,
                "error-message": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error-message": f"Error setting rate: {str(e)}"
            }
    
    def set_volume(self, volume: float) -> dict[str, str | bool]:
        """
        Set the volume level.
        
        Args:
            volume: Volume level between 0.0 and 1.0
            
        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        if not self._is_initialized:
            return {
                "success": False,
                "error-message": "TTS engine not initialized"
            }
        
        if not 0.0 <= volume <= 1.0:
            return {
                "success": False,
                "error-message": "Volume must be between 0.0 and 1.0"
            }
        
        try:
            self._volume = volume
            return {
                "success": True,
                "error-message": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error-message": f"Error setting volume: {str(e)}"
            }
