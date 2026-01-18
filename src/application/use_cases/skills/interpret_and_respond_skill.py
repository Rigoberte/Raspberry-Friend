"""
Skill auxiliar: Interpreta con Gemini y responde (árbol de decisión).

Esta skill encapsula la lógica de:
1. Llamar a Gemini para interpretar la transcripción
2. Parsear la respuesta JSON (is_task, task_name, response, etc)
3. Decidir si es una tarea o una consulta general
4. Si es tarea: ejecutar el comando con el dispatcher
5. Si es consulta: reproducir la respuesta por voz
"""

import json
import re
from typing import Optional

from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.ai_chatbot_ports import AI_ChatBotPort
from src.domain.ports.outbound.tts_ports import TTSPort
from src.application.services.command_dispatcher import CommandDispatcher


class InterpretAndRespondSkill(RobotSkill):
    """
    Skill auxiliar que interpreta audio transcrito y responde.
    
    Ejecuta la lógica del árbol de decisión:
    - Interpreta con Gemini si es tarea o consulta
    - Si es tarea: ejecuta el comando
    - Si es consulta: devuelve la respuesta
    """

    # Prompt para Gemini: transcribe, interpreta Y responde en una sola llamada
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

IMPORTANTE: Responde SOLO con el JSON, sin explicaciones adicionales. Y siempre las respuestas deben estar en ESPAÑOL.
""".strip()

    def __init__(
        self,
        ai_service: AI_ChatBotPort,
        tts_service: TTSPort,
        command_dispatcher: CommandDispatcher = None,
    ) -> None:
        """
        Inicializa la skill de interpretación y respuesta.
        
        Args:
            ai_service: Servicio de IA (Gemini)
            tts_service: Servicio de síntesis de voz
            command_dispatcher: Dispatcher para ejecutar comandos (opcional)
        """
        super().__init__({
            "interpret-and-respond": "Interpreta el audio transcrito y responde (ejecuta tarea o devuelve respuesta)."
        })
        self._ai = ai_service
        self._tts = tts_service
        self._dispatcher = command_dispatcher

    def handle(self, command: Command) -> CommandResult:
        """
        Maneja el comando 'interpret-and-respond'.
        
        Árbol de decisión:
        1. Interpreta con Gemini si es tarea o consulta
        2. Si es tarea → ejecuta el comando
        3. Si es consulta → devuelve la respuesta
        4. Reproduce la respuesta por voz
        """
        args = command.get_args() or {}
        transcript = str(args.get("text", "")).strip()
        
        if not transcript:
            return CommandResult(success=False, message="❌ No hay transcripción")
        
        # ===== Interpretar con Gemini =====
        interpretation_prompt = self.INTERPRETATION_PROMPT.format(transcript=transcript)
        interpretation_result = self._ai.generate_text(interpretation_prompt)
        
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
                message=f"❌ No se pudo parsear la respuesta de Gemini"
            )
        
        is_task = interpretation_data.get("is_task", False)
        task_name = interpretation_data.get("task_name")
        task_args = interpretation_data.get("task_args", {})
        response_text = interpretation_data.get("response")
        interpretation_text = interpretation_data.get("interpretation", "")
        
        # ===== Árbol de decisión =====
        if is_task and task_name and self._dispatcher:
            # Es una tarea: ejecutar
            task_command = Command(task_name, task_args)
            task_result = self._dispatcher.handle(task_command)
            
            if task_result.is_successful():
                task_response = task_result.get_message()
                # Reproducir respuesta por voz
                self._speak_response(task_response)
                
                return CommandResult(
                    success=True,
                    message=f"✅ Tarea ejecutada: {task_name}\n💬 Respuesta: {task_response}",
                    data={
                        "transcript": transcript,
                        "is_task": True,
                        "task_name": task_name,
                        "task_result": task_response,
                        "interpretation": interpretation_text,
                    }
                )
            else:
                error_response = f"Error en la tarea: {task_result.get_message()}"
                self._speak_response(error_response)
                
                return CommandResult(
                    success=False,
                    message=f"❌ Error ejecutando tarea {task_name}: {task_result.get_message()}",
                    data={
                        "transcript": transcript,
                        "is_task": True,
                        "task_name": task_name,
                        "interpretation": interpretation_text,
                    }
                )
        else:
            # Es una consulta: responder con Gemini
            if not response_text:
                response_text = "Lo siento, no pude obtener una respuesta en este momento."
            
            # Reproducir respuesta por voz
            self._speak_response(response_text)
            
            return CommandResult(
                success=True,
                message=f"💬 {response_text}",
                data={
                    "transcript": transcript,
                    "is_task": False,
                    "response": response_text,
                    "interpretation": interpretation_text,
                }
            )

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
