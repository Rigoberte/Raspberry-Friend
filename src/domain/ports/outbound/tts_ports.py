from abc import ABC, abstractmethod

class TTSPort(ABC):
    """
    Abstract interface for Text-to-Speech (TTS) functionality.
    """
    
    @abstractmethod
    def speak(self, text: str) -> dict[str, str | bool]:
        """
        Convert text to speech and play the audio.
        
        Args:
            text: The text to be spoken
            
        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        raise NotImplementedError
    
    @abstractmethod
    def stop(self) -> dict[str, str | bool]:
        """
        Stop any ongoing speech.
        
        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        raise NotImplementedError
    
    @abstractmethod
    def is_speaking(self) -> bool:
        """
        Check if TTS is currently speaking.
        
        Returns:
            bool: True if speaking, False otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    def set_rate(self, rate: int) -> dict[str, str | bool]:
        """
        Set the speech rate (words per minute).
        
        Args:
            rate: Speed in words per minute (typically 100-200)
            
        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        raise NotImplementedError
    
    @abstractmethod
    def set_volume(self, volume: float) -> dict[str, str | bool]:
        """
        Set the volume level.
        
        Args:
            volume: Volume level between 0.0 and 1.0
            
        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        raise NotImplementedError
