"""
CameraSkill: handles camera operations.
"""
from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.camera_ports import CameraPort


class CameraSkill(RobotSkill):
    """
    Handles camera commands like 'turn-on-camera' and 'turn-off-camera'.
    """
    
    def __init__(self, camera_service: CameraPort):
        super().__init__(
            {
                "turn-on-camera": "Turn on and display the camera feed in real-time.",
                "turn-off-camera": "Turn off the camera.",
                "track-my-face": "Track your face in real-time without restarting the camera.",
                "untrack-my-face": "Disable face tracking while keeping the camera on.",
            }
        )
        self.camera_service = camera_service
    
    def handle(self, command: Command) -> CommandResult:
        """
        Handle camera-related commands.
        
        Args:
            command: The command to handle
        
        Returns:
            CommandResult with success status and message
        """
        match command.get_name():
            case "turn-on-camera":
                return self.__turn_on_camera__()
            case "turn-off-camera":
                return self.__turn_off_camera__()
            case "track-my-face":
                return self.__track_my_face__()
            case "untrack-my-face":
                return self.__untrack_my_face__()
            case _:
                return CommandResult(False, f"Unknown camera command: {command.get_name()}")
    
    def __turn_on_camera__(self) -> CommandResult:
        """
        Turn on the camera and display the feed.
        
        Returns:
            CommandResult with success status
        """
        if not self.camera_service.is_camera_available():
            return CommandResult(
                success=False,
                message="No camera detected. Please ensure your camera is connected."
            )
        
        result = self.camera_service.start_camera()
        
        if result.get("success"):
            return CommandResult(
                success=True,
                message="Camera is now on."
            )
        else:
            error_msg = result.get("error-message", "Unknown error")
            return CommandResult(
                success=False,
                message=f"Failed to turn on camera: {error_msg}"
            )

    def __track_my_face__(self) -> CommandResult:
        """
        Enable face tracking using the already running camera.
        """
        if not self.camera_service.is_camera_available():
            return CommandResult(
                success=False,
                message="No camera detected. Please ensure your camera is connected."
            )

        # track_my_face will auto-start the camera if it was off
        result = self.camera_service.track_my_face()

        if result.get("success"):
            return CommandResult(
                success=True,
                message="Face tracking enabled."
            )
        else:
            error_msg = result.get("error-message", "Unknown error")
            return CommandResult(
                success=False,
                message=f"Failed to start face tracking: {error_msg}"
            )

    def __untrack_my_face__(self) -> CommandResult:
        """Disable face tracking but keep camera running."""
        result = self.camera_service.untrack_my_face()

        if result.get("success"):
            return CommandResult(
                success=True,
                message="Face tracking disabled. Camera remains on."
            )
        else:
            error_msg = result.get("error-message", "Unknown error")
            return CommandResult(
                success=False,
                message=f"Failed to disable face tracking: {error_msg}"
            )
    
    def __turn_off_camera__(self) -> CommandResult:
        """
        Turn off the camera.
        
        Returns:
            CommandResult with success status
        """
        result = self.camera_service.stop_camera()
        
        if result.get("success"):
            return CommandResult(
                success=True,
                message="Camera has been turned off."
            )
        else:
            error_msg = result.get("error-message", "Unknown error")
            return CommandResult(
                success=False,
                message=f"Failed to turn off camera: {error_msg}"
            )
