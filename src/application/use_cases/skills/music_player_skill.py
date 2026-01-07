"""
MusicPlayerSkill: handles music playback commands.
"""
import time
import os

from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.music_player_ports import MusicPlayerPort

class MusicPlayerSkill(RobotSkill):
    """
    Handles 'music' commands. For now, returns a placeholder response.
    """
    def __init__(self, service: MusicPlayerPort):
        self.service = service

    def supported_commands(self) -> list[str]:
        return [
            "play-song", "pause-song", "resume-song", 
            "rewind-song", "stop-song", 
            "next-song", "previous-song", 
            "add-to-playlist", "current-song",
            "play-current-folder"
            ]
    
    def handle(self, command: Command) -> CommandResult:
        match command.get_name():
            case "play-song":
                command_result = self.__play_song__(command)
            
            case "pause-song":
                command_result = self.__pause_song__()

            case "resume-song":
                command_result = self.__resume_song__()

            case "rewind-song":
                command_result = self.__rewind_song__()

            case "stop-song":
                command_result = self.__stop_song__()

            case "next-song":
                command_result = self.__next_song__()

            case "previous-song":
                command_result = self.__previous_song__()

            case "add-to-playlist":
                command_result = self.__add_to_playlist__(command)

            case "current-song":
                command_result = {
                    "success": True,
                    "message": f"Now playing: '{self.__current_song__()}'."
                }

            case "play-current-folder":
                command_result = self.__play_current_folder__(command)
                
        success = command_result.get("success", False)
        message = command_result.get("message", "No message provided")
        
        return CommandResult(success=success, message=message)
    
    def __play_song__(self, command: Command) -> dict[str, str | bool]:
        song = command.get_args().get("text", "unknown song")
        
        command_result = self.service.play_song(song)

        return self.__handle_command_result__(
            command_result, 
            success_message=f"", 
            failure_message=f"Failed to play '{song}'"
        )

    def __pause_song__(self) -> dict[str, str | bool]:
        command_result = self.service.pause_song()

        return self.__handle_command_result__(
            command_result, 
            success_message="Song paused",
            failure_message="Failed to pause song"
        )
    
    def __resume_song__(self) -> dict[str, str | bool]:
        command_result = self.service.resume_song()
        
        return self.__handle_command_result__(
            command_result,
            success_message="Song resumed",
            failure_message="Failed to resume song"
        )
    
    def __rewind_song__(self) -> dict[str, str | bool]:
        command_result = self.service.rewind_song()

        return self.__handle_command_result__(
            command_result,
            success_message="Song rewound to the beginning",
            failure_message="Failed to rewind song"
        )

    def __stop_song__(self) -> dict[str, str | bool]:
        command_result = self.service.stop_song()
        
        return self.__handle_command_result__(
            command_result,
            success_message="Song stopped",
            failure_message="Failed to stop song"
        )
    
    def __next_song__(self) -> dict[str, str | bool]:
        command_result = self.service.next_song()

        return self.__handle_command_result__(
            command_result,
            success_message="Skipped to next song",
            failure_message="Failed to skip to next song"
        )
    
    def __previous_song__(self) -> dict[str, str | bool]:
        command_result = self.service.previous_song()

        return self.__handle_command_result__(
            command_result,
            success_message="Skipped to previous song",
            failure_message="Failed to skip to previous song"
        )
    
    def __add_to_playlist__(self, command: Command) -> dict[str, str | bool]:
        song = command.get_args().get("text", "unknown song")

        command_result = self.service.add_to_playlist(song)

        return self.__handle_command_result__(
            command_result,
            success_message=f"Added '{song}' to playlist.",
            failure_message=f"Failed to add '{song}' to playlist"
        )
    
    def __current_song__(self) -> str:
        return self.service.current_song()
    
    def __play_current_folder__(self, command: Command) -> dict[str, str | bool]:
        raise NotImplementedError("play-current-folder command is not yet implemented.")

    def __get_pos__(self) -> int:
        return self.service.get_pos()
    
    def __handle_command_result__(self, command_result: dict[str, str | bool], success_message: str, failure_message: str) -> dict[str, str | bool]:
        if not command_result.get("success", False):
            return {
                "success": False, 
                "message": f"{failure_message}. Error: {command_result.get('message', 'Unknown error')}"
            }
        
        time.sleep(0.1)  # brief pause to ensure state is updated
        if self.service.is_busy():
            current_song = os.path.basename(self.service.current_song())

            return {
                "success": True, 
                "message": success_message + ". " if success_message else "" + f"Now playing '{current_song}'.",
                "duration": command_result.get("duration", 0),
                "file": command_result.get("file", "")
            }

        return {
            "success": True, 
            "message": success_message
        }