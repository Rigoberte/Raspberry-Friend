"""
Workflow: Escucha, interpreta y responde.

Árbol de decisión:
1. Grabar audio
2. Transcribir
3. Interpretar con Gemini (UNA SOLA LLAMADA)
   ├─ Si is_task=true
   │  └─ Ejecutar comando (dispatcher)
   └─ Si is_task=false
      └─ Reproducir respuesta por voz

Nota: Este workflow requiere una skill auxiliar "interpret-and-respond" que 
ejecuta la lógica de interpretación de Gemini con el árbol de decisión.
"""

from src.domain.models.command import Command
from src.domain.models.workflows.workflow_step import WorkflowStep
from src.domain.models.workflows.workflow_task import WorkflowTask


def build_listen_and_interpret_workflow(command: Command) -> WorkflowTask:
    """
    Construye el workflow de escucha e interpretación.
    
    Flujo:
    1. record-audio: Graba audio del micrófono
    2. transcribe: Transcribe el audio grabado
    3. interpret-and-respond: Interpreta con Gemini, decide si es tarea o consulta,
                               ejecuta o responde, y reproduce por voz
    
    Args:
        command: Comando con argumentos (ej: {"text": "10"} para 10 segundos)
    
    Returns:
        WorkflowTask con los pasos configurados
    """
    args = command.get_args() or {}
    duration_text = str(args.get("text", "")).strip() or "10.0"
    
    steps = [
        # PASO 1: Grabar audio
        WorkflowStep(
            name="record-audio",
            command=lambda ctx: Command("record-audio", {"text": duration_text}),
            on_success=lambda ctx, res: ctx.update({
                "audio_path": res.get_data().get("path") if res.get_data() else None
            })
        ),
        
        # PASO 2: Transcribir audio
        WorkflowStep(
            name="transcribe",
            command=lambda ctx: Command("transcribe", {"text": ctx.get("audio_path", "")}),
            on_success=lambda ctx, res: ctx.update({
                "transcript": res.get_message()
            })
        ),
        
        # PASO 3: Árbol de decisión - Interpretar y responder
        # Esta skill encapsula la lógica de:
        # - Interpretar con Gemini
        # - Decidir si es tarea o consulta
        # - Ejecutar o responder
        # - Reproducir respuesta por voz
        WorkflowStep(
            name="interpret-and-respond",
            command=lambda ctx: Command("interpret-and-respond", {
                "text": ctx.get("transcript", "")
            }),
            on_success=lambda ctx, res: ctx.update({
                "is_task": res.get_data().get("is_task") if res.get_data() else False,
                "task_name": res.get_data().get("task_name") if res.get_data() else None,
                "response": res.get_message()
            })
        ),
    ]
    
    return WorkflowTask(
        steps,
        initial_context={
            "duration": duration_text,
            "audio_path": None,
            "transcript": None,
            "is_task": False,
            "task_name": None,
            "response": None,
        }
    )
