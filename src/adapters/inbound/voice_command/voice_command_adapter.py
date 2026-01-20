import json
import re
import os
from typing import Optional
from pathlib import Path
from google.genai import types as genai_types

from src.domain.models.command import Command
from src.domain.models.command import CommandResult
from src.application.services.assistant_service import AssistantService
from src.domain.ports.outbound.ai_chatbot_ports import AI_ChatBotPort
from src.domain.ports.outbound.tts_ports import TTSPort

INTERPRETATION_PROMPT = """
Eres un asistente inteligente de un robot llamado Raspberry Friend.
El usuario adjunta un archivo de audio con su solicitud.

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
- weather [city-name]: Dice el clima, temperatura, etc. en una ciudad 
- calculator <expresión>: Calcula una expresión
- gemini <prompt>: Pregunta a Gemini
- list-tasks: Lista tareas activas
- file-explorer <ruta>: Explora archivos

INSTRUCCIONES:
1. Analiza si la frase del usuario es una SOLICITUD DE TAREA (comando) o una CONSULTA GENERAL
2. Si es TAREA: Devuelve is_task=true con el comando correspondiente
3. Si es CONSULTA GENERAL: Devuelve is_task=false Y proporciona la respuesta directamente

PRIORIDAD CLIMA:
- Si el usuario pide clima/tiempo/temperatura/pronóstico/"weather" y menciona o implica una ciudad, SIEMPRE debe devolver is_task=true con task_name="weather" y task_args {"text": "<ciudad>"}. Nunca respondas directo en "response" para estas consultas; usa el comando weather.

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

IMPORTANTE: Responde SOLO con el JSON, sin explicaciones adicionales. Y siempre las respuestas deben estar en ESPAÑOL.
""".strip()

class VoiceCommandAdapter:
    """
    Adaptador de entrada para comandos por voz.
    
    Flujo:
    1. Graba audio del micrófono
    2. Transcribe el audio
    3. Envía el texto a la skill interpret-and-respond (centraliza Gemini)
    4. Esa skill decide si es tarea del sistema o consulta general y responde
    """

    def __init__(
            self,
            assistant_service: AssistantService,
            ai_service: AI_ChatBotPort,
            tts_service: TTSPort
        ) -> None:
        """
        Inicializa el adaptador de comandos por voz.
        
        Args:
            mic_service: Servicio de micrófono para grabar audio
            command_dispatcher: Dispatcher que invoca las skills registradas
            ai_service: Servicio AI para procesamiento de lenguaje
            tts_service: Servicio TTS para respuestas habladas
            default_record_seconds: Segundos por defecto a grabar
        """
        self._assistant_service: AssistantService = assistant_service
        self._ai: AI_ChatBotPort = ai_service
        self._tts: TTSPort = tts_service

    def interpret_voice_command(self, audio_path: str) -> dict[str, str | bool]:
        """Envía el texto a la skill interpret-and-respond-audio para evitar duplicar lógica."""
        try:
            result = self._handle(audio_path)
        except Exception as exc:  # noqa: BLE001
            return {
                "success": False,
                "message": f"❌ Error interpretando: {exc}",
                "transcript": "",
                "is_task": False
            }

        data = result.get_data() or {}
        is_task = bool(data.get("is_task", False))
        task_name = data.get("task_name", "")
        response_payload = data.get("task_result") or data.get("response") or result.get_message()
        interpretation_text = data.get("interpretation")
        transcript = data.get("transcript", "")

        os.remove(audio_path)
        
        return {
            "success": result.is_successful(),
            "message": result.get_message(),
            "transcript": transcript,
            "is_task": is_task,
            "task_name": task_name,
            "response": response_payload,
            "interpretation": interpretation_text
        }

    def _handle(self, audio_path: str) -> CommandResult:
        """
        Maneja el comando 'interpret-and-respond'.
        
        Árbol de decisión:
        1. Recibe archivo de audio .wav
        2. Envía el audio a Gemini para que lo interprete (transcribe + analiza)
        3. Si es tarea → ejecuta el comando
        4. Si es consulta → devuelve la respuesta
        5. Reproduce la respuesta por voz
        """
        try:
            if not audio_path:
                return CommandResult(success=False, message="❌ No se proporcionó ruta de audio")
            
            path = Path(audio_path or "").expanduser()
            if not path.exists() or not path.is_file():
                return CommandResult(success=False, message=f"❌ No se encontró el archivo: {path}")

            # Leer archivo de audio
            audio_bytes = path.read_bytes()
            audio_part = genai_types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
            
            # ===== Interpretar con Gemini (audio + prompt) =====
            interpretation_result = self._interpret_audio_with_gemini(audio_part)
            
            if not interpretation_result.get("success", False):
                return CommandResult(
                    success=False,
                    message=f"❌ Error con Gemini: {interpretation_result.get('message', 'Error desconocido')}"
                )
            
            # Parsear respuesta JSON
            raw_response = interpretation_result.get("message", "").strip()
            interpretation_data = self._parse_interpretation(raw_response)
            
            if not interpretation_data:
                return CommandResult(
                    success=False,
                    message=f"❌ No se pudo parsear la respuesta de Gemini",
                    data={"raw_response": raw_response}
                )
            
            is_task = interpretation_data.get("is_task", False)
            task_name = interpretation_data.get("task_name")
            task_args = interpretation_data.get("task_args") or {}
            if not isinstance(task_args, dict):
                # Normalizar task_args a dict para evitar errores aguas abajo
                task_args = {"text": str(task_args)}
            response_text = interpretation_data.get("response")
            interpretation_text = interpretation_data.get("interpretation", "")
            
            # ===== Árbol de decisión =====
            if is_task and task_name and self._assistant_service:
                # Es una tarea: ejecutar
                task_command = Command(task_name, task_args)
                try:
                    self._assistant_service.handle_command(task_command)
                except Exception as exc:  # noqa: BLE001
                    error_response = f"Error ejecutando tarea {task_name}: {exc}"
                    self._speak_response(error_response)
                    return CommandResult(
                        success=False,
                        message=f"❌ {error_response}",
                        data={
                            "is_task": True,
                            "task_name": task_name,
                            "task_args": task_args,
                            "interpretation": interpretation_text,
                        }
                    )
                
                message = f"Tarea agregada: {task_name}"
                self._speak_response(message)

                return CommandResult(
                    success=True,
                    message=message,
                    data={
                        "is_task": True,
                        "task_name": task_name,
                        "task_args": task_args,
                        "task_result": f"La tarea '{task_name}' ha sido agregada para su ejecución.",
                        "interpretation": interpretation_text,
                    }
                )
            else:
                # Es una consulta: responder directamente
                if not response_text:
                    response_text = "Lo siento, no pude obtener una respuesta en este momento."
                
                # Reproducir respuesta por voz
                self._speak_response(response_text)
                
                return CommandResult(
                    success=True,
                    message=f"💬 {response_text}",
                    data={
                        "is_task": False,
                        "response": response_text,
                        "interpretation": interpretation_text,
                    }
                )
        except Exception as exc:  # noqa: BLE001
            # Captura cualquier error inesperado para no romper el flujo de voz
            return CommandResult(
                success=False,
                message=f"❌ Error interpretando: {exc}",
                data={
                    "raw_response": locals().get("raw_response"),
                }
            )
        
    def _interpret_audio_with_gemini(self, audio_part: object) -> dict[str, str | bool]:
        """
        Envía el audio y el prompt a Gemini para interpretación.
        
        Usa generate_text() que soporta:
        - str (solo prompt)
        - list de Parts (solo audio/imágenes)
        - list mixta [str, Part, Part, ...] (prompt + contenido multimodal)
        
        Args:
            audio_part: Parte de audio (genai_types.Part)
            
        Returns:
            Dict con success, message (respuesta JSON de Gemini)
        """
        try:
            result = self._ai.generate_text([INTERPRETATION_PROMPT, audio_part])
            return result
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "message": f"Error llamando a Gemini con audio: {exc}"}

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
