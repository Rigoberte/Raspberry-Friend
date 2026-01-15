# Camera Skill - Documentación

## Descripción

Se ha agregado una nueva funcionalidad **Camera Skill** que permite encender y apagar la cámara de tu dispositivo Raspberry Pi o computadora. La cámara se muestra en tiempo real en una ventana OpenCV.

## Arquitectura

La implementación sigue la arquitectura hexagonal del proyecto:

### 1. **Puerto (Domain Layer)**
- **Archivo**: `src/domain/ports/outbound/camera_ports.py`
- **Clase**: `CameraPort` (interfaz abstracta)
- Define los métodos que debe implementar cualquier adaptador de cámara:
  - `start_camera()`: Inicia y muestra la cámara
  - `stop_camera()`: Detiene la cámara
  - `is_camera_available()`: Verifica si hay una cámara disponible

### 2. **Adaptador (Adapters Layer)**
- **Archivo**: `src/adapters/outbound/camera/opencv_camera_adapter.py`
- **Clase**: `OpenCVCameraAdapter` (implementa `CameraPort`)
- Utiliza OpenCV (cv2) para capturar y mostrar el feed de cámara
- Maneja la cámara en un thread separado para no bloquear la aplicación
- Características:
  - Detección automática de disponibilidad de cámara
  - Display en tiempo real
  - Opción de cerrar la ventana presionando 'q'

### 3. **Skill (Application Layer)**
- **Archivo**: `src/application/use_cases/skills/camera_skill.py`
- **Clase**: `CameraSkill` (extiende `RobotSkill`)
- Maneja los comandos:
  - `turn-on-camera`: Enciende la cámara
  - `turn-off-camera`: Apaga la cámara
- Valida disponibilidad de cámara antes de ejecutar
- Proporciona mensajes de error descriptivos

### 4. **Contenedor de Inyección de Dependencias**
- **Archivo**: `src/adapters/container.py`
- La skill está registrada en el `build_assistant()` function
- Se crea una instancia de `OpenCVCameraAdapter` y se inyecta en `CameraSkill`

## Uso

### Desde la CLI

```bash
# Encender la cámara
turn-on-camera

# Apagar la cámara
turn-off-camera
```

### Desde código Python

```python
from src.adapters.container import build_assistant
from src.application.services.command_parser import CommandParser
from src.application.use_cases.execute_command_use_case import ExecuteCommandUseCase

# Crear asistente
assistant, _ = build_assistant()

# Crear parser y ejecutor
parser = CommandParser()
execute_uc = ExecuteCommandUseCase(assistant, logger)

# Encender cámara
command = parser.parse("turn-on-camera")
result = execute_uc.execute(command)
print(result.message)

# Apagar cámara
command = parser.parse("turn-off-camera")
result = execute_uc.execute(command)
print(result.message)
```

## Dependencias

La funcionalidad requiere:
- **opencv-python** (>= 4.8.1.78) - Se ha agregado a `requirements.txt`
- **threading** (librería estándar de Python)

Para instalar:
```bash
pip install -r requirements.txt
```

## Características Principales

✅ **Arquitectura Hexagonal**: Separa completamente la interfaz de usuario de la lógica de negocio
✅ **Sin Acoplamiento**: El modelo de dominio no conoce sobre OpenCV o detalles de implementación
✅ **Thread-safe**: Maneja la cámara en un thread separado
✅ **Detección automática**: Verifica si la cámara está disponible antes de intentar usarla
✅ **Mensajes descriptivos**: Proporciona feedback claro al usuario
✅ **Manejo de errores**: Captura y reporta errores de forma elegante

## Testing

Se han creado tests unitarios en:
- `tests/unit/application/skills/test_camera_skill.py`

Ejecutar los tests:
```bash
pytest tests/unit/application/skills/test_camera_skill.py -v
```

### Casos de prueba cubiertos:
- ✅ Registro correcto de comandos
- ✅ Manejo de comando "turn-on-camera"
- ✅ Manejo de comando "turn-off-camera"
- ✅ Validación de disponibilidad de cámara
- ✅ Manejo de errores en inicio y parada
- ✅ Estado correcto de llamadas a métodos

## Mejoras Futuras

Para completar la funcionalidad, se pueden agregar:
1. Grabación de video
2. Captura de fotos
3. Filtros y transformaciones de imagen
4. Transmisión en vivo (streaming)
5. Detección de movimiento
6. Reconocimiento facial

## Estructura de Archivos Creados

```
src/
├── domain/
│   └── ports/outbound/
│       └── camera_ports.py          (Puerto/Interfaz)
├── adapters/
│   └── outbound/camera/
│       ├── __init__.py
│       └── opencv_camera_adapter.py (Adaptador)
└── application/
    └── use_cases/skills/
        └── camera_skill.py          (Skill)

tests/
└── unit/application/skills/
    └── test_camera_skill.py         (Tests)

examples/
└── camera_skill_example.py          (Ejemplo de uso)

requirements.txt (actualizado con opencv-python)
```

## Notas Técnicas

- La cámara se ejecuta en un daemon thread, lo que significa que cerrará automáticamente cuando la aplicación principal se cierre
- La función `is_camera_available()` hace una prueba rápida abriendo y cerrando la cámara
- El evento `cv2.waitKey(1)` permite procesar interrupciones de teclado de forma no-bloqueante
- El adapter es independiente de cualquier implementación específica de cámara, lo que permite agregar adaptadores alternativos en el futuro

