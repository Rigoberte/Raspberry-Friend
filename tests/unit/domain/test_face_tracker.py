"""
Unit tests for Face Tracker

Tests the FaceTracker algorithm without hardware dependencies.
"""

import pytest
from src.domain.models.face_tracker import FaceTracker


class TestFaceTracker:
    """Test suite for FaceTracker algorithm."""
    
    def test_initialization(self):
        """Test tracker initializes with correct parameters."""
        tracker = FaceTracker()
        
        assert tracker.center_x == 320
        assert tracker.center_y == 240
        assert tracker.sensitivity == 0.015
        assert tracker.deadzone == 10
    
    def test_custom_initialization(self):
        """Test tracker with custom parameters."""
        tracker = FaceTracker(
            center_x=640,
            center_y=480,
            sensitivity=0.02,
            deadzone=20
        )
        
        assert tracker.center_x == 640
        assert tracker.center_y == 480
        assert tracker.sensitivity == 0.02
        assert tracker.deadzone == 20
    
    def test_face_centered(self):
        """Test when face is centered in frame (no movement)."""
        tracker = FaceTracker(center_x=320, center_y=240)
        
        # Face at center
        new_pan, new_tilt = tracker.calculate_servo_angles(
            face_x=280,      # Center at 320
            face_y=200,      # Center at 240
            face_w=80,
            face_h=80,
            current_pan=90,
            current_tilt=90
        )
        
        # Should stay close to current angles due to deadzone
        assert abs(new_pan - 90) <= 1
        assert abs(new_tilt - 90) <= 1
    
    def test_face_to_the_right(self):
        """Test face on the right side (pan should increase)."""
        tracker = FaceTracker(center_x=320, center_y=240)
        
        # Face to the right
        new_pan, new_tilt = tracker.calculate_servo_angles(
            face_x=420,      # Center at 460
            face_y=200,
            face_w=80,
            face_h=80,
            current_pan=90,
            current_tilt=90
        )
        
        # Pan should increase to follow face right
        assert new_pan > 90
        # Tilt should remain mostly unchanged
        assert abs(new_tilt - 90) <= 2
    
    def test_face_to_the_left(self):
        """Test face on the left side (pan should decrease)."""
        tracker = FaceTracker(center_x=320, center_y=240)
        
        # Face to the left
        new_pan, new_tilt = tracker.calculate_servo_angles(
            face_x=180,      # Center at 220
            face_y=200,
            face_w=80,
            face_h=80,
            current_pan=90,
            current_tilt=90
        )
        
        # Pan should decrease to follow face left
        assert new_pan < 90
        # Tilt should remain mostly unchanged
        assert abs(new_tilt - 90) <= 2
    
    def test_face_above_center(self):
        """Test face above center (tilt should decrease)."""
        tracker = FaceTracker(center_x=320, center_y=240)
        
        # Face above center
        new_pan, new_tilt = tracker.calculate_servo_angles(
            face_x=280,
            face_y=100,      # Center at 140
            face_w=80,
            face_h=80,
            current_pan=90,
            current_tilt=90
        )
        
        # Pan should remain mostly unchanged
        assert abs(new_pan - 90) <= 2
        # Tilt should decrease
        assert new_tilt < 90
    
    def test_face_below_center(self):
        """Test face below center (tilt should increase)."""
        tracker = FaceTracker(center_x=320, center_y=240)
        
        # Face below center
        new_pan, new_tilt = tracker.calculate_servo_angles(
            face_x=280,
            face_y=340,      # Center at 380
            face_w=80,
            face_h=80,
            current_pan=90,
            current_tilt=90
        )
        
        # Pan should remain mostly unchanged
        assert abs(new_pan - 90) <= 2
        # Tilt should increase
        assert new_tilt > 90
    
    def test_angle_constraints(self):
        """Test that angles are constrained to 0-180 range."""
        tracker = FaceTracker(center_x=320, center_y=240)
        
        # Extreme case: face far to the right
        new_pan, new_tilt = tracker.calculate_servo_angles(
            face_x=600,      # Far right
            face_y=200,
            face_w=80,
            face_h=80,
            current_pan=90,
            current_tilt=90
        )
        
        # Should be constrained to max 180
        assert 0 <= new_pan <= 180
        assert 0 <= new_tilt <= 180
        
        # Extreme case: face far to the left
        new_pan, new_tilt = tracker.calculate_servo_angles(
            face_x=0,        # Far left
            face_y=200,
            face_w=80,
            face_h=80,
            current_pan=90,
            current_tilt=90
        )
        
        # Should be constrained to min 0
        assert 0 <= new_pan <= 180
        assert 0 <= new_tilt <= 180
    
    def test_deadzone_prevents_small_movements(self):
        """Test that deadzone prevents micro-adjustments."""
        tracker = FaceTracker(center_x=320, center_y=240, deadzone=10)
        
        # Face slightly off-center but within deadzone
        new_pan, new_tilt = tracker.calculate_servo_angles(
            face_x=315,      # Center at 355, error = -35 (not enough)
            face_y=235,      # Center at 275, error = -35 (not enough)
            face_w=80,
            face_h=80,
            current_pan=90,
            current_tilt=90
        )
        
        # Should not move significantly due to deadzone
        assert abs(new_pan - 90) < 1
        assert abs(new_tilt - 90) < 1
    
    def test_sensitivity_affects_movement(self):
        """Test that sensitivity parameter affects movement magnitude."""
        # Low sensitivity
        tracker_low = FaceTracker(center_x=320, center_y=240, sensitivity=0.005)
        pan_low, tilt_low = tracker_low.calculate_servo_angles(
            face_x=420, face_y=240, face_w=80, face_h=80,
            current_pan=90, current_tilt=90
        )
        
        # High sensitivity
        tracker_high = FaceTracker(center_x=320, center_y=240, sensitivity=0.05)
        pan_high, tilt_high = tracker_high.calculate_servo_angles(
            face_x=420, face_y=240, face_w=80, face_h=80,
            current_pan=90, current_tilt=90
        )
        
        # Higher sensitivity should cause larger pan movement
        assert abs(pan_high - 90) > abs(pan_low - 90)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
