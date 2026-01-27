import os
import threading
from difflib import get_close_matches

from .skill import RobotSkill
from src.domain.models.command import Command, CommandResult

ROOT = os.path.join(".", "user_data")

class FileExplorerSkill(RobotSkill):
    """
    Handles 'list_files' commands to list files in a given directory.
    """
    def __init__(self):
        super().__init__(
            {
                "list-files": "List files in the current directory or a specified directory.",
                "ls": "List files in the current directory or a specified directory.",
                "cd": "Change the current directory to a specified directory.",
                "get-path": "Get the full path of a specified file or the current directory.",
                "select-file": "Select a file in current directory and return its full path (for workflows).",
                "find-song": "Find an mp3 by name under user_data and return the path.",
                "..": "Navigate up to the parent directory."
            }
        )
        self._directory = ROOT  # Default directory
        self._lock = threading.Lock()

    def handle(self, command: Command) -> CommandResult:
        match command.get_name():
            case "list-files" | "ls":
                return self.__list_files__(command)
            case "cd":
                return self.__cd__(command)
            case "get-path":
                return self.__get_path__(command)
            case "select-file":
                return self.__select_file__(command)
            case "find-song":
                return self.__find_song__(command)
            case "..":
                return self.__navigate_up__()
    
    def __list_files__(self, command: Command) -> CommandResult:
        command_text = command.get_args().get("text", "")
        if command_text != "":
            new_directory = os.path.join(self._directory, command_text)
        else:
            new_directory = self._directory
        
        try:
            files = os.listdir(new_directory)
            with self._lock:
                self._directory = new_directory
            
            if not files:
                return CommandResult(success=True, message=f"No files found in directory '{new_directory}'.")
            
            folders_list = "\n".join(["🗀 " + f for f in files if os.path.isdir(os.path.join(new_directory, f))])
            not_folders_list = "\n".join(["🗎 " + f for f in files if not os.path.isdir(os.path.join(new_directory, f))])

            file_list = ".. to navigate up\n" + folders_list + ("\n" if folders_list and not_folders_list else "") + not_folders_list

            return CommandResult(
                success=True, 
                message=f"Files in '{new_directory}':\n{file_list}",
                data={
                    "cwd": new_directory,
                    "folders": folders_list,
                    "files": not_folders_list,
                }
            )
        except FileNotFoundError:
            return CommandResult(success=False, message=f"Directory '{new_directory}' not found.")
        except PermissionError:
            return CommandResult(success=False, message=f"Permission denied to access '{new_directory}'.")
        except Exception as e:
            return CommandResult(success=False, message=f"An error occurred: {str(e)}")
    
    def __navigate_up__(self) -> CommandResult:
        with self._lock:
            if self._directory == ROOT:
                return CommandResult(success=False, message="Already at the root directory.")
            
            parent_directory = os.path.dirname(self._directory)
            self._directory = parent_directory

        return CommandResult(
            success=True, 
            message=f"Moved up to directory '{parent_directory}'.",
            data={"cwd": parent_directory}
        )
    
    def __cd__(self, command: Command) -> CommandResult:
        command_text = command.get_args().get("text", "")

        if command_text in [".", ".."]:
            return self.__navigate_up__()
        
        with self._lock:
            base_dir = self._directory
        new_directory = os.path.join(base_dir, command_text)

        if os.path.isdir(new_directory):
            with self._lock:
                self._directory = new_directory
            return CommandResult(success=True, message=f"Changed directory to '{new_directory}'.", data={"cwd": new_directory})
        else:
            return CommandResult(success=False, message=f"'{new_directory}' is not a valid directory.")
        
    def __get_path__(self, command: Command) -> CommandResult:
        file_name = command.get_args().get("text", "")
        with self._lock:
            cwd = self._directory

        if not file_name:
            return CommandResult(True, f"Current directory: '{cwd}'", data={"path": cwd, "cwd": cwd})

        file_path = os.path.join(cwd, file_name)
        if os.path.exists(file_path):
            return CommandResult(True, f"Full path: '{file_path}'", data={"path": file_path, "cwd": cwd})
        return CommandResult(False, f"'{file_name}' does not exist in '{cwd}'.")
    
    def __select_file__(self, command: Command) -> CommandResult:
        file_name = command.get_args().get("text", "")
        if not file_name:
            return CommandResult(False, "Usage: select-file <filename>")

        with self._lock:
            cwd = self._directory
        file_path = os.path.join(cwd, file_name)

        if not os.path.isfile(file_path):
            return CommandResult(False, f"'{file_name}' is not a file in '{cwd}'.")

        return CommandResult(True, f"Selected: {file_name}", data={"path": file_path, "cwd": cwd})

    def __find_song__(self, command: Command) -> CommandResult:
        query = command.get_args().get("text", "").strip().lower()
        
        if not query:
            return CommandResult(False, "Usage: find-song <song-name>")

        # Recolectar todas las canciones mp3 disponibles
        all_songs: dict[str, str] = {}  # {filename_lower: full_path}
        for dirpath, _, filenames in os.walk(ROOT):
            for fn in filenames:
                if fn.lower().endswith(".mp3"):
                    # Usar el nombre sin extensión para búsqueda
                    song_name = os.path.splitext(fn)[0].lower()
                    full_path = os.path.join(dirpath, fn)
                    all_songs[song_name] = full_path

        if not all_songs:
            return CommandResult(False, f"No mp3 files found under '{ROOT}'.")

        # Buscar canciones similares usando difflib (como en weather adapter)
        # get_close_matches devuelve coincidencias ordenadas por similitud
        close_matches = get_close_matches(
            query, 
            all_songs.keys(), 
            n=10,  # Retornar hasta 10 matches
            cutoff=0.65  # Umbral de similitud (65% similar es suficiente)
        )

        if not close_matches:
            return CommandResult(
                False, 
                f"No similar songs found for '{query}'. Try with a different name."
            )

        # Usar el mejor match (primero en la lista)
        best_match = close_matches[0]
        best_path = all_songs[best_match]

        return CommandResult(
            True, 
            f"Found: {best_match}.mp3",
            data={
                "path": best_path,
                "song_name": best_match,
                "matches": [all_songs[m] for m in close_matches]  # Top 10 matches ordenados por similitud
            }
        )