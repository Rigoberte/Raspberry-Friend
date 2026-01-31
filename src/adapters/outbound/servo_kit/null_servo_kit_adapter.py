"""
Null Object Pattern implementation for ServoKit.
Provides a safe no-op implementation when servo kit hardware is not available.
"""

from src.domain.ports.outbound.servo_kit_ports import ServoKitPort


class NullServoKitAdapter(ServoKitPort):
    """
    Null Object Pattern implementation for ServoKit.

    This adapter provides a safe, silent no-op behavior when servo kit
    hardware is not available or should be disabled. It allows the system
    to function normally without the servo motor hardware.

    All operations return success=False with appropriate messages,
    allowing callers to handle the situation gracefully.
    """

    def __init__(self):
        """Initialize the Null servo kit adapter."""
        pass

    def get_angle(self) -> dict[str, float | str | bool]:
        return {
            "angle": 0,
            "success": False,
            "error-message": "Servo kit is not available"
        }
    
    def increase_angle(self) -> dict[str, str | bool]:
        return {
            "success": False,
            "error-message": "Servo kit is not available"
        }
    
    def decrease_angle(self) -> dict[str, str | bool]:
        return {
            "success": False,
            "error-message": "Servo kit is not available"
        }

    def reset(self) -> dict[str, str | bool]:
        return {
            "success": False,
            "error-message": "Servo kit is not available"
        }