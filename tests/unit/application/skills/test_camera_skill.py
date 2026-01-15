"""
Unit tests for CameraSkill
"""
import pytest
from unittest.mock import Mock, patch
from src.application.use_cases.skills.camera_skill import CameraSkill
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.camera_ports import CameraPort


class MockCameraAdapter(CameraPort):
    """Mock camera adapter for testing"""
    
    def __init__(self, available=True, start_success=True, stop_success=True):
        self.available = available
        self.start_success = start_success
        self.stop_success = stop_success
        self.start_called = False
        self.stop_called = False
    
    def is_camera_available(self) -> bool:
        return self.available
    
    def start_camera(self) -> dict[str, str | bool]:
        self.start_called = True
        if self.start_success:
            return {"success": True, "error-message": ""}
        return {"success": False, "error-message": "Camera failed to start"}
    
    def stop_camera(self) -> dict[str, str | bool]:
        self.stop_called = True
        if self.stop_success:
            return {"success": True, "error-message": ""}
        return {"success": False, "error-message": "Camera failed to stop"}


class TestCameraSkill:
    
    def test_camera_skill_has_correct_commands(self):
        """Test that CameraSkill registers the correct commands"""
        camera = MockCameraAdapter()
        skill = CameraSkill(camera_service=camera)
        
        assert "turn-on-camera" in skill.supported_commands()
        assert "turn-off-camera" in skill.supported_commands()
    
    def test_can_handle_turn_on_camera(self):
        """Test that skill can handle 'turn-on-camera' command"""
        camera = MockCameraAdapter()
        skill = CameraSkill(camera_service=camera)
        
        command = Mock(spec=Command)
        command.get_name.return_value = "turn-on-camera"
        
        assert skill.can_handle(command) is True
    
    def test_can_handle_turn_off_camera(self):
        """Test that skill can handle 'turn-off-camera' command"""
        camera = MockCameraAdapter()
        skill = CameraSkill(camera_service=camera)
        
        command = Mock(spec=Command)
        command.get_name.return_value = "turn-off-camera"
        
        assert skill.can_handle(command) is True
    
    def test_turn_on_camera_success(self):
        """Test successful camera startup"""
        camera = MockCameraAdapter(available=True, start_success=True)
        skill = CameraSkill(camera_service=camera)
        
        command = Mock(spec=Command)
        command.get_name.return_value = "turn-on-camera"
        
        result = skill.handle(command)
        
        assert result.is_successful() is True
        assert camera.start_called is True
        assert "Camera is now on" in result.get_message()
    
    def test_turn_on_camera_not_available(self):
        """Test turning on camera when not available"""
        camera = MockCameraAdapter(available=False)
        skill = CameraSkill(camera_service=camera)
        
        command = Mock(spec=Command)
        command.get_name.return_value = "turn-on-camera"
        
        result = skill.handle(command)
        
        assert result.is_successful() is False
        assert "No camera detected" in result.get_message()
        assert camera.start_called is False
    
    def test_turn_on_camera_failure(self):
        """Test camera startup failure"""
        camera = MockCameraAdapter(available=True, start_success=False)
        skill = CameraSkill(camera_service=camera)
        
        command = Mock(spec=Command)
        command.get_name.return_value = "turn-on-camera"
        
        result = skill.handle(command)
        
        assert result.is_successful() is False
        assert "Failed to turn on camera" in result.get_message()
        assert camera.start_called is True
    
    def test_turn_off_camera_success(self):
        """Test successful camera shutdown"""
        camera = MockCameraAdapter(available=True, stop_success=True)
        skill = CameraSkill(camera_service=camera)
        
        command = Mock(spec=Command)
        command.get_name.return_value = "turn-off-camera"
        
        result = skill.handle(command)
        
        assert result.is_successful() is True
        assert camera.stop_called is True
        assert "Camera has been turned off" in result.get_message()
    
    def test_turn_off_camera_failure(self):
        """Test camera shutdown failure"""
        camera = MockCameraAdapter(available=True, stop_success=False)
        skill = CameraSkill(camera_service=camera)
        
        command = Mock(spec=Command)
        command.get_name.return_value = "turn-off-camera"
        
        result = skill.handle(command)
        
        assert result.is_successful() is False
        assert "Failed to turn off camera" in result.get_message()
        assert camera.stop_called is True
