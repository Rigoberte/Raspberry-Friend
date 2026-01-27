from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.tts_ports import TTSPort


class SaySkill(RobotSkill):
    """
    Skill for text-to-speech functionality.
    Converts text to speech and plays it through the system's audio output.
    """
    
    def __init__(self, tts_service: TTSPort):
        """
        Initialize the Say skill.
        
        Args:
            tts_service: Text-to-speech service implementation
        """
        super().__init__({
            "say": "Speak the provided text using text-to-speech."
        })
        self._tts_service = tts_service
    
    def handle(self, command: Command) -> CommandResult:
        """
        Handle the say command.
        
        Args:
            command: Command object containing the text to speak
            
        Returns:
            CommandResult with success status and message
        """
        text = command.get_args().get("text", "")
        
        if not text or not text.strip():
            return CommandResult(
                success=False,
                message="No text provided to speak. Usage: say 'your text here'"
            )
        
        result = self._tts_service.speak(text)
        
        if result.get("success"):
            return CommandResult(
                success=True,
                message=f"Speaking: {text}"
            )
        else:
            error_msg = result.get("error-message", "Unknown error")
            return CommandResult(
                success=False,
                message=f"Failed to speak text: {error_msg}"
            )
