from src.application.services.skill_registry import SkillRegistry
from src.application.services.task_scheduler import TaskScheduler
from src.application.services.assistant_service import AssistantService
from src.application.services.command_dispatcher import CommandDispatcher
from src.application.events.event_bus import EventBus, NoOpEventBus

from src.adapters.outbound.weather.real_weather_adapter import RealWeatherPort
from src.adapters.outbound.music_player.pygame_music_player_adapter import PygameMusicPlayerPort

from src.application.use_cases.skills.weather_skill import WeatherSkill
from src.application.use_cases.skills.echo_skill import EchoSkill
from src.application.use_cases.skills.time_skill import TimeSkill
from src.application.use_cases.skills.music_player_skill import MusicPlayerSkill
from src.application.use_cases.skills.file_explorer_skill import FileExplorerSkill
from src.application.use_cases.skills.wait_skill import WaitSkill
from src.application.use_cases.skills.calculator_skill import CalculatorSkill

def build_assistant(event_bus: EventBus = NoOpEventBus()) -> AssistantService:
    registry = SkillRegistry()
    registry.register(EchoSkill())
    registry.register(TimeSkill())
    registry.register(WeatherSkill(service=RealWeatherPort()))
    registry.register(MusicPlayerSkill(service=PygameMusicPlayerPort()))
    registry.register(FileExplorerSkill())
    registry.register(WaitSkill())
    registry.register(CalculatorSkill())

    dispatcher = CommandDispatcher(registry)
    
    scheduler = TaskScheduler(dispatcher=dispatcher, event_bus=event_bus, max_workers=5)
    
    return AssistantService(registry, scheduler)