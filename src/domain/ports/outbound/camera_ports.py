from abc import ABC, abstractmethod
from typing import Callable, Optional


class CameraPort(ABC):
    """
    Abstract interface for camera operations.
    """
    
    @abstractmethod
    def start_camera(self) -> dict[str, str | bool]:
        """
        Start the camera and display it in real-time.
        
        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        raise NotImplementedError
    
    @abstractmethod
    def stop_camera(self) -> dict[str, str | bool]:
        """
        Stop the camera.
        
        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        raise NotImplementedError
    
    @abstractmethod
    def is_camera_available(self) -> bool:
        """
        Check if camera is available and connected.
        
        Returns:
            True if camera is available, False otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    def set_frame_callback(self, callback: Optional[Callable]) -> None:
        """
        Set a callback function to receive camera frames.
        The callback will be called with each frame as numpy array.
        
        Args:
            callback: Function that accepts a frame (numpy array) or None to disable
        """
        raise NotImplementedError
