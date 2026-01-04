"""
MusicPlayerSkill: handles music playback commands.
"""
from mutagen.mp3 import MP3
import time
import threading
import sys

from src.model.skills.skill import RobotSkill
from src.model.command.command import Command, CommandResult
from src.services.music_player.music_player_service import MusicPlayerService

class MusicPlayerSkill(RobotSkill):
    """
    Handles 'music' commands. For now, returns a placeholder response.
    """
    def __init__(self, service: MusicPlayerService):
        self.service = service
        self._progress_stop = threading.Event()
        self._progress_thread: threading.Thread | None = None

    def can_handle(self, command: Command) -> bool:
        return command.get_name() in [
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

                time.sleep(0.5)  # brief pause to ensure playback starts
                self._progress_stop.clear()
                self._progress_thread = threading.Thread(
                    target=self.__show_progress_bar__,
                    daemon=True
                )
                self._progress_thread.start()
            
            case "pause-song":
                command_result = self.__pause_song__()

            case "resume-song":
                command_result = self.__resume_song__()

                time.sleep(0.5)  # brief pause to ensure playback resumes
                self._progress_stop.clear()
                self._progress_thread = threading.Thread(
                    target=self.__show_progress_bar__,
                    daemon=True
                )
                self._progress_thread.start()

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

        if not command_result.get("success", False):
            return {
                "success": False, 
                "message": f"Failed to play '{song}'. Error: {command_result.get('message', 'Unknown error')}"
            }
        
        return {
            "success": True, 
            "message": f"Playing '{song.title()}':\n"
            }

    def __pause_song__(self) -> dict[str, str | bool]:
        command_result = self.service.pause_song()

        self._progress_stop.set()
        if self._progress_thread is not None:
            self._progress_thread.join()

        if not command_result.get("success", False):
            return {
                "success": False, 
                "message": f"Failed to pause song. Error: {command_result.get('message', 'Unknown error')}"
            }
        
        return {
            "success": True, 
            "message": "Song paused."
        }
    
    def __resume_song__(self) -> dict[str, str | bool]:
        command_result = self.service.resume_song()

        if not command_result.get("success", False):
            return {
                "success": False, 
                "message": f"Failed to resume song. Error: {command_result.get('message', 'Unknown error')}"
            }
        
        current_song = self.__current_song__()
        
        return {
            "success": True, 
            "message": f"Song resumed. Now playing '{current_song}'."
        }
    
    def __rewind_song__(self) -> dict[str, str | bool]:
        command_result = self.service.rewind_song()

        if not command_result.get("success", False):
            return {
                "success": False, 
                "message": f"Failed to rewind song. Error: {command_result.get('message', 'Unknown error')}"
            }
        
        return {
            "success": True, 
            "message": "Song rewound to the beginning."
        }

    def __stop_song__(self) -> dict[str, str | bool]:
        command_result = self.service.stop_song()
        
        self._progress_stop.set()
        if self._progress_thread is not None:
            self._progress_thread.join()

        if not command_result.get("success", False):
            return {
                "success": False, 
                "message": f"Failed to stop song. Error: {command_result.get('message', 'Unknown error')}"
            }
        
        return {
            "success": True, 
            "message": "Song stopped."
        }
    
    def __next_song__(self) -> dict[str, str | bool]:
        command_result = self.service.next_song()

        if not command_result.get("success", False):
            return {
                "success": False, 
                "message": f"Failed to skip to next song. Error: {command_result.get('message', 'Unknown error')}"
            }
        
        current_song = self.__current_song__()
        return {
            "success": True, 
            "message": f"Now playing next song: '{current_song}'."
        }
    
    def __previous_song__(self) -> dict[str, str | bool]:
        command_result = self.service.previous_song()

        if not command_result.get("success", False):
            return {
                "success": False, 
                "message": f"Failed to skip to previous song. Error: {command_result.get('message', 'Unknown error')}"
            }
        
        current_song = self.__current_song__()
        return {
            "success": True, 
            "message": f"Now playing previous song: '{current_song}'."
        }
    
    def __add_to_playlist__(self, command: Command) -> dict[str, str | bool]:
        song = command.get_args().get("text", "unknown song")

        command_result = self.service.add_to_playlist(song)

        if not command_result.get("success", False):
            return {
                "success": False, 
                "message": f"Failed to add '{song}' to playlist. Error: {command_result.get('message', 'Unknown error')}"
            }
        
        return {
            "success": True, 
            "message": f"Added '{song}' to playlist."
        }
    
    def __current_song__(self) -> str:
        return self.service.current_song()
    
    def __play_current_folder__(self, command: Command) -> dict[str, str | bool]:
        raise NotImplementedError("play-current-folder command is not yet implemented.")

    def __get_pos__(self) -> int:
        return self.service.get_pos()

    def __show_progress_bar__(self, bar_length: int = 30) -> str:
        """
        Generates a textual progress bar.
        """
        current_song = ""
        while self.service.is_busy() and not self._progress_stop.is_set():
            if current_song != self.service.current_song():
                try:
                    current_song = self.service.current_song()
                    audio_total_length = MP3(current_song).info.length
                except Exception:
                    return "No song is currently playing"

            pos_ms = self.__get_pos__()
            current_length = pos_ms / 1000.0
            filled_length = int(bar_length * current_length // audio_total_length)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            time_text = f"{self.__format_time__(current_length)} / {self.__format_time__(audio_total_length)}"

            out = sys.__stdout__  # stdout real (no el wrap de prompt_toolkit)

            #if last line starts with |, overwrite it
            out.write("\033[s")       # save cursor
            out.write("\033[1A")  # up 1 line
            out.write("\r\033[2K")    # clear line
            out.write(f"|{bar}| {time_text}")
            out.write("\033[u")       # restore cursor (vuelve al prompt)
            out.flush()

            time.sleep(1)

        return ""
    
    def __format_time__(self, seconds: int) -> str:
        """
        Formats seconds into MM:SS format.
        """
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"