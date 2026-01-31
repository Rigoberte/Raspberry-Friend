"""
Unit tests for Pan/Tilt Controller

Tests the PanTiltController class with mock servo adapters.
"""

import pytest
from src.domain.models.pan_tilt_controller import PanTiltController, PanTiltControlMode
from src.domain.ports.outbound.servo_kit_ports import ServoKitPort


class MockServoKitAdapter(ServoKitPort):
    """Mock servo kit adapter for testing."""
    
    def __init__(self):
        self.angles = {i: 90 for i in range(16)}
        self.is_init = True
    
    def set_angle(self, port: int, angle: float) -> dict[str, str | bool]:
        if not self.is_init:
            return {"success": False, "error-message": "Not initialized"}
        self.angles[port] = angle
        return {"success": True, "error-message": ""}
    
    def get_angle(self, port: int) -> dict[str, float | str | bool]:
        if not self.is_init:
            return {"angle": 0, "success": False, "error-message": "Not initialized"}
        return {"angle": self.angles[port], "success": True, "error-message": ""}
    
    def reset(self, port: int) -> dict[str, str | bool]:
        self.angles[port] = 90
        return {"success": True, "error-message": ""}
    
    def reset_all(self) -> dict[str, str | bool]:
        for i in range(16):
            self.angles[i] = 90
        return {"success": True, "error-message": ""}
    
    def is_available(self) -> bool:
        return self.is_init


class TestPanTiltController:
    """Test suite for PanTiltController."""
    
    def test_initialization(self):
        """Test controller initializes with correct default values."""
        servo_kit = MockServoKitAdapter()
        controller = PanTiltController(servo_kit)
        
        assert controller.pan == 90
        assert controller.tilt == 90
        assert controller.mode == PanTiltControlMode.MANUAL
        assert controller.is_available() is True
    
    def test_pan_left(self):
        """Test pan left movement."""
        servo_kit = MockServoKitAdapter()
        controller = PanTiltController(servo_kit)
        
        controller.move_pan_left()
        assert controller.pan == 85  # 90 - 5
        assert servo_kit.angles[0] == 85
    
    def test_pan_right(self):
        """Test pan right movement."""
        servo_kit = MockServoKitAdapter()
        controller = PanTiltController(servo_kit)
        
        controller.move_pan_right()
        assert controller.pan == 95  # 90 + 5
        assert servo_kit.angles[0] == 95
    
    def test_tilt_up(self):
        """Test tilt up movement."""
        servo_kit = MockServoKitAdapter()
        controller = PanTiltController(servo_kit)
        
        controller.move_tilt_up()
        assert controller.tilt == 95  # 90 + 5
        assert servo_kit.angles[1] == 95
    
    def test_tilt_down(self):
        """Test tilt down movement."""
        servo_kit = MockServoKitAdapter()
        controller = PanTiltController(servo_kit)
        
        controller.move_tilt_down()
        assert controller.tilt == 85  # 90 - 5
        assert servo_kit.angles[1] == 85
    
    def test_pan_constraints(self):
        """Test pan angle constraints (0-180)."""
        servo_kit = MockServoKitAdapter()
        controller = PanTiltController(servo_kit)
        
        # Test minimum boundary
        controller.pan = 2
        controller.move_pan_left()
        assert controller.pan == 0  # Cannot go below 0
        
        # Test maximum boundary
        controller.pan = 178
        controller.move_pan_right()
        assert controller.pan == 180  # Cannot go above 180
    
    def test_tilt_constraints(self):
        """Test tilt angle constraints (0-180)."""
        servo_kit = MockServoKitAdapter()
        controller = PanTiltController(servo_kit)
        
        # Test minimum boundary
        controller.tilt = 2
        controller.move_tilt_down()
        assert controller.tilt == 0
        
        # Test maximum boundary
        controller.tilt = 178
        controller.move_tilt_up()
        assert controller.tilt == 180
    
    def test_reset(self):
        """Test reset to default angles."""
        servo_kit = MockServoKitAdapter()
        controller = PanTiltController(servo_kit)
        
        # Move servos away from default
        controller.pan = 45
        controller.tilt = 135
        
        # Reset
        controller.reset()
        
        assert controller.pan == 90
        assert controller.tilt == 90
    
    def test_mode_switching(self):
        """Test switching between manual and auto modes."""
        servo_kit = MockServoKitAdapter()
        controller = PanTiltController(servo_kit)
        
        assert controller.get_mode() == PanTiltControlMode.MANUAL
        
        controller.set_mode(PanTiltControlMode.AUTO)
        assert controller.get_mode() == PanTiltControlMode.AUTO
        
        controller.set_mode(PanTiltControlMode.MANUAL)
        assert controller.get_mode() == PanTiltControlMode.MANUAL
    
    def test_face_tracking(self):
        """Test automatic face tracking calculation."""
        servo_kit = MockServoKitAdapter()
        controller = PanTiltController(servo_kit)
        
        # Face directly in center (no movement needed)
        controller.track_face(280, 200, 80, 80)  # x, y, w, h
        # Pan and tilt should be close to default (within deadzone)
        assert abs(controller.pan - 90) < 5
        assert abs(controller.tilt - 90) < 5
        
        # Face to the right (pan should increase)
        initial_pan = controller.pan
        controller.track_face(380, 240, 80, 80)  # Face further right
        assert controller.pan > initial_pan
        
        # Face above center (tilt should decrease)
        initial_tilt = controller.tilt
        controller.track_face(320, 140, 80, 80)  # Face higher up
        assert controller.tilt < initial_tilt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
