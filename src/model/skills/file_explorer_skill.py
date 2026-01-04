import os

from .skill import RobotSkill
from src.model.command.command import Command, CommandResult

class FileExplorerSkill(RobotSkill):
    """
    Handles 'list_files' commands to list files in a given directory.
    """
    def __init__(self):
        self.directory = "."  # Default directory

    def can_handle(self, command: Command) -> bool:
        return command.get_name() in ["list-files", "..", "cd", "ls", "get-path"]

    def handle(self, command: Command) -> CommandResult:
        match command.get_name():
            case "list-files" | "ls":
                return self.__list_files__(command)
            case "cd":
                return self.__cd__(command)
            case "get-path":
                return self.__get_path__(command)
            case "..":
                return self.__navigate_up__()
    
    def __list_files__(self, command: Command) -> CommandResult:
        command_text = command.get_args().get("text", "")
        if command_text != "":
            new_directory = os.path.join(self.directory, command_text)
        else:
            new_directory = self.directory
        
        try:
            files = os.listdir(new_directory)
            self.directory = new_directory
            
            if not files:
                return CommandResult(success=True, message=f"No files found in directory '{new_directory}'.")
            
            folders_list = "\n".join(["🗀 " + f for f in files if os.path.isdir(os.path.join(new_directory, f))])
            not_folders_list = "\n".join(["🗎 " + f for f in files if not os.path.isdir(os.path.join(new_directory, f))])

            file_list = ".. to navigate up\n" + folders_list + ("\n" if folders_list and not_folders_list else "") + not_folders_list

            return CommandResult(success=True, message=f"Files in '{new_directory}':\n{file_list}")
        except FileNotFoundError:
            return CommandResult(success=False, message=f"Directory '{new_directory}' not found.")
        except PermissionError:
            return CommandResult(success=False, message=f"Permission denied to access '{new_directory}'.")
        except Exception as e:
            return CommandResult(success=False, message=f"An error occurred: {str(e)}")
    
    def __navigate_up__(self) -> CommandResult:
        if self.directory == ".":
            return CommandResult(success=False, message="Already at the root directory.")
        
        parent_directory = os.path.dirname(self.directory)
        self.directory = parent_directory

        return CommandResult(success=True, message=f"Moved up to directory '{parent_directory}'.")
    
    def __cd__(self, command: Command) -> CommandResult:
        command_text = command.get_args().get("text", "")

        if command_text in [".", ".."]:
            return self.__navigate_up__()
        
        new_directory = os.path.join(self.directory, command_text)

        if os.path.isdir(new_directory):
            self.directory = new_directory
            return CommandResult(success=True, message=f"Changed directory to '{new_directory}'.")
        else:
            return CommandResult(success=False, message=f"'{new_directory}' is not a valid directory.")
        
    def __get_path__(self, command: Command) -> CommandResult:
        file_name = command.get_args().get("text", "")

        if file_name:
            file_path = os.path.join(self.directory, file_name)
            
            if os.path.exists(file_path):
                return CommandResult(success=True, message=f"Full path: '{file_path}'")
            else:
                return CommandResult(success=False, message=f"Directory '{file_name}' does not exist in '{self.directory}'.")