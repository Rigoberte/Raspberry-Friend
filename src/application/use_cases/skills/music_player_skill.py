"""
MusicPlayerSkill: handles music playback commands.
"""
import os
import time

from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.music_player_ports import MusicPlayerPort

class MusicPlayerSkill(RobotSkill):
    """
    Handles 'music' commands. For now, returns a placeholder response.
    """
    def __init__(self, service: MusicPlayerPort):
        super().__init__(
            {
                "play-mp3" : "Play a specified mp3 song.", 
                "pause-song" : "Pause the current song.", 
                "resume-song" : "Resume the paused song.", 
                "rewind-song" : "Rewind the current song to the beginning.", 
                "stop-song" : "Stop the current song.", 
                "next-song" : "Play the next song in the playlist.", 
                "previous-song" : "Play the previous song in the playlist.",
                "add-to-playlist" : "Add a song to the playlist.",
                "current-song" : "Get the currently playing song.",
                "play-current-folder" : "Play all songs in the current folder.",
                "get-pos" : "Get the current position of the song in seconds.",
                "volume-up" : "Increase the volume.",
                "volume-down" : "Decrease the volume.",
                "set-volume" : "Set the volume to a specific level."
            }
        )
        self.service = service

    def handle(self, command: Command) -> CommandResult:
        match command.get_name():
            case "play-mp3":
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
                command_result = CommandResult(
                    success=True,
                    message=f"Now playing: '{self.__current_song__()}'."
                )

            case "play-current-folder":
                command_result = self.__play_current_folder__(command)

            case "get-pos":
                command_result = self.__get_pos__()

            case "volume-up":
                command_result = self.__volume_up__()
            
            case "volume-down":
                command_result = self.__volume_down__()

            case "set-volume":
                command_result = self.__set_volume__(command)
                
        return command_result
    
    def __play_song__(self, command: Command) -> CommandResult:
        path = command.get_args().get("path") or command.get_args().get("text", "")
        if not path:
            return CommandResult(False, "Usage: play-file <path>")
        
        command_result = self.service.play_song(path)

        return self.__handle_command_result__(
            command_result, 
            success_message="", 
            failure_message= "Failed to play song"
        )

    def __pause_song__(self) -> CommandResult:
        command_result = self.service.pause_song()

        return self.__handle_command_result__(
            command_result, 
            success_message="Song paused",
            failure_message="Failed to pause song"
        )
    
    def __resume_song__(self) -> CommandResult:
        command_result = self.service.resume_song()
        
        return self.__handle_command_result__(
            command_result,
            success_message="Song resumed",
            failure_message="Failed to resume song"
        )
    
    def __rewind_song__(self) -> CommandResult:
        command_result = self.service.rewind_song()

        return self.__handle_command_result__(
            command_result,
            success_message="Song rewound to the beginning",
            failure_message="Failed to rewind song"
        )

    def __stop_song__(self) -> CommandResult:
        command_result = self.service.stop_song()
        
        return self.__handle_command_result__(
            command_result,
            success_message="Song stopped",
            failure_message="Failed to stop song"
        )
    
    def __next_song__(self) -> CommandResult:
        command_result = self.service.next_song()

        return self.__handle_command_result__(
            command_result,
            success_message="Skipped to next song",
            failure_message="Failed to skip to next song"
        )
    
    def __previous_song__(self) -> CommandResult:
        command_result = self.service.previous_song()

        return self.__handle_command_result__(
            command_result,
            success_message="Skipped to previous song",
            failure_message="Failed to skip to previous song"
        )
    
    def __add_to_playlist__(self, command: Command) -> CommandResult:
        song = command.get_args().get("text", "unknown song")

        command_result = self.service.add_to_playlist(song)

        return self.__handle_command_result__(
            command_result,
            success_message=f"Added '{song}' to playlist.",
            failure_message=f"Failed to add '{song}' to playlist"
        )
    
    def __current_song__(self) -> str:
        return self.service.current_song()
    
    def __play_current_folder__(self, command: Command) -> CommandResult:
        raise NotImplementedError("play-current-folder command is not yet implemented.")

    def __get_pos__(self) -> int:
        return self.service.get_pos()
    
    def __volume_up__(self) -> CommandResult:
        command_result = self.service.volume_up()

        return self.__handle_command_result__(
            command_result,
            success_message="Volume increased",
            failure_message="Failed to increase volume"
        )
    
    def __volume_down__(self) -> CommandResult:
        command_result = self.service.volume_down()

        return self.__handle_command_result__(
            command_result,
            success_message="Volume decreased",
            failure_message="Failed to decrease volume"
        )
    
    def __set_volume__(self, command: Command) -> CommandResult:
        text = str(command.get_args().get("text"))
        level = text.split("-")[0].strip() if text else None
        
        if not level or not level.isdigit():
            return CommandResult(False, "Volume level must be an integer between 0 and 100.")

        if level is None:
            return CommandResult(False, "Usage: set-volume <level>")
        
        level_int = max(0, min(float(level) / 100, 1.0))
        
        command_result = self.service.set_volume(level_int)

        return self.__handle_command_result__(
            command_result,
            success_message=f"Volume set to {level_int * 100:.0f}%",
            failure_message="Failed to set volume"
        )
    
    def __handle_command_result__(self, command_result: dict[str, str | bool], success_message: str, failure_message: str) -> CommandResult:
        if not command_result.get("success", False):
            return self.__build_failure_result__(command_result, failure_message)
        
        return self.__build_success_result__(command_result, success_message)
    
    def __build_success_result__(self, command_result: dict[str, str | bool], success_message: str) -> CommandResult:
        duration_s = float(command_result.get("duration", 0) or 0)
        file_path = str(command_result.get("file", command_result))
        track = os.path.basename(file_path)
        
        time.sleep(0.1)  # brief pause to ensure state is updated
        if self.service.is_busy():
            current_song = os.path.basename(self.service.current_song())

            return CommandResult(
                success=True, 
                message=success_message + ". " if success_message else "" + f"Now playing '{current_song}'.",
                data={
                    "path": file_path,
                    "track": track,
                    "duration_s": duration_s,
                }
            )

        return CommandResult(
            success=True, 
            message=success_message
        )
    
    def __build_failure_result__(self, command_result: dict[str, str | bool], failure_message: str) -> CommandResult:
        return CommandResult(
            success=False,
            message=f"{failure_message}. Error: {command_result.get('error-message', 'Unknown error')}"
        )