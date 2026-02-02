"""
Ports (interfaces) for Pan/Tilt UI control.

Defines contracts for UI components that control pan/tilt servo motors.
This keeps the domain layer decoupled from the GUI implementation.
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional


class PanTiltUIPort(ABC):
    """
    Abstract interface for Pan/Tilt UI controls.
    
    This port defines how the UI layer should expose pan/tilt control.
    It receives callbacks from the application layer to show/hide controls
    based on the camera and face tracking state.
    """

    @abstractmethod
    def show_pan_tilt_controls(self) -> None:
        """
        Show the pan/tilt control UI (e.g., virtual joystick).
        Called when camera starts and face tracking is disabled.
        """
        raise NotImplementedError

    @abstractmethod
    def hide_pan_tilt_controls(self) -> None:
        """
        Hide the pan/tilt control UI.
        Called when camera stops or face tracking is enabled.
        """
        raise NotImplementedError

    @abstractmethod
    def set_pan_tilt_control_callback(self, callback: Optional[Callable[[int, int], None]]) -> None:
        """
        Set callback function for pan/tilt joystick input.
        
        Args:
            callback: Function(pan_direction: int, tilt_direction: int) where:
                     - pan_direction: -1 (left), 0 (center), 1 (right)
                     - tilt_direction: -1 (down), 0 (center), 1 (up)
                     - None to disable callbacks
        """
        raise NotImplementedError
