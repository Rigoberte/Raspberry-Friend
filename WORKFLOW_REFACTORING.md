## Refactorización: De Skill a Workflow

### 🎯 Cambio de Arquitectura

**Antes:**
- `ListenAndInterpretSkill`: Una skill monolítica que hacía todo (grabar, transcribir, interpretar, ejecutar, responder)
- Acoplada fuertemente con CommandDispatcher
- Difícil de reutilizar componentes

**Ahora:**
- `listen_and_interpret_workflow`: Workflow que orquesta pasos
- `InterpretAndRespondSkill`: Skill auxiliar que implementa el árbol de decisión
- Componentes desacoplados y reutilizables

---

### 📊 Arquitectura del Workflow

```
listen_and_interpret_workflow
├── Paso 1: record-audio
│   └─ Graba audio del micrófono
│
├── Paso 2: transcribe  
│   └─ Transcribe el audio grabado
│
└── Paso 3: interpret-and-respond (ÁRBOL DE DECISIÓN)
    ├─ UNA llamada a Gemini que:
    │  ├─ Transcribe (ya está hecho, pero Gemini puede reconfirmar)
    │  ├─ Interpreta si es tarea o consulta
    │  └─ Si consulta: devuelve respuesta
    │
    ├─ Si is_task = true → Ejecutar comando con dispatcher
    │  └─ Reproducir respuesta por voz (TTS)
    │
    └─ Si is_task = false → Devolver respuesta de Gemini
       └─ Reproducir respuesta por voz (TTS)
```

---

### 🔄 Flujo de Decisión en `InterpretAndRespondSkill`

#### JSON de respuesta de Gemini:
```json
{
    "is_task": true/false,
    "task_name": "comando-o-null",
    "task_args": {"text": "argumentos"},
    "response": "respuesta-si-consulta-o-null",
    "interpretation": "explicación en inglés"
}
```

#### Rama 1: Es una tarea (is_task=true)
```python
if is_task and task_name and dispatcher:
    # Crear comando
    task_command = Command(task_name, task_args)
    # Ejecutar
    task_result = dispatcher.handle(task_command)
    # Reproducir respuesta
    _speak_response(task_result.get_message())
```

#### Rama 2: Es una consulta (is_task=false)
```python
else:
    # Gemini ya dio la respuesta
    response_text = interpretation_data.get("response")
    # Reproducir respuesta
    _speak_response(response_text)
```

---

### 💡 Ventajas del Nuevo Enfoque

1. **Separación de responsabilidades:**
   - Workflow: Orquestación de pasos
   - Skill auxiliar: Lógica de decisión
   
2. **Reutilización:**
   - `record-audio` puede usarse en otros workflows
   - `transcribe` puede usarse independientemente
   - `interpret-and-respond` puede extenderse

3. **Composición:**
   - Fácil agregar nuevos pasos al workflow
   - Fácil crear variaciones (ej: workflow sin TTS)

4. **Testing:**
   - Cada componente es testeable independientemente

5. **Escalabilidad:**
   - Agregar skills de música sin conflictos
   - Crear workflows complejos combinando pasos

---

### 🚀 Cómo Usar

#### Desde el dispatcher (como comando directo):
```python
from src.application.use_cases.workflows.listen_and_interpret_workflow import build_listen_and_interpret_workflow

# Crear el workflow
command = Command("listen-to-me", {"text": "10"})
workflow = build_listen_and_interpret_workflow(command)

# Ejecutar en el scheduler
scheduler.add_task(workflow)
```

#### Como parte de un workflow más grande:
```python
# Puedes anidar workflows
steps = [
    # ... otros pasos ...
    WorkflowStep(
        name="listen",
        command=lambda ctx: Command("listen-to-me", {"text": "10"}),
        # ... manejo de resultado ...
    ),
    # ... más pasos ...
]
```

---

### 📝 Cambios en Container

**Antes:**
```python
from src.application.use_cases.skills.listen_and_interpret_skill import ListenAndInterpretSkill

listen_and_interpret = ListenAndInterpretSkill(...)
registry.register(listen_and_interpret)
```

**Ahora:**
```python
from src.application.use_cases.skills.interpret_and_respond_skill import InterpretAndRespondSkill

interpret_and_respond = InterpretAndRespondSkill(
    ai_service=gemini_adapter,
    tts_service=tts_adapter,
    command_dispatcher=dispatcher
)
registry.register(interpret_and_respond)

# El workflow se construye bajo demanda
```

---

### 🔧 Extensiones Posibles

1. **Variantes del workflow:**
   - Sin TTS (para interfaces gráficas)
   - Con logging adicional
   - Con reintentos en caso de error

2. **Nuevas skills auxiliares:**
   - `validate-command-skill`: Validar si un comando es válido
   - `log-interaction-skill`: Registrar interacciones para análisis

3. **Workflows compuestos:**
   - Workflow que combina `listen-interpret` + `music-control`
   - Workflow de diálogo multi-turno

