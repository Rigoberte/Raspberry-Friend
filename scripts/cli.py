import sys
import pathlib

# Añadir la carpeta raíz del proyecto al path
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from src.raspberry_friend.model.robot import Robot
from src.raspberry_friend.model.skills.echo_skill import EchoSkill
from src.raspberry_friend.model.skills.time_skill import TimeSkill
from src.raspberry_friend.model.skills.weather_skill import WeatherSkill
from src.raspberry_friend.services.real_weather_service import RealWeatherService  # placeholder for now
from src.raspberry_friend.model.command import Command

def main():
    robot = Robot()
    # Register all skills
    robot.register(EchoSkill())
    robot.register(TimeSkill())
    robot.register(WeatherSkill(service=RealWeatherService()))

    print("Welcome to Raspberry-Friend CLI! Type 'exit' to quit.")

    while True:
        user_input = input("> ")
        if user_input.lower() in ("exit", "quit"):
            break

        # Generic parser: first word is command, rest are args
        parts = user_input.strip().split(maxsplit=1)
        name = parts[0]
        args = {}
        if len(parts) > 1:
            args["text"] = parts[1]  # default key for now

        command = Command(name=name, args=args)
        result = robot.dispatch(command)
        print(result.message)

if __name__ == "__main__":
    main()
