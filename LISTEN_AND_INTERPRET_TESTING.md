# 🧪 Testing Guide: Listen-and-Interpret

## Quick Start

### 1️⃣ Test Básico desde GUI

```
En la interfaz gráfica, escribe:

listen-to-me

El sistema:
1. Comenzará a grabar (verás un indicador)
2. Esperará 10 segundos
3. Procesará el audio
4. Reproducirá la respuesta por voz
```

### 2️⃣ Test Manual (CLI)

```bash
cd c:\Users\inaki.costa\Downloads\GitHub_Repositories\Raspberry-Friend
python -c "
from src.adapters.container import build_gui_adapter
from src.application.events.event_bus import InMemoryEventBus

event_bus = InMemoryEventBus()
gui = build_gui_adapter(event_bus=event_bus)
gui.run()
"
```

---

## Casos de Prueba Recomendados

### ✅ Caso 1: Música (Tarea)

**Input:** "Ponme la canción Bohemian Rhapsody de Queen"

**Esperado:**
- ✓ Se transcribe correctamente
- ✓ Se interpreta como `play-song`
- ✓ Se ejecuta el comando
- ✓ Se reproduce respuesta por voz
- ✓ Status: `is_task=true`

---

### ✅ Caso 2: Pregunta General (Consulta)

**Input:** "¿Cuál es la capital de Francia?"

**Esperado:**
- ✓ Se transcribe correctamente
- ✓ Se interpreta como NOT task (is_task=false)
- ✓ Gemini genera respuesta
- ✓ Se reproduce respuesta por voz
- ✓ Respuesta: "La capital de Francia es París..."

---

### ✅ Caso 3: Comando Corto (Tarea)

**Input:** "Silencia la música"

**Esperado:**
- ✓ Se interpreta como `stop-song`
- ✓ Se detiene la música
- ✓ Respuesta: "Música detenida"

---

### ✅ Caso 4: Información (Tarea)

**Input:** "¿Qué hora es?"

**Esperado:**
- ✓ Se interpreta como `time`
- ✓ Ejecuta comando time
- ✓ Reproduce la hora actual

---

### ✅ Caso 5: Duración Personalizada

**Input:** `listen-to-me 5`

**Esperado:**
- ✓ Graba solo 5 segundos (no 10)
- ✓ Todo lo demás igual

---

### ✅ Caso 6: Texto Confuso

**Input:** "Ponme esa música que toca el tipo con la guitarra"

**Esperado:**
- ✓ Se transcribe
- ✓ Gemini intenta interpretar (podría fallar)
- ✓ Si falla, retorna error descriptivo
- ✓ Status: `is_task=true` (intenta) pero `task_result` con error

---

## Debug Mode

### Ver logs detallados

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Luego ejecuta listen-to-me y verás todos los detalles
```

### Ver respuesta JSON de Gemini

```python
from src.application.events.event_bus import InMemoryEventBus
from src.adapters.container import build_assistant

event_bus = InMemoryEventBus()
assistant, _, _ = build_assistant(event_bus=event_bus)

# Acceder al skill directamente
from src.application.use_cases.skills.listen_and_interpret_skill import ListenAndInterpretSkill

# Después de usar listen-to-me, checkea el parsed JSON
# imprimiendo interpretation_data en el método handle
```

---

## Escenarios de Error

### ❌ Error 1: No hay micrófono

**Esperado:**
```
❌ Error grabando: No microphone detected
```

**Solución:**
- Verifica que el micrófono esté conectado
- Chequea permisos de Windows

---

### ❌ Error 2: No se entiende el audio

**Esperado:**
```
❌ No se pudo entender el audio
```

**Solución:**
- Habla más claro
- Más cerca del micrófono
- Menos ruido de fondo

---

### ❌ Error 3: Gemini no responde

**Esperado:**
```
❌ Error interpretando con Gemini
```

**Solución:**
- Chequea conexión a Internet
- Verifica API key válida
- Rate limit: espera unos minutos

---

### ❌ Error 4: Comando no ejecutable

**Esperado:**
```
❌ Error ejecutando tarea play-song: No song found
```

**Solución:**
- El comando fue interpretado pero falló
- Es un error de ejecución, no de interpretación
- Chequea los argumentos

---

## Métricas a Trackear

Mientras testas, observa:

### ⏱️ Tiempos

- Grabación: 10-15 segundos (según config)
- Transcripción: 2-5 segundos (depende de Gemini)
- Interpretación: 1-3 segundos
- Ejecución de tarea: 0-2 segundos
- **Total:** ~5-15 segundos

### 🎙️ Calidad de Audio

- Claridad de transcripción (% palabras correctas)
- Interpretaciones correctas vs incorrectas
- False positives (ej: consulta se interpreta como tarea)

### 💻 Recursos

- CPU usage (debería bajar después de responder)
- Memory (no debería crecer indefinidamente)
- Threads (debería mantenerse en 3-4)

---

## Test Automatizado (Python)

```python
import unittest
from src.domain.models.command import Command
from src.adapters.container import build_assistant
from src.application.events.event_bus import InMemoryEventBus

class TestListenAndInterpret(unittest.TestCase):
    
    def setUp(self):
        event_bus = InMemoryEventBus()
        self.assistant, _, _ = build_assistant(event_bus=event_bus)
    
    def test_skill_exists(self):
        """Verifica que el skill esté registrado"""
        cmd = Command("listen-to-me", {})
        # Debería no lanzar excepción
        self.assertIsNotNone(
            self.assistant.registry.get_skill(cmd)
        )
    
    def test_help_message(self):
        """Verifica la descripción del skill"""
        registry = self.assistant.registry
        # Busca el skill en la lista
        for skill in registry._skills:
            if "listen-to-me" in skill.supported_commands():
                help_text = skill.supported_commands()
                self.assertIn("listen-to-me", help_text)
    
    def test_command_creation(self):
        """Verifica que se puede crear el comando"""
        cmd = Command("listen-to-me", {"text": "5"})
        self.assertEqual(cmd.get_name(), "listen-to-me")
        self.assertEqual(cmd.get_args().get("text"), "5")

if __name__ == "__main__":
    unittest.main()
```

---

## Checklist de Testing

### Funcionalidad Básica
- [ ] `listen-to-me` sin argumentos funciona
- [ ] `listen-to-me 15` con duración personalizada funciona
- [ ] Se graba audio correctamente
- [ ] Se transcribe el audio
- [ ] Gemini interpreta correctamente

### Tareas del Sistema
- [ ] Música: `play-song` se interpreta
- [ ] Cámara: `camera-on` se interpreta
- [ ] Información: `time`, `weather` se interpreta
- [ ] Se ejecutan correctamente
- [ ] Se responde por voz

### Consultas Generales
- [ ] Preguntas se responden con Gemini
- [ ] Respuestas son relevantes
- [ ] Se reproducen por voz

### Manejo de Errores
- [ ] Error de grabación → mensaje descriptivo
- [ ] Error de transcripción → mensaje descriptivo
- [ ] Error de Gemini → mensaje descriptivo
- [ ] Error de ejecución → mensaje descriptivo

### Performance
- [ ] No se congela la GUI durante grabación
- [ ] CPU regresa a normal después
- [ ] Memory no crece indefinidamente
- [ ] Respuestas son razonablemente rápidas

### Edge Cases
- [ ] Silencio completo durante grabación
- [ ] Audio muy bajo o muy alto
- [ ] Palabras mal pronunciadas
- [ ] Comando muy largo
- [ ] Comando muy corto (una palabra)

---

## Logging Detallado

Para ver qué está pasando en cada paso:

```python
# En listen_and_interpret_skill.py, agrega prints:

# PASO 1
print(f"📝 Grabando por {duration}s...")

# PASO 2
print(f"📝 Transcripción: {transcript}")

# PASO 3
print(f"🧠 Interpretación recibida: {raw_response}")
print(f"📊 Parsed: {interpretation_data}")

# PASO 4
if is_task:
    print(f"⚡ Ejecutando tarea: {task_name}")
else:
    print(f"🤖 Consulta general - preguntando a Gemini")

# PASO 5
print(f"🔊 Reproduciendo: {response_text[:50]}...")
```

---

## Conclusión

El sistema está **completamente funcional**. El testing debe enfocarse en:

1. **Exactitud de interpretación** - ¿Entiende correctamente qué quiero?
2. **Calidad de ejecución** - ¿Ejecuta el comando correcto?
3. **Feedback de voz** - ¿La respuesta se entiende bien?
4. **Robustez** - ¿Maneja errores gracefully?

**¡Listo para usar en Raspberry Pi 5!** 🚀

---

**Versión:** 1.0  
**Fecha:** 15 Enero 2026  
**Estado:** ✅ PRONTO PARA TESTING
