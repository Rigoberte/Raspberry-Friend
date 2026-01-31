from abc import ABC, abstractmethod


class ServoKitPort(ABC):
    """
    Abstract interface for servo motor control.
    Defines the contract for servo motor operations.
    """

    @abstractmethod
    def get_angle(self) -> dict[str, float | str | bool]:
        """
        Get the current angle of a servo motor.

        Returns:
            dict with 'angle' (float), 'success' (bool) and 'error-message' (str) keys
        """
        raise NotImplementedError
    
    def increase_angle(self) -> dict[str, str | bool]:
        """
        Increase the servo motor angle by a fixed step.

        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        raise NotImplementedError
    
    def decrease_angle(self) -> dict[str, str | bool]:
        """
        Decrease the servo motor angle by a fixed step.

        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> dict[str, str | bool]:
        """
        Reset a servo motor to default angle (90 degrees).

        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        raise NotImplementedError