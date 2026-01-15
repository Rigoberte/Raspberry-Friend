from src.application.services.skill_registry import SkillRegistry
from src.application.services.task_scheduler import TaskScheduler
from src.application.services.assistant_service import AssistantService
from src.application.services.command_dispatcher import CommandDispatcher
from src.application.services.progress_monitor_service import ProgressMonitorService
from src.application.events.event_bus import NoOpEventBus

from src.domain.ports.outbound.event_bus_ports import EventBusPort
from src.domain.ports.outbound.task_executor_ports import TaskExecutorPort

from src.adapters.outbound.weather.real_weather_adapter import RealWeatherPort
from src.adapters.outbound.music_player.pygame_music_player_adapter import PygameMusicPlayerPort
from src.adapters.outbound.task_executor.thread_pool_executor_adapter import ThreadPoolExecutorAdapter
from src.adapters.outbound.camera.opencv_camera_adapter import OpenCVCameraAdapter
from src.adapters.inbound.gui.gui_adapter import GUIAdapter

from src.application.use_cases.skills.weather_skill import WeatherSkill
from src.application.use_cases.skills.echo_skill import EchoSkill
from src.application.use_cases.skills.time_skill import TimeSkill
from src.application.use_cases.skills.music_player_skill import MusicPlayerSkill
from src.application.use_cases.skills.playback_monitor_skill import PlaybackMonitorSkill
from src.application.use_cases.skills.file_explorer_skill import FileExplorerSkill
from src.application.use_cases.skills.wait_skill import WaitSkill
from src.application.use_cases.skills.calculator_skill import CalculatorSkill
from src.application.use_cases.skills.camera_skill import CameraSkill

def build_assistant(
    event_bus: EventBusPort = None,
    executor: TaskExecutorPort = None,
    max_workers: int = 4
) -> tuple[AssistantService, ProgressMonitorService | None]:
    """
    Construye e inyecta todas las dependencias del AssistantService.
    
    Args:
        event_bus: Implementación del EventBus (por defecto NoOpEventBus)
        executor: Implementación del TaskExecutor (por defecto ThreadPoolExecutorAdapter)
        max_workers: Número de workers para el executor si no se proporciona uno
    
    Returns:
        Tupla (AssistantService, ProgressMonitorService)
    """
    if event_bus is None:
        event_bus = NoOpEventBus()
    
    if executor is None:
        executor = ThreadPoolExecutorAdapter(max_workers=max_workers)
    
    music_player = PygameMusicPlayerPort(event_bus=event_bus)
    camera = OpenCVCameraAdapter()
    
    registry = SkillRegistry()
    registry.register(EchoSkill())
    registry.register(TimeSkill())
    registry.register(WeatherSkill(service=RealWeatherPort()))
    registry.register(MusicPlayerSkill(service=music_player))
    registry.register(PlaybackMonitorSkill(player=music_player, event_bus=event_bus))
    registry.register(FileExplorerSkill())
    registry.register(WaitSkill())
    registry.register(CalculatorSkill())
    registry.register(CameraSkill(camera_service=camera))

    dispatcher = CommandDispatcher(registry)
    
    scheduler = TaskScheduler(
        dispatcher=dispatcher,
        event_bus=event_bus,
        executor=executor
    )
    
    # Inicializar monitor de progreso si el bus está activo
    progress_monitor = None
    if not isinstance(event_bus, NoOpEventBus):
        progress_monitor = ProgressMonitorService(scheduler, event_bus)
    
    return AssistantService(registry, scheduler), progress_monitor


def build_gui_adapter(
    event_bus: EventBusPort = None,
    executor: TaskExecutorPort = None,
    max_workers: int = 4,
    title: str = "Raspberry Friend",
    width: int = 800,
    height: int = 600,
) -> GUIAdapter:
    """
    Construye el adaptador GUI con todas las dependencias.
    
    Args:
        event_bus: Implementación del EventBus
        executor: Implementación del TaskExecutor
        max_workers: Número de workers para el executor
        title: Título de la ventana GUI
        width: Ancho de la ventana
        height: Alto de la ventana
    
    Returns:
        GUIAdapter configurado y listo para usar
    """
    if event_bus is None:
        event_bus = NoOpEventBus()
    
    if executor is None:
        executor = ThreadPoolExecutorAdapter(max_workers=max_workers)
    
    # Crear adaptador de música
    music_player = PygameMusicPlayerPort(event_bus=event_bus)
    
    # Crear adaptador de cámara
    camera = OpenCVCameraAdapter()
    
    # Crear registry de skills
    registry = SkillRegistry()
    registry.register(EchoSkill())
    registry.register(TimeSkill())
    registry.register(WeatherSkill(service=RealWeatherPort()))
    registry.register(MusicPlayerSkill(service=music_player))
    registry.register(PlaybackMonitorSkill(player=music_player, event_bus=event_bus))
    registry.register(FileExplorerSkill())
    registry.register(WaitSkill())
    registry.register(CalculatorSkill())
    registry.register(CameraSkill(camera_service=camera))

    # Crear dispatcher y scheduler
    dispatcher = CommandDispatcher(registry)
    scheduler = TaskScheduler(
        dispatcher=dispatcher,
        event_bus=event_bus,
        executor=executor
    )
    
    # Crear servicio asistente
    assistant_service = AssistantService(registry, scheduler)
    
    # Crear adaptador GUI
    gui_adapter = GUIAdapter(
        assistant_service=assistant_service,
        event_bus=event_bus,
        title=title,
        width=width,
        height=height,
    )
    
    # Conectar la cámara al GUI para que envíe frames y limpie al detener
    camera.set_frame_callback(gui_adapter.display_camera_frame)
    camera.set_clear_callback(gui_adapter.clear_camera_display)
    
    return gui_adapter