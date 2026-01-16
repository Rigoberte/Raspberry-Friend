"""
Voice Command Adapter - Adaptador de entrada para comandos por voz.

Este adaptador permite recibir comandos hablados del usuario, transcribirlos,
interpretarlos con IA y ejecutarlos como tareas o workflows.

Arquitectura hexagonal:
- Inbound Adapter: punto de entrada al sistema por voz
- Usa AssistantService para ejecutar comandos (workflows o tasks)
- No tiene acoplamiento con skills internas
"""

import json
import re
from typing import Optional

from src.application.services.assistant_service import AssistantService
from src.domain.models.command import Command
from src.domain.ports.outbound.microphone_ports import MicrophonePort
from src.domain.ports.outbound.transcription_ports import TranscriptionPort
from src.domain.ports.outbound.ai_chatbot_ports import AI_ChatBotPort
from src.domain.ports.outbound.tts_ports import TTSPort


class VoiceCommandAdapter:
    """
    Adaptador de entrada para comandos por voz.
    
    Flujo:
    1. Graba audio del micrófono
    2. Transcribe con Gemini
    3. Interpreta con Gemini (una sola llamada optimizada):
       - Determina si es tarea del sistema o consulta general
       - Si es tarea: devuelve comando a ejecutar
       - Si es consulta: devuelve respuesta directa
    4. Ejecuta tarea/workflow O responde consulta
    5. Reproduce respuesta por voz
    """

    # Prompt optimizado: transcribe, interpreta Y responde en una llamada
    INTERPRETATION_PROMPT = """
Eres un asistente inteligente de un robot llamado Raspberry Friend.
El usuario ha dicho: "{transcript}"

El robot tiene los siguientes comandos disponibles:
- play-song <nombre_cancion>: Reproduce una canción
- stop-song: Detiene la música
- next-song: Siguiente canción
- previous-song: Canción anterior
- pause-song: Pausa la música
- resume-song: Reanuda la música
- record-audio [duracion]: Graba audio
- transcribe <ruta_archivo>: Transcribe un archivo
- wait <segundos>: Espera segundos
- say <texto>: Dice un texto
- turn-on-camera: Enciende la cámara
- turn-off-camera: Apaga la cámara
- track-my-face: Activa seguimiento de rostro
- untrack-my-face: Desactiva seguimiento de rostro
- echo <texto>: Repite texto
- time: Dice la hora
- weather [city-name]: Dice el clima
- calculator <expresión>: Calcula una expresión
- gemini <prompt>: Pregunta a Gemini
- list-tasks: Lista tareas activas
- file-explorer <ruta>: Explora archivos

INSTRUCCIONES:
1. Analiza si la frase del usuario es una SOLICITUD DE TAREA (comando) o una CONSULTA GENERAL
2. Si es TAREA: Devuelve is_task=true con el comando correspondiente
3. Si es CONSULTA GENERAL: Devuelve is_task=false Y proporciona la respuesta directamente

Responde SOLO con un JSON válido sin markdown (no uses ```json):
{{
    "is_task": true/false,
    "task_name": "nombre-del-comando" o null,
    "task_args": {{"text": "argumentos"}} o null,
    "response": "respuesta si es consulta, null si es tarea",
    "interpretation": "Brief explanation in English"
}}

Ejemplos:
- Usuario: "Che, por favor poneme la canción 'No tengo ganas' de Pity A"
  Respuesta: {{"is_task": true, "task_name": "play-song", "task_args": {{"text": "No tengo ganas Pity A"}}, "response": null, "interpretation": "Wants to play a song"}}

- Usuario: "¿Cuántas copas del mundo ganó Argentina?"
  Respuesta: {{"is_task": false, "task_name": null, "task_args": null, "response": "Argentina ganó 3 Copas del Mundo: 1978, 1986 y 2022.", "interpretation": "General query about history"}}

- Usuario: "¿Cuál es el clima en Madrid?"
  Respuesta: {{"is_task": true, "task_name": "weather", "task_args": {{"text": "Madrid"}}, "response": null, "interpretation": "Wants to know the weather in a specific city"}}

- Usuario: "Silencia la música"
  Respuesta: {{"is_task": true, "task_name": "stop-song", "task_args": {{"text": ""}}, "response": null, "interpretation": "Wants to stop the music"}}

- Usuario: "¿A qué hora abre el supermercado?"
  Respuesta: {{"is_task": false, "task_name": null, "task_args": null, "response": "Los horarios varían según la ubicación. Generalmente los supermercados abren de 8am a 9pm.", "interpretation": "General query about business hours"}}

IMPORTANTE: Responde SOLO con el JSON, sin explicaciones adicionales. Y siempre las respuestas deben estar en INGLES.""" .strip()

    def __init__(
        self,
        assistant_service: AssistantService,
        mic_service: MicrophonePort,
        transcription_service: TranscriptionPort,
        ai_service: AI_ChatBotPort,
        tts_service: TTSPort,
        default_record_seconds: float = 10.0,
    ) -> None:
        """
        Inicializa el adaptador de comandos por voz.
        
        Args:
            assistant_service: Servicio del asistente (para ejecutar comandos)
            mic_service: Servicio de micrófono
            transcription_service: Servicio de transcripción
            ai_service: Servicio de IA (Gemini)
            tts_service: Servicio de síntesis de voz
            default_record_seconds: Segundos por defecto a grabar
        """
        self._assistant = assistant_service
        self._mic = mic_service
        self._transcription = transcription_service
        self._ai = ai_service
        self._tts = tts_service
        self._default_record_seconds = default_record_seconds

    def listen_and_execute(self, duration_seconds: Optional[float] = None) -> dict:
        """
        Escucha un comando por voz, lo interpreta y lo ejecuta.
        
        Args:
            duration_seconds: Duración de grabación (None = default)
            
        Returns:
            Dict con el resultado de la operación:
            {
                "success": bool,
                "message": str,
                "transcript": str,
                "is_task": bool,
                "task_name": str (opcional),
                "response": str (opcional)
            }
        """
        # Obtener duración de grabación
        duration = duration_seconds or self._default_record_seconds
        duration = min(max(duration, 1.0), 300.0)  # Entre 1s y 5min
        
        # ===== PASO 1: Grabar audio =====
        record_result = self._mic.record(duration)
        if not record_result.get("success", False):
            error = record_result.get("message", "No se pudo grabar audio")
            return {
                "success": False,
                "message": f"❌ Error grabando: {error}",
                "transcript": None,
                "is_task": False
            }
        
        audio_path = record_result.get("path", "")
        
        # ===== PASO 2: Transcribir audio =====
        transcribe_result = self._transcription.transcribe(audio_path)
        if not transcribe_result.get("success", False):
            error = transcribe_result.get("message", "No se pudo transcribir")
            return {
                "success": False,
                "message": f"❌ Error transcribiendo: {error}",
                "transcript": None,
                "is_task": False
            }
        
        transcript = transcribe_result.get("message", "").strip()
        if not transcript:
            return {
                "success": False,
                "message": "❌ No se pudo entender el audio",
                "transcript": None,
                "is_task": False
            }
        
        # ===== PASO 3: Interpretar con Gemini (una sola llamada) =====
        interpretation_prompt = self.INTERPRETATION_PROMPT.format(transcript=transcript)
        interpretation_result = self._ai.generate_text(interpretation_prompt)
        
        if not interpretation_result.get("success", False):
            return {
                "success": False,
                "message": f"❌ Error con Gemini: {interpretation_result.get('message', 'Error desconocido')}",
                "transcript": transcript,
                "is_task": False
            }
        
        # Parsear respuesta JSON de Gemini
        raw_response = interpretation_result.get("message", "").strip()
        interpretation_data = self._parse_interpretation(raw_response)
        
        if not interpretation_data:
            return {
                "success": False,
                "message": "❌ No se pudo parsear la respuesta de Gemini",
                "transcript": transcript,
                "is_task": False
            }
        
        is_task = interpretation_data.get("is_task", False)
        task_name = interpretation_data.get("task_name")
        task_args = interpretation_data.get("task_args", {})
        response_text = interpretation_data.get("response")
        interpretation_text = interpretation_data.get("interpretation", "")
        
        # ===== PASO 4: Ejecutar tarea O responder consulta =====
        if is_task and task_name:
            # Es una tarea del sistema: ejecutar con AssistantService
            # AssistantService usa CommandToTask que resuelve workflows
            
            # Crear objeto Command
            command = Command(task_name, task_args or {})
            
            try:
                # handle_command no devuelve nada, solo añade la tarea al scheduler
                self._assistant.handle_command(command)
                
                task_response = f"Tarea '{task_name}' programada correctamente"
                # Reproducir respuesta por voz
                self._speak_response(task_response)
                
                return {
                    "success": True,
                    "message": f"✅ Tarea ejecutada: {task_name}\n📝 Transcripción: {transcript}\n💬 Respuesta: {task_response}",
                    "transcript": transcript,
                    "is_task": True,
                    "task_name": task_name,
                    "response": task_response,
                    "interpretation": interpretation_text
                }
            except Exception as e:
                error_response = f"Error ejecutando la tarea '{task_name}': {str(e)}"
                self._speak_response(error_response)
                
                return {
                    "success": False,
                    "message": f"❌ Error ejecutando tarea {task_name}: {str(e)}\n📝 Transcripción: {transcript}",
                    "transcript": transcript,
                    "is_task": True,
                    "task_name": task_name,
                    "interpretation": interpretation_text
                }
        else:
            # Es una consulta general: responder con la respuesta de Gemini
            if not response_text:
                response_text = "Lo siento, no pude obtener una respuesta en este momento."
            
            # Reproducir respuesta por voz
            self._speak_response(response_text)
            
            return {
                "success": True,
                "message": f"💬 Consulta respondida\n📝 Transcripción: {transcript}\n🤖 Respuesta: {response_text}",
                "transcript": transcript,
                "is_task": False,
                "response": response_text,
                "interpretation": interpretation_text
            }

    def _parse_interpretation(self, raw_json: str) -> Optional[dict]:
        """
        Parsea la respuesta JSON de Gemini.
        
        Args:
            raw_json: String con JSON (posiblemente con markdown)
            
        Returns:
            Dict parseado o None si no se puede parsear
        """
        try:
            # Limpiar posible markdown ```json ... ```
            cleaned = re.sub(r'^```json\s*', '', raw_json.strip())
            cleaned = re.sub(r'\s*```$', '', cleaned)
            
            data = json.loads(cleaned)
            return data
        except json.JSONDecodeError:
            # Intentar extraer JSON del string
            try:
                match = re.search(r'\{.*\}', raw_json, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except:
                pass
            
            return None

    def _speak_response(self, text: str) -> None:
        """
        Reproduce la respuesta por voz usando TTS.
        
        Args:
            text: Texto a reproducir
        """
        try:
            # Limitar texto a 500 caracteres para TTS
            if len(text) > 500:
                text = text[:497] + "..."
            
            self._tts.speak(text)
        except Exception as e:
            print(f"Error reproduciendo respuesta: {e}")
