# 🎤 Listen-and-Interpret: Diálogo Natural con el Robot

## Descripción General

El skill **`listen-and-interpret`** es un sistema inteligente que permite hablar naturalmente con Raspberry Friend. El robot:

1. **Escucha** tu voz a través del micrófono
2. **Transcribe** lo que dijiste con Gemini STT
3. **Interpreta** si es una tarea del sistema o una consulta general
4. **Ejecuta** la tarea O **responde** con Gemini
5. **Reproduce** la respuesta por voz (TTS)

---

## Flujo Completo

```
┌─────────────────────────────────────────────────────────┐
│ Usuario dice: "Che, ponme la canción No tengo ganas"    │
└──────────────────────────┬──────────────────────────────┘
                           ↓
        ┌──────────────────────────────────────┐
        │   PASO 1: Grabar Audio (Micrófono)   │
        │   Duración: 10 segundos (default)    │
        └──────────────────┬───────────────────┘
                           ↓
     ┌────────────────────────────────────────────┐
     │  PASO 2: Transcribir (Gemini STT)          │
     │  "Che, ponme la canción No tengo ganas"    │
     └────────────────────┬─────────────────────────┘
                          ↓
        ┌──────────────────────────────────────────┐
        │ PASO 3: Interpretar (Gemini)             │
        │ ¿Es una tarea del sistema?               │
        │ {                                        │
        │   "is_task": true,                       │
        │   "task_name": "play-song",              │
        │   "task_args": {"text": "No tengo ganas"}│
        │ }                                        │
        └──────────────────┬──────────────────────┘
                           ↓
      ┌────────────────────────────────────┐
      │ PASO 4: ¿Es tarea?                 │
      │ SÍ → Ejecutar "play-song"          │
      └────────────────┬───────────────────┘
                       ↓
     ┌────────────────────────────────────────┐
     │ PASO 5: Reproducir Respuesta (TTS)     │
     │ "Reproduciendo No tengo ganas..."      │
     └────────────────────────────────────────┘
```

---

## Comandos Soportados

El sistema puede interpretar solicitudes para cualquiera de estos comandos:

### 🎵 Música
- `play-song <nombre>` - Reproduce una canción
- `stop-song` - Detiene la música
- `pause-song` - Pausa la música
- `resume-song` - Reanuda la música
- `next-song` - Siguiente canción
- `previous-song` - Canción anterior

### 🎥 Cámara
- `camera-on` - Enciende la cámara
- `camera-off` - Apaga la cámara
- `track-face` - Activar seguimiento de rostro
- `untrack-face` - Desactivar seguimiento de rostro

### 🎙️ Audio
- `record-audio [duración]` - Graba audio
- `transcribe <ruta>` - Transcribe un archivo
- `say <texto>` - Dice un texto

### 🌍 Información
- `time` - Dice la hora
- `weather` - Dice el clima
- `calculator <expresión>` - Calcula una expresión

### 🔧 Utilidades
- `echo <texto>` - Repite texto
- `wait <segundos>` - Espera X segundos
- `list-tasks` - Lista tareas activas
- `file-explorer <ruta>` - Explora archivos
- `gemini <prompt>` - Pregunta a Gemini

---

## Ejemplos de Uso

### Ejemplo 1: Solicitar una Tarea
**Tú:** "Che, por favor ponme la canción 'No tengo ganas' de Pity A"

**Flujo:**
1. Se graba tu voz (10 segundos)
2. Se transcribe: "Che, por favor ponme la canción No tengo ganas de Pity A"
3. Gemini interpreta: `{"is_task": true, "task_name": "play-song", ...}`
4. Se ejecuta: `play-song No tengo ganas Pity A`
5. Reproduce por voz: "Reproduciendo No tengo ganas..."

---

### Ejemplo 2: Consulta General
**Tú:** "¿Cuántas copas del mundo ganó Argentina?"

**Flujo:**
1. Se graba tu voz (10 segundos)
2. Se transcribe: "¿Cuántas copas del mundo ganó Argentina?"
3. Gemini interpreta: `{"is_task": false, "task_name": null, ...}`
4. Se consulta Gemini: "Responde la pregunta sobre copas del mundo..."
5. Gemini responde: "Argentina ganó 3 Copas del Mundo: 1978, 1986 y 2022"
6. Reproduce por voz: "Argentina ganó 3 Copas del Mundo..."

---

### Ejemplo 3: Comando Corto
**Tú:** "Silencia la música"

**Flujo:**
1. Se graba tu voz (10 segundos)
2. Se transcribe: "Silencia la música"
3. Gemini interpreta: `{"is_task": true, "task_name": "stop-song", ...}`
4. Se ejecuta: `stop-song`
5. Reproduce por voz: "Música detenida"

---

## Uso en la GUI

### Comando Manual
```
listen-to-me
```

O con duración personalizada:
```
listen-to-me 15
```

(15 segundos de grabación en lugar de 10)

---

## Arquitectura Interna

### Componentes Principales

1. **RecordAudioSkill** - Graba audio del micrófono
2. **TranscribeSkill** - Convierte audio a texto (Gemini STT)
3. **AI_ChatbotSkill** - Accede a Gemini para interpretación y respuestas
4. **SaySkill** - Reproduce respuestas por voz (TTS)
5. **CommandDispatcher** - Ejecuta comandos interpretados

### Flujo Técnico

```python
# 1. Grabar
audio_path = mic.record(duration=10)

# 2. Transcribir
transcript = transcription.transcribe(audio_path)

# 3. Interpretar
prompt = f"¿Es tarea o consulta? '{transcript}'"
interpretation_json = gemini.generate_text(prompt)
parsed = json.loads(interpretation_json)

# 4. Ejecutar o Responder
if parsed["is_task"]:
    # Ejecutar tarea
    command = Command(parsed["task_name"], parsed["task_args"])
    result = dispatcher.handle(command)
else:
    # Consulta general
    result = gemini.generate_text(f"Responde: {transcript}")

# 5. Reproducir
tts.speak(result)
```

---

## Prompt de Interpretación

El sistema usa un prompt especial para Gemini que:

1. **Lista todos los comandos disponibles**
2. **Proporciona ejemplos** de cómo interpretar entrada natural
3. **Pide respuesta en JSON** con estructura consistente
4. **Asegura respuesta válida** sin markdown

**Estructura JSON esperada:**
```json
{
  "is_task": true/false,
  "task_name": "nombre-comando",
  "task_args": {"text": "argumentos"},
  "interpretation": "Explicación breve"
}
```

---

## Configuración

Puedes ajustar parámetros en `src/configs/configs_dev.py`:

```python
# Duración por defecto de grabación (segundos)
# Default: 10 segundos
LISTEN_DEFAULT_SECONDS = 10

# Máximo de caracteres para reproducir por TTS
# Default: 500 caracteres
LISTEN_MAX_TTS_LENGTH = 500
```

---

## Casos de Uso Reales

### 1. Control de Música (Más Común)
```
Usuario: "Siguiente canción"
→ Detecta: play-song
→ Ejecuta: next-song
→ Resultado: "Reproduciendo siguiente..."
```

### 2. Control de Cámara
```
Usuario: "Enciende la cámara y rastrea mi cara"
→ Detecta: camera-on + track-face (o dos comandos)
→ Ejecuta: camera-on, track-face
→ Resultado: "Cámara activada con seguimiento..."
```

### 3. Información General
```
Usuario: "¿Qué hora es?"
→ Detecta: time
→ Ejecuta: time
→ Resultado: "Son las 14:30"
```

### 4. Consultas que NO son del Sistema
```
Usuario: "¿Cuál es la capital de Francia?"
→ Detecta: NOT task (es_task=false)
→ Consulta Gemini
→ Resultado: "La capital de Francia es París..."
```

---

## Manejo de Errores

El sistema maneja elegantemente:

✅ **Audio no grabado correctamente**
- Retorna: "❌ Error grabando: [detalles]"

✅ **Transcripción fallida**
- Retorna: "❌ Error transcribiendo: [detalles]"

✅ **Gemini no responde**
- Retorna: "❌ Error interpretando con Gemini"

✅ **Comando inválido**
- Retorna: "❌ Error ejecutando tarea: [detalles]"

✅ **Respuesta incompleta**
- Usa defaults y maneja excepciones

---

## Ventajas de Este Enfoque

1. **Natural** - Hablas como lo harías normalmente
2. **Inteligente** - Entiende contexto y matices
3. **Flexible** - Funciona con muchas variaciones de entrada
4. **Feedback** - Siempre reproduce una respuesta por voz
5. **Robusto** - Maneja errores con gracia
6. **Abierto** - Las consultas generales van a Gemini
7. **Eficiente** - No requiere configuración previa

---

## Roadmap Futuro

1. **Multi-comando** - Entender y ejecutar múltiples comandos en una frase
   - Ejemplo: "Enciende la cámara y reproduce música"

2. **Context awareness** - Recordar contexto de conversaciones previas
   - Ejemplo: "Ponla en repeat" después de "ponme Bohemian Rhapsody"

3. **Voice profiles** - Adaptarse a diferentes voces/acentos

4. **Custom commands** - Permitir crear comandos personalizados

5. **Confidence scores** - Mostrar qué tan seguro está de su interpretación

---

## Troubleshooting

### "No se pudo grabar audio"
✓ Verifica que el micrófono esté conectado y funcionando
✓ Chequea permisos de acceso al micrófono
✓ Intenta `record-audio 5` directamente para testear

### "No se pudo transcribir"
✓ Verifica tu conexión a Internet (Gemini necesita conexión)
✓ Chequea que GEMINI_API_KEY sea válida
✓ Intenta hablar más lentamente y claro

### "Error interpretando con Gemini"
✓ API rate limit alcanzado - espera minutos
✓ API key inválida o sin créditos
✓ Problema de red - chequea conexión

### "No reconoce mi comando"
✓ Sé más claro y explícito
✓ Usa palabras que estén en la lista de comandos
✓ Ejemplo MAL: "dame música" → MAL
✓ Ejemplo BIEN: "Ponme una canción" → BIEN

---

**Versión:** 1.0  
**Fecha:** 15 Enero 2026  
**Estado:** ✅ Implementado y Listo para Usar
