"""
Pan/Tilt servo controller for camera pointing.

Manages the pan and tilt servo motors and provides both manual
(WASD keys) and automatic (face tracking) control modes.
"""

from enum import Enum
from src.domain.models.face_tracker import FaceTracker
from src.adapters.outbound.servo_kit.servo_kit_adapter import AdafruitServoKitAdapter
from src.adapters.outbound.servo_kit.null_servo_kit_adapter import NullServoKitAdapter

class PanTiltControlMode(Enum):
    """Control mode for pan/tilt servos."""
    MANUAL = "manual"
    AUTO = "auto"


class PanTiltController:
    """
    Controller for pan and tilt servo motors.

    Manages:
    - Manual servo control via keyboard input (WASD)
    - Automatic face tracking mode
    - Servo angle constraints
    - State management (current pan/tilt angles)
    """

    DEFAULT_PAN = 90
    DEFAULT_TILT = 90
    MANUAL_STEP = 5  # Degrees per key press
    DEADZONE: int = 50  # Pixels: minimum error to trigger movement
    
    SENSITIVITY: float = 0.005  # Ratio of pixel error to angle adjustment

    def __init__(self):
        """
        Initialize pan/tilt controller.
        """

        try:
            self.pan_port = AdafruitServoKitAdapter(port=0)
            self.tilt_port = AdafruitServoKitAdapter(port=1)
        except RuntimeError:
            # If servo kit is not available, use null adapter
            self.pan_port = NullServoKitAdapter()
            self.tilt_port = NullServoKitAdapter()
        
        self.face_tracker = FaceTracker()
        self.mode = PanTiltControlMode.MANUAL

    def reset(self) -> dict[str, str | bool]:
        """
        Reset pan and tilt to default angles.

        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        pan_result = self.pan_port.reset()
        tilt_result = self.tilt_port.reset()

        if not pan_result["success"]:
            return pan_result
        if not tilt_result["success"]:
            return tilt_result

        return {"success": True, "error-message": ""}

    def move_pan_left(self) -> None:
        """Decrease pan angle (move left)."""
        self.pan_port.decrease_angle()

    def move_pan_right(self) -> None:
        """Increase pan angle (move right)."""
        self.pan_port.increase_angle()

    def move_tilt_up(self) -> None:
        """Increase tilt angle (move up)."""
        self.tilt_port.increase_angle()

    def move_tilt_down(self) -> None:
        """Decrease tilt angle (move down)."""
        self.tilt_port.decrease_angle()

    def track_face(self, face_x: int, face_y: int, face_w: int, face_h: int) -> None:
        """
        Automatically adjust pan/tilt to track a detected face.

        Args:
            face_x: Face bounding box X coordinate
            face_y: Face bounding box Y coordinate
            face_w: Face bounding box width
            face_h: Face bounding box height
        """
        if self.is_manual_mode():
            return  # Do not track in manual mode
        
        error_x, error_y = self.face_tracker.calculate_error_from_face_center(
            face_x, face_y, face_w, face_h
        )

        # Apply deadzone
        if abs(error_x) < self.DEADZONE:
            error_x = 0

        if abs(error_y) < self.DEADZONE:
            error_y = 0
        
        # Calculate angle adjustments
        adjust_pan = error_x * self.SENSITIVITY
        adjust_tilt = error_y * self.SENSITIVITY

        if adjust_pan > 0:
            self.move_pan_right()
        elif adjust_pan < 0:
            self.move_pan_left()

        if adjust_tilt > 0:
            self.move_tilt_up()
        elif adjust_tilt < 0:
            self.move_tilt_down()
        

    def set_manual_mode(self) -> None:
        """Set control mode to manual (WASD keys)."""
        self.mode = PanTiltControlMode.MANUAL

    def set_auto_mode(self) -> None:
        """Set control mode to automatic (face tracking)."""
        self.mode = PanTiltControlMode.AUTO

    def is_manual_mode(self) -> bool:
        """Check if current control mode is manual."""
        return self.mode == PanTiltControlMode.MANUAL
    
    def is_auto_mode(self) -> bool:
        """Check if current control mode is automatic."""
        return self.mode == PanTiltControlMode.AUTO