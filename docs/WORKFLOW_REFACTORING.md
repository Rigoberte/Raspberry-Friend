## Workflows Reales Implementados

### ✅ Workflows Actuales

El proyecto cuenta actualmente con estos workflows:

1. **play-song-workflow**: Reproduce una canción con pasos secuenciales
2. **transcribe-me-workflow**: Graba y transcribe audio en pasos

**Ubicación**: `src/application/use_cases/workflows/`

### ❌ Voice Command NO es un Workflow

El sistema de comandos de voz (`VoiceCommandAdapter`) **NO** es un workflow. Es un **adaptador inbound** que:
- Maneja grabación de audio (press-to-talk)
- Transcribe con Gemini
- Interpreta comandos
- Ejecuta a través del AssistantService
- Reproduce respuestas por TTS

Es comparable a `GUIAdapter` o `CLI` (otro adaptador de entrada).

---

## Arquitectura de Workflow (General)

### 🎯 Cambio de Arquitectura

**Contexto histórico:**
- Anteriormente existía `ListenAndInterpretSkill`: una skill monolítica que hacía todo (grabar, transcribir, interpretar, ejecutar, responder)
- Acoplada fuertemente con CommandDispatcher
- Difícil de reutilizar componentes

**Evolución actual:**
- El sistema de comandos de voz es ahora un **adaptador inbound** (`VoiceCommandAdapter`)
- Los workflows reales (`play-song-workflow`, `transcribe-me-workflow`) son composiciones de skills
- Componentes desacoplados y reutilizables

---

### Ejemplo: play-song-workflow

```
play-song-workflow
├── Paso 1: Cargar canción
│   └─ Busca archivo de audio
│
└── Paso 2: Reproducir
    └─ Inicia playback con MusicPlayerSkill
```

### Ejemplo: transcribe-me-workflow

```
transcribe-me-workflow
├── Paso 1: record-audio
│   └─ Graba audio del micrófono
│
└── Paso 2: transcribe  
    └─ Transcribe el audio grabado con Gemini
```

---

### 🔄 Flujo de Decisión en Workflows

Los workflows pueden contener lógica condicional en sus pasos, donde cada `WorkflowStep` puede decidir:

- Qué comando ejecutar basado en el contexto
- Cómo manejar el resultado del paso anterior
- Si continuar o abortar el workflow

**Ejemplo de paso condicional:**
```python
WorkflowStep(
    name="conditional_step",
    command=lambda ctx: (
        Command("play-song", ctx.get("song_name"))
        if ctx.get("has_song")
        else Command("echo", {"text": "No hay canción"})
    ),
    on_success=lambda ctx, result: ctx.update({"played": True})
)
```

---

### 💡 Ventajas del Nuevo Enfoque

1. **Separación de responsabilidades:**
   - Workflow: Orquestación de pasos
   - Skill auxiliar: Lógica de decisión
   
2. **Reutilización:**
   - `record-audio` puede usarse en otros workflows
   - `transcribe` puede usarse independientemente
   - Skills individuales se pueden componer en nuevos workflows

3. **Composición:**
   - Fácil agregar nuevos pasos al workflow
   - Fácil crear variaciones (ej: workflow sin TTS)

4. **Testing:**
   - Cada componente es testeable independientemente

5. **Escalabilidad:**
   - Agregar skills de música sin conflictos
   - Crear workflows complejos combinando pasos

---

### 🚀 Cómo Crear un Workflow

Los workflows se crean mediante funciones builder:

```python
# src/application/use_cases/workflows/mi_workflow.py
from src.domain.models.command import Command
from src.domain.models.workflows.workflow_task import WorkflowTask
from src.domain.models.workflows.workflow_step import WorkflowStep

def build_mi_workflow(command: Command) -> WorkflowTask:
    """Construye un workflow personalizado"""
    
    steps = [
        WorkflowStep(
            name="paso1",
            command=lambda ctx: Command("echo", {"text": "Iniciando"}),
            on_success=lambda ctx, result: ctx.update({"started": True})
        ),
        WorkflowStep(
            name="paso2",
            command=lambda ctx: Command("wait", {"text": "2"}),
            on_success=lambda ctx, result: None
        ),
    ]
    
    return WorkflowTask(
        name=f"mi-workflow-{command.name}",
        steps=steps
    )
```

Luego registrarlo en `command_to_task.py`:

```python
self._workflow_builders = {
    "play-song": build_play_song_workflow,
    "transcribe-me": build_transcribe_me_workflow,
    "mi-comando": build_mi_workflow,  # ← Nuevo
}
```

---

### 📝 Cambios en Container

Los workflows se registran en `CommandToTask`:

```python
# src/adapters/container.py
from src.application.use_cases.workflows.play_song_workflow import build_play_song_workflow
from src.application.use_cases.workflows.transcribe_me_workflow import build_transcribe_me_workflow

# En build_assistant():
# Los workflows se construyen bajo demanda cuando se ejecuta el comando
```

**Archivo clave:** `src/application/services/command_to_task.py`

```python
class CommandToTask:
    def __init__(self):
        self._workflow_builders = {
            "play-song": build_play_song_workflow,
            "transcribe-me": build_transcribe_me_workflow,
        }
```

---

### 🔧 Extensiones Posibles

1. **Nuevos workflows:**
   - Workflow de alarma (espera + notificación)
   - Workflow de análisis de imagen (captura + análisis IA)
   - Workflow de conversación multi-turno

2. **Mejoras a workflows existentes:**
   - Añadir logging a cada paso
   - Implementar reintentos automáticos
   - Guardar estado en disco para resumir después

3. **Composición de workflows:**
   - Workflows que llaman a otros workflows
   - Workflows paralelos (ejecutar pasos en paralelo)

