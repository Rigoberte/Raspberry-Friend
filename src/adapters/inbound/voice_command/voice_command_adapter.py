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
- jump-to-pos <posición>: Salta a una posición específica en la canción actual.
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

POLÍTICAS DE PROGRAMACIÓN:
Las tareas pueden programarse usando estos formatos en el campo "text" de task_args:
- "-at: HH:MM" → Ejecutar a una hora específica (ej: "-at: 18:00")
- "-at: DD-MM HH:MM" → Ejecutar en fecha y hora específica (ej: "-at: 25-12 09:00")
- "-every: <cantidad><unidad>" → Ejecutar cada intervalo de tiempo:
  * s = segundos (ej: "-every: 30s")
  * m = minutos (ej: "-every: 5m")
  * h = horas (ej: "-every: 2h")
  * d = días (ej: "-every: 1d")
  * w = semanas (ej: "-every: 1w")
  * M = meses (ej: "-every: 1M")
  * y = años (ej: "-every: 1y")
- "-max: <número>" → Limitar número máximo de ejecuciones (ej: "-every: 1h -max: 5")
- "-while: <condición>" → Ejecutar continuamente mientras se cumpla condición (ej: "-every: 30s -while: true")

Ejemplos de programación:
- "Decime la hora a las 6 de la tarde" → {"text": "-at: 18:00"}
- "Decime el clima cada 2 horas" → {"text": "Madrid -every: 2h"}
- "Poneme música cada 30 minutos, máximo 3 veces" → {"text": "canción -every: 30m -max: 3"}

Nota: 
- En el caso que no se especifique política, la tarea se ejecuta inmediatamente, por lo que no es necesario agregar "-at:" o "-every:".

MÚLTIPLES TAREAS Y CONSULTAS:
El usuario puede combinar TAREAS (comandos del robot) y CONSULTAS GENERALES en una misma frase.
Debes analizar cada elemento por separado y devolver un array "items" donde cada elemento puede ser:
- Una TAREA: is_task=true, task_name y task_args poblados, response=null
- Una CONSULTA: is_task=false, task_name=null, task_args=null, response poblado

INSTRUCCIONES:
1. Analiza TODA la frase del usuario identificando tanto TAREAS como CONSULTAS GENERALES
2. Para cada elemento (tarea o consulta), crea un item en el array "items"
3. Cada item se procesa independientemente según su campo "is_task"

PRIORIDAD CLIMA:
- Si el usuario pide clima/tiempo/temperatura/pronóstico/"weather" y menciona o implica una ciudad, SIEMPRE debe ser una TAREA con is_task=true, task_name="weather" y task_args {"text": "<ciudad>"}.

Responde SOLO con un JSON válido sin markdown (no uses ```json):
{{
    "items": [
        {{"is_task": true/false, "task_name": "comando" o null, "task_args": {{"text": "args"}} o null, "response": "texto" o null}}
    ],
    "interpretation": "Brief explanation in English"
}}

Ejemplos:

1. SOLO TAREA:
- Usuario: "Che, por favor poneme la canción 'No tengo ganas' de Pity A"
    Respuesta: {{"items": [{{"is_task": true, "task_name": "play-song", "task_args": {{"text": "No tengo ganas Pity A"}}, "response": null}}], "interpretation": "Wants to play a song"}}

- Usuario: "Decime que hora es a las 18 horas"
    Respuesta: {{"items": [{{"is_task": true, "task_name": "time", "task_args": {{"text": "-at: 18:00"}}, "response": null}}], "interpretation": "Wants to know the time scheduled at 6 PM"}}

2. MÚLTIPLES TAREAS:
- Usuario: "Decime que hora es y cual es el clima"
    Respuesta: {{"items": [{{"is_task": true, "task_name": "time", "task_args": {{"text": ""}}, "response": null}}, {{"is_task": true, "task_name": "weather", "task_args": {{"text": ""}}, "response": null}}], "interpretation": "Wants to know the time and weather"}}

- Usuario: "Cada 30 minutos decime la hora, máximo 5 veces"
    Respuesta: {{"items": [{{"is_task": true, "task_name": "time", "task_args": {{"text": "-every: 30m -max: 5"}}, "response": null}}], "interpretation": "Wants time announcements every 30 minutes, max 5 times"}}

3. SOLO CONSULTA:
- Usuario: "¿Cuántas copas del mundo ganó Argentina?"
    Respuesta: {{"items": [{{"is_task": false, "task_name": null, "task_args": null, "response": "Argentina ganó 3 Copas del Mundo: 1978, 1986 y 2022."}}], "interpretation": "General query about history"}}

- Usuario: "¿A qué hora abre el supermercado?"
    Respuesta: {{"items": [{{"is_task": false, "task_name": null, "task_args": null, "response": "Los horarios varían según la ubicación. Generalmente los supermercados abren de 8am a 9pm."}}], "interpretation": "General query about business hours"}}

4. TAREA + CONSULTA (MIXTO):
- Usuario: "Decime que hora es y ¿cuántas copas del mundo ganó Argentina?"
    Respuesta: {{"items": [{{"is_task": true, "task_name": "time", "task_args": {{"text": ""}}, "response": null}}, {{"is_task": false, "task_name": null, "task_args": null, "response": "Argentina ganó 3 Copas del Mundo: 1978, 1986 y 2022."}}], "interpretation": "Wants to know the time (task) and asks about Argentina's World Cups (general query)"}}

- Usuario: "Poneme música y decime cuál es la capital de Francia"
    Respuesta: {{"items": [{{"is_task": true, "task_name": "play-song", "task_args": {{"text": ""}}, "response": null}}, {{"is_task": false, "task_name": null, "task_args": null, "response": "La capital de Francia es París."}}], "interpretation": "Wants music (task) and asks about France's capital (general query)"}}

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
        
        # Extraer información
        items = data.get("items", [])
        executed_tasks = data.get("executed_tasks", [])
        response_parts = data.get("response_parts", [])
        
        # Construir valores para compatibilidad
        task_name = ", ".join(executed_tasks) if executed_tasks else ""
        is_task = len(executed_tasks) > 0
        response_payload = result.get_message()
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
            
            # Extraer array de items
            items = interpretation_data.get("items", [])
            interpretation_text = interpretation_data.get("interpretation", "")
            
            # Compatibilidad: Si no hay items pero hay campos legacy, crear un item
            if not items:
                is_task = interpretation_data.get("is_task", False)
                task_name = interpretation_data.get("task_name")
                task_args = interpretation_data.get("task_args")
                response_text = interpretation_data.get("response")
                
                if is_task and task_name:
                    items = [{"is_task": True, "task_name": task_name, "task_args": task_args, "response": None}]
                elif response_text:
                    items = [{"is_task": False, "task_name": None, "task_args": None, "response": response_text}]
            
            if not items:
                # No hay items, fallback a respuesta genérica
                items = [{"is_task": False, "task_name": None, "task_args": None, "response": "Lo siento, no entendí tu solicitud."}]
            
            # ===== Procesar cada item individualmente =====
            executed_tasks = []
            errors = []
            response_parts = []
            
            for item in items:
                is_task = item.get("is_task", False)
                
                if is_task:
                    # Es una TAREA
                    task_name = item.get("task_name")
                    task_args = item.get("task_args") or {}
                    
                    if not isinstance(task_args, dict):
                        task_args = {"text": str(task_args)}
                    
                    if task_name and self._assistant_service:
                        task_command = Command(task_name, task_args)
                        try:
                            self._assistant_service.handle_command(task_command)
                            executed_tasks.append(task_name)
                        except Exception as exc:  # noqa: BLE001
                            error_msg = f"Error ejecutando {task_name}: {exc}"
                            errors.append(error_msg)
                else:
                    # Es una CONSULTA
                    response_text = item.get("response")
                    if response_text:
                        response_parts.append(response_text)
            
            # ===== Construir mensaje final =====
            final_parts = []
            
            # Agregar mensaje de tareas ejecutadas
            if executed_tasks:
                if len(executed_tasks) == 1:
                    final_parts.append(f"Tarea agregada: {executed_tasks[0]}")
                else:
                    final_parts.append(f"Tareas agregadas: {', '.join(executed_tasks)}")
            
            # Agregar errores si los hay
            if errors:
                final_parts.append(f"Errores: {'; '.join(errors)}")
            
            # Agregar respuestas a consultas
            final_parts.extend(response_parts)
            
            # Combinar todo
            final_message = ". ".join(final_parts) if final_parts else "Solicitud procesada."
            
            # Reproducir respuesta por voz
            self._speak_response(final_message)
            
            # Determinar éxito: al menos una tarea ejecutada o una respuesta
            success = len(executed_tasks) > 0 or len(response_parts) > 0
            
            return CommandResult(
                success=success,
                message=final_message,
                data={
                    "items": items,
                    "executed_tasks": executed_tasks,
                    "errors": errors,
                    "response_parts": response_parts,
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
