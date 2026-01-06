import sys
import pathlib
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import colorama

from src.model.robot.robot import Robot
from src.model.command.command import Command

from src.model.skills.echo_skill import EchoSkill
from src.model.skills.time_skill import TimeSkill
from src.model.skills.file_explorer_skill import FileExplorerSkill

from src.model.skills.weather_skill import WeatherSkill
from src.services.weather.real_weather_service import RealWeatherService  # placeholder for now

from src.model.skills.music_player_skill import MusicPlayerSkill
from src.services.music_player.pygame_music_player_service import PygameMusicPlayerService

def main():
    robot = Robot()
    # Register all skills
    robot.register(EchoSkill())
    robot.register(TimeSkill())
    robot.register(WeatherSkill(service=RealWeatherService()))
    robot.register(MusicPlayerSkill(service=PygameMusicPlayerService()))
    robot.register(FileExplorerSkill())

    print("Welcome to Raspberry-Friend CLI! Type 'exit' to quit.")

    session = PromptSession()

    while True:
        with patch_stdout():
            user_input = session.prompt("> ")
            user_input = user_input.lower().strip()
        
        if user_input in ("exit", "quit"):
            break

        if not user_input:
            continue

        # Generic parser: first word is command, rest are args
        parts = user_input.split(maxsplit=1)
        name = parts[0]
        args = {}
        if len(parts) > 1:
            args["text"] = parts[1]

        command = Command(name=name, args=args)
        result = robot.dispatch(command)
        print(result.message)

if __name__ == "__main__":
    # Añadir la carpeta raíz del proyecto al path
    sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
    colorama.just_fix_windows_console()
    
    main()