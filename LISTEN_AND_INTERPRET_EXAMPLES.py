"""
Ejemplos de uso del workflow 'listen-and-interpret'

Este archivo muestra diferentes formas de usar el nuevo workflow
que permite interactuar con el robot hablando naturalmente.

NOTA: Se refactorizó de skill monolítico a workflow + skill auxiliar
para mejor composición y reutilización.
"""

# ============================================================================
# EJEMPLO 1: Usar desde la GUI
# ============================================================================
"""
En la interfaz gráfica de Raspberry Friend, simplemente escribe:

    listen-to-me

Y el sistema:
1. Escuchará durante 10 segundos (default)
2. Transcribirá lo que dijiste
3. Interpretará si es una tarea o consulta
4. Ejecutará la tarea O responderá tu pregunta
5. Reproducirá la respuesta por voz

Ejemplos de entrada natural:
"""

# Caso 1: Música
entrada_1 = "Che, por favor ponme la canción 'No tengo ganas' de Pity A"
# → Sistema detecta: play-song
# → Ejecuta: play-song No tengo ganas Pity A
# → Responde por voz: "Reproduciendo No tengo ganas..."

# Caso 2: Pregunta General
entrada_2 = "¿Cuántas copas del mundo ganó Argentina?"
# → Sistema detecta: NOT task
# → Consulta a Gemini
# → Responde por voz: "Argentina ganó 3 Copas del Mundo: 1978, 1986 y 2022"

# Caso 3: Comando Simple
entrada_3 = "Silencia la música"
# → Sistema detecta: stop-song
# → Ejecuta: stop-song
# → Responde por voz: "Música detenida"

# Caso 4: Información
entrada_4 = "¿Qué hora es?"
# → Sistema detecta: time
# → Ejecuta: time
# → Responde por voz: "Son las 14:30"

# Caso 5: Cámara
entrada_5 = "Enciende la cámara"
# → Sistema detecta: camera-on
# → Ejecuta: camera-on
# → Responde por voz: "Cámara activada"

# Caso 6: Control de Reproducción
entrada_6 = "Siguiente canción, por favor"
# → Sistema detecta: next-song
# → Ejecuta: next-song
# → Responde por voz: "Reproduciendo siguiente..."

# ============================================================================
# EJEMPLO 2: Usar desde Python directamente
# ============================================================================

from src.adapters.container import build_assistant
from src.domain.models.command import Command
from src.application.events.event_bus import InMemoryEventBus

# Construir el asistente con event bus activo
event_bus = InMemoryEventBus()
assistant, _, _ = build_assistant(event_bus=event_bus)

# Crear comando listen-to-me con duración personalizada (15 segundos)
listen_command = Command("listen-to-me", {"text": "15"})

# Ejecutar el skill
result = assistant.dispatcher.handle(listen_command)

# Procesar resultado
if result.success:
    print(f"✅ {result.message}")
    # El resultado contiene:
    # - transcript: Lo que se transcribió
    # - is_task: Si fue una tarea
    # - task_name: Nombre de la tarea (si aplica)
    # - task_result: Resultado de ejecutar (si aplica)
    # - gemini_response: Respuesta de Gemini (si no era tarea)
else:
    print(f"❌ {result.message}")

# ============================================================================
# EJEMPLO 3: Usando el Workflow (Recomendado)
# ============================================================================

from src.application.use_cases.workflows.listen_and_interpret_workflow import build_listen_and_interpret_workflow
from src.adapters.container import build_assistant
from src.application.events.event_bus import NoOpEventBus
from src.domain.models.command import Command

# Construir el asistente
event_bus = NoOpEventBus()
assistant, _, _ = build_assistant(event_bus=event_bus)

# Crear el workflow
command = Command("listen-to-me", {"text": "10"})  # 10 segundos de grabación
workflow = build_listen_and_interpret_workflow(command)

# Agregar al scheduler
assistant.scheduler.add_task(workflow)

# El workflow se ejecuta automáticamente en el scheduler

# ============================================================================
# EJEMPLO 4: Acceso Manual a Skills (Bajo nivel)
# ============================================================================

from src.adapters.outbound.microphone.sounddevice_microphone_adapter import SoundDeviceMicrophoneAdapter
from src.adapters.outbound.transcription.gemini_transcription_adapter import GeminiTranscriptionAdapter
from src.adapters.outbound.ai_chatbot.gemini_adapter import GeminiAdapter
from src.adapters.outbound.tts.pyttsx3_tts_adapter import Pyttsx3TTSAdapter
from src.application.use_cases.skills.interpret_and_respond_skill import InterpretAndRespondSkill
from src.configs.configs_dev import Configs

# Inicializar adapters
mic = SoundDeviceMicrophoneAdapter(output_dir="user_data/media")
transcription = GeminiTranscriptionAdapter(api_key=Configs.GEMINI_API_KEY.value)
gemini = GeminiAdapter(api_key=Configs.GEMINI_API_KEY.value)
tts = Pyttsx3TTSAdapter()

# Construir el asistente para tener el dispatcher
assistant, _, _ = build_assistant(event_bus=event_bus)

# Crear la skill auxiliar de interpretación
interpret_skill = InterpretAndRespondSkill(
    ai_service=gemini,
    tts_service=tts,
    command_dispatcher=assistant.dispatcher
)

# Usar directamente (paso a paso manual)
# 1. Grabar
record_result = mic.record(10)

# 2. Transcribir
transcribe_cmd = Command("transcribe", {"text": record_result.get("path")})
transcribe_result = assistant.dispatcher.handle(transcribe_cmd)

# 3. Interpretar y responder
transcript = transcribe_result.get_message()
interpret_cmd = Command("interpret-and-respond", {"text": transcript})
result = interpret_skill.handle(interpret_cmd)

print(result.message)

# ============================================================================
# EJEMPLO 4: Procesar respuesta con datos completos
# ============================================================================

result = listen_skill.handle(Command("listen-to-me", {}))

if result.success:
    data = result.data  # Acceder a los datos adicionales
    
    # Para tareas ejecutadas:
    if data.get("is_task"):
        print(f"📝 Transcripción: {data.get('transcript')}")
        print(f"🎯 Tarea: {data.get('task_name')}")
        print(f"✅ Resultado: {data.get('task_result')}")
    
    # Para consultas generales:
    else:
        print(f"📝 Transcripción: {data.get('transcript')}")
        print(f"🤖 Respuesta de Gemini: {data.get('gemini_response')}")
    
    print(f"💭 Interpretación: {data.get('interpretation')}")

# ============================================================================
# EJEMPLO 5: Casos de Uso Avanzados
# ============================================================================

# Caso: Usuario dice algo ambiguo
caso_1 = "Toca una canción"
# ¿Cuál canción? El sistema tratará de interpretarlo como play-song
# y Gemini buscará parámetros razonables

# Caso: Usuario usa variaciones de lenguaje
caso_2 = "Ponle pausa a la música, boludo"
# Gemini entiende coloquialismos y localiza a "pause-song"

# Caso: Usuario pide varias cosas
caso_3 = "Enciende la cámara y ponme música"
# El sistema probablemente interpretará como:
# 1. camera-on
# 2. play-song
# (Puede ejecutar ambas o la primera, dependiendo de la implementación)

# Caso: Pregunta sobre el robot mismo
caso_4 = "¿Cuáles son tus capacidades?"
# → Sistema detecta: NOT task
# → Consulta a Gemini
# → Gemini responde listando las capacidades

# Caso: Mezcla de contexto
caso_5 = "Tengo frío, ¿cuál es la temperatura?"
# → Sistema detecta: weather
# → Ejecuta: weather
# → Responde con temperatura actual

# ============================================================================
# EJEMPLO 6: Depuración y Logging
# ============================================================================

# Si quieres ver qué está pasando en detalle:

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

result = listen_skill.handle(Command("listen-to-me", {}))

# Ahora verás logs detallados de cada paso

# ============================================================================
# EJEMPLO 7: Diferencia con Comandos Tradicionales
# ============================================================================

# COMANDO TRADICIONAL:
# El usuario debe escribir:
#   play-song Bohemian Rhapsody
# Es rápido pero requiere formato exacto

# LISTEN-AND-INTERPRET:
# El usuario puede decir:
#   "Ponme Bohemian Rhapsody de Queen"
# O:
#   "Escucha esta: Bohemian Rhapsody"
# O:
#   "Toca la canción de Queen, la famosa"
# El sistema lo interpreta automáticamente

# ============================================================================
# EJEMPLO 8: Optimización para Raspberry Pi
# ============================================================================

# Si estás en RPi y quieres reducir duración de grabación:

# Opción 1: Desde GUI
#   listen-to-me 5    (5 segundos en lugar de 10)

# Opción 2: Desde Python
command_short = Command("listen-to-me", {"text": "5"})
result = listen_skill.handle(command_short)

# Esto usa menos CPU y responde más rápido

# ============================================================================
# EJEMPLO 9: Manejo de Errores
# ============================================================================

# Si hay algún error en el flujo:

result = listen_skill.handle(Command("listen-to-me", {}))

if not result.success:
    # El mensaje de error es descriptivo
    error_msg = result.message
    
    if "grabando" in error_msg:
        print("Problema con el micrófono")
    elif "transcribiendo" in error_msg:
        print("Problema de transcripción")
    elif "interpretando" in error_msg:
        print("Problema con Gemini")
    else:
        print(f"Error desconocido: {error_msg}")

# ============================================================================
# EJEMPLO 10: Integración con Workflows Existentes
# ============================================================================

# listen-to-me se integra perfectamente con el sistema existente:

# 1. Como cualquier otro skill:
#    assistant.dispatcher.handle(Command("listen-to-me", {}))

# 2. En tareas programadas:
#    task = OneTimeTask(
#        command=Command("listen-to-me", {"text": "10"}),
#        run_at=datetime.now() + timedelta(seconds=5)
#    )

# 3. En workflows:
#    (Si tienes un workflow que ejecuta skills)

# 4. Combinado con otros skills:
#    # Primero escucha qué hacer
#    listen_result = assistant.dispatcher.handle(Command("listen-to-me", {}))
#    # Luego procesa el resultado
#    if listen_result.success:
#        # Hacer algo con listen_result.data

"""
RESUMEN:

listen-to-me es el puente entre:
  - Entrada natural (lo que dices)
  - Interpretación inteligente (Gemini)
  - Ejecución de tareas (dispatcher)
  - Feedback por voz (TTS)

Es como tener un asistente que entiende contexto y puede ejecutar
comandos sin que tengas que ser preciso en la sintaxis.
"""
