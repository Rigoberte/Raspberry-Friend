from src.application.services.skill_registry import SkillRegistry
from src.application.services.task_scheduler import TaskScheduler
from src.application.services.assistant_service import AssistantService

from src.adapters.outbound.weather.real_weather_adapter import RealWeatherPort
from src.adapters.outbound.music_player.pygame_music_player_adapter import PygameMusicPlayerPort

from src.application.use_cases.skills.weather_skill import WeatherSkill
from src.application.use_cases.skills.echo_skill import EchoSkill
from src.application.use_cases.skills.time_skill import TimeSkill
from src.application.use_cases.skills.music_player_skill import MusicPlayerSkill
from src.application.use_cases.skills.file_explorer_skill import FileExplorerSkill

def build_assistant() -> AssistantService:
    registry = SkillRegistry()
    registry.register(EchoSkill())
    registry.register(TimeSkill())
    registry.register(WeatherSkill(service=RealWeatherPort()))
    registry.register(MusicPlayerSkill(service=PygameMusicPlayerPort()))
    registry.register(FileExplorerSkill())
    
    scheduler = TaskScheduler()
    
    return AssistantService(registry, scheduler)