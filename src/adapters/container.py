from src.application.services.skill_registry import SkillRegistry
from src.application.services.task_scheduler import TaskScheduler
from src.application.services.assistant_service import AssistantService
from src.application.services.command_dispatcher import CommandDispatcher
from src.application.services.progress_monitor_service import ProgressMonitorService
from src.application.events.event_bus import NoOpEventBus
from src.application.use_cases.skills.weather_skill import WeatherSkill
from src.application.use_cases.skills.echo_skill import EchoSkill
from src.application.use_cases.skills.time_skill import TimeSkill
from src.application.use_cases.skills.music_player_skill import MusicPlayerSkill
from src.application.use_cases.skills.playback_monitor_skill import PlaybackMonitorSkill
from src.application.use_cases.skills.file_explorer_skill import FileExplorerSkill
from src.application.use_cases.skills.wait_skill import WaitSkill
from src.application.use_cases.skills.calculator_skill import CalculatorSkill
from src.application.use_cases.skills.camera_skill import CameraSkill
from src.application.use_cases.skills.ai_chatbot_skill import AI_ChatbotSkill
from src.application.use_cases.skills.say_skill import SaySkill
from src.application.use_cases.skills.record_audio_skill import RecordAudioSkill
from src.application.use_cases.skills.transcribe_skill import TranscribeSkill
from src.application.events.event_bus import InMemoryEventBus

from src.domain.ports.outbound.event_bus_ports import EventBusPort
from src.domain.ports.outbound.task_executor_ports import TaskExecutorPort

from src.adapters.outbound.weather.real_weather_adapter import RealWeatherPort
from src.adapters.outbound.music_player.pygame_music_player_adapter import PygameMusicPlayerPort
from src.adapters.outbound.task_executor.thread_pool_executor_adapter import ThreadPoolExecutorAdapter
from src.adapters.outbound.camera.opencv_camera_adapter import OpenCVCameraAdapter
from src.adapters.outbound.ai_chatbot.gemini_adapter import GeminiAdapter
from src.adapters.outbound.tts.pyttsx3_tts_adapter import Pyttsx3TTSAdapter
from src.adapters.outbound.microphone.microphone_adapter import MicrophoneAdapter
from src.adapters.outbound.transcription.gemini_transcription_adapter import GeminiTranscriptionAdapter
from src.adapters.outbound.logger.gui_logger_adapter import GUILoggerAdapter
from src.adapters.inbound.gui.gui_adapter import GUIAdapter
from src.adapters.inbound.voice_command import VoiceCommandAdapter


BRANCH = "develop" # TODO: Detect dynamically based on environment

if BRANCH == "develop":
    from src.configs.configs_dev import Configs
else:
    from src.configs.configs import Configs

def build_assistant(
    event_bus: EventBusPort,
    executor: TaskExecutorPort
) -> tuple[AssistantService, OpenCVCameraAdapter, VoiceCommandAdapter, MicrophoneAdapter]:
    """
    Construye e inyecta todas las dependencias del AssistantService.
    
    Args:
        event_bus: Implementación del EventBus (por defecto NoOpEventBus)
        executor: Implementación del TaskExecutor (por defecto ThreadPoolExecutorAdapter)

    Returns:
        Tupla (AssistantService, ProgressMonitorService, OpenCVCameraAdapter)
    """
    music_player = PygameMusicPlayerPort(event_bus=event_bus)
    camera = OpenCVCameraAdapter()
    gemini_adapter = GeminiAdapter(api_key=Configs.GEMINI_API_KEY.value)
    tts_adapter = Pyttsx3TTSAdapter(rate=150, volume=0.9)
    mic_adapter = MicrophoneAdapter(output_dir="user_data/media")
    stt_adapter = GeminiTranscriptionAdapter()
    
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
    registry.register(AI_ChatbotSkill(gemini_service=gemini_adapter))
    registry.register(SaySkill(tts_service=tts_adapter))
    registry.register(RecordAudioSkill(mic_service=mic_adapter))
    registry.register(TranscribeSkill(stt_service=stt_adapter))

    dispatcher = CommandDispatcher(registry)
    
    scheduler = TaskScheduler(
        dispatcher=dispatcher,
        event_bus=event_bus,
        executor=executor
    )
    
    assistant_service = AssistantService(registry, scheduler)
    
    # Inbound Adapter: Voice Command (comandos por voz)
    voice_command_adapter = VoiceCommandAdapter(
        assistant_service=assistant_service,
        ai_service=gemini_adapter,
        tts_service=tts_adapter
    )
    
    # Inicializar monitor de progreso si el bus está activo
    progress_monitor = None
    if not isinstance(event_bus, NoOpEventBus):
        progress_monitor = ProgressMonitorService(scheduler, event_bus)
    
    return assistant_service, camera, voice_command_adapter, mic_adapter


def build_gui_adapter(
        max_workers: int,
        title: str,
        width: int,
        height: int
    ) -> GUIAdapter:
    """
    Construye el adaptador GUI con todas las dependencias.
    
    Args:
        max_workers: Número de workers para el executor
        title: Título de la ventana GUI
        width: Ancho de la ventana
        height: Alto de la ventana
    
    Returns:
        GUIAdapter configurado y listo para usar
    """
    event_bus = InMemoryEventBus()
    executor = ThreadPoolExecutorAdapter(max_workers=max_workers)

    assistant_service, camera, voice_command_adapter, mic_adapter = build_assistant(
        event_bus=event_bus,
        executor=executor
    )

    gui_adapter = GUIAdapter(
        assistant_service=assistant_service,
        event_bus=event_bus,
        title=title,
        width=width,
        height=height
    )
    
    camera.set_frame_callback(gui_adapter.display_camera_frame)
    camera.set_clear_callback(gui_adapter.clear_camera_display)
    
    gui_adapter.set_voice_command_adapter(voice_command_adapter, mic_adapter)
    
    return gui_adapter