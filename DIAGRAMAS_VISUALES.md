# Diagrama Visual: Pan/Tilt Servo Control System

## 1. Flujo General del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                     USUARIO (GUI / Terminal)                     │
│                    Presiona WASD + ESPACIO                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│             OpenCV VideoCapture (640x480)                        │
│                  Adquiere frames de cámara                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
         ┌───────────────┐   ┌──────────────────┐
         │ Procesa Frame │   │ Detecta caras    │
         │  (Frame Skip) │   │ (Haar Cascade)   │
         └───────────────┘   └────────┬─────────┘
                                      │
                                      ▼
                            ┌──────────────────────┐
                            │  Si cara detectada:  │
                            │ - Dibuja rectángulo  │
                            │ - Dibuja centro      │
                            └────────────┬─────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
          ┌──────────────────┐  ┌──────────────────┐  ┌──────────┐
          │ Si modo MANUAL:  │  │ Si modo AUTO:    │  │ Renderea │
          │ Espera WASD      │  │ Calcula ángulos  │  │ a GUI    │
          └────────┬─────────┘  └────────┬─────────┘  └──────────┘
                   │                     │
                   │                     ▼
                   │         ┌────────────────────────┐
                   │         │  FaceTracker calcula: │
                   │         │ - error_x, error_y    │
                   │         │ - new_pan, new_tilt   │
                   │         │ (con deadzone)        │
                   │         └────────┬───────────────┘
                   │                  │
                   └──────────┬───────┘
                              │
                              ▼
                   ┌──────────────────────────────┐
                   │ PanTiltController actualiza  │
                   │ - pan angle                  │
                   │ - tilt angle                 │
                   │ - Modo (MANUAL / AUTO)       │
                   └──────────┬───────────────────┘
                              │
                              ▼
                   ┌──────────────────────────────┐
                   │   ServoKitPort (interfaz)    │
                   │ set_angle(port, angle)       │
                   └──────────┬───────────────────┘
                              │
                ┌─────────────┴──────────────┐
                │                            │
                ▼                            ▼
     ┌────────────────────────┐  ┌──────────────────────────┐
     │ AdafruitServoKit      │  │ NullServoKit             │
     │ (Hardware Real)        │  │ (Null Object Pattern)    │
     │ - I2C → PCA9685       │  │ - No-op                  │
     │ - PWM → Servo         │  │ - Testing/Dev sin HW     │
     └────────────────────────┘  └──────────────────────────┘
                │                            │
                ▼                            ▼
       ┌─────────────────┐        ┌─────────────────┐
       │  Raspberry Pi   │        │  Laptop/PC      │
       │  con hardware   │        │  sin hardware   │
       │  real           │        │                 │
       └─────────────────┘        └─────────────────┘
```

---

## 2. Estructura de Clases y Relaciones

```
┌──────────────────────────────────────────────────────────┐
│               OpenCVCameraAdapter                         │
│  (src/adapters/outbound/camera/...)                      │
├──────────────────────────────────────────────────────────┤
│ - camera: cv2.VideoCapture                              │
│ - pan_tilt_controller: PanTiltController                │
│ - is_tracking: bool                                      │
│ - face_cascade: cv2.CascadeClassifier                   │
├──────────────────────────────────────────────────────────┤
│ + handle_keyboard_input(key)                             │
│ + track_my_face()                                        │
│ + __annotate_faces__(frame)                             │
│ + _toggle_face_tracking()                               │
└────────────────┬────────────────────────────────────────┘
                 │ inyecta
                 ▼
┌──────────────────────────────────────────────────────────┐
│          PanTiltController                               │
│  (src/domain/models/pan_tilt_controller.py)             │
├──────────────────────────────────────────────────────────┤
│ - servo_kit: ServoKitPort                               │
│ - face_tracker: FaceTracker                             │
│ - pan: float (0-180)                                    │
│ - tilt: float (0-180)                                   │
│ - mode: PanTiltControlMode (MANUAL | AUTO)              │
├──────────────────────────────────────────────────────────┤
│ + move_pan_left/right()                                 │
│ + move_tilt_up/down()                                   │
│ + track_face(x, y, w, h)                                │
│ + set_mode(mode)                                        │
│ + is_available()                                        │
└────────────────┬────────────────────────────────────────┘
    ┌────────────┴──────────────────────────────┐
    │ usa                                        │ delega cálculos
    ▼                                            ▼
┌─────────────────────────┐    ┌────────────────────────────┐
│    ServoKitPort         │    │    FaceTracker              │
│  (abstract interface)   │    │  (algoritmo puro)           │
│                         │    │                             │
├─────────────────────────┤    ├────────────────────────────┤
│ + set_angle()           │    │ - sensitivity: float        │
│ + get_angle()           │    │ - deadzone: int             │
│ + reset()               │    │ - center_x: int             │
│ + reset_all()           │    │ - center_y: int             │
│ + is_available()        │    │                             │
└────────┬────────────────┘    ├────────────────────────────┤
         │                      │ + calculate_servo_angles() │
         │ implementado por      └────────────────────────────┘
    ┌────┴──────────────────────┐
    │                            │
    ▼                            ▼
┌────────────────────┐  ┌──────────────────────────┐
│AdafruitServoKit    │  │NullServoKit              │
│Adapter             │  │Adapter                   │
├────────────────────┤  ├──────────────────────────┤
│- kit: ServoKit()   │  │(Null Object)             │
│- num_ports: int    │  │                          │
│- is_initialized    │  │No-op implementations     │
├────────────────────┤  │para testing sin HW       │
│ Comunica con:      │  │                          │
│ ├─ I2C bus         │  └──────────────────────────┘
│ ├─ PCA9685         │
│ └─ Servomotores    │
└────────────────────┘
```

---

## 3. Máquina de Estados: Modos de Control

```
┌────────────────────────────────────────────────────────────┐
│              Control Mode State Machine                     │
└────────────────────────────────────────────────────────────┘

┌─────────────────┐
│    STARTUP      │
│                 │
│ mode = MANUAL   │
│ pan = 90°       │
│ tilt = 90°      │
└────────┬────────┘
         │
         │ Espera entrada de usuario
         │
         ▼
    ┌─────────────────────┐
    │  MODO MANUAL        │
    │                     │  ESPACIO presionado
    │ - WASD activo       ├────────────┐
    │ - Pan/Tilt control  │            │
    │ - No tracking       │            ▼
    │                     │  ┌──────────────────────┐
    │◄────────────────────┤  │  MODO AUTO           │
    │  ESPACIO presionado │  │                      │
    │                     │  │ - WASD inactivo      │
    │                     │  │ - Tracking automático│
    │                     │  │ - FaceTracker activo │
    │                     │  │                      │
    │                     │  └──────────────────────┘
    │                     │
    │  Acciones en MANUAL:
    │  • W: tilt += 5°
    │  • S: tilt -= 5°
    │  • A: pan -= 5°
    │  • D: pan += 5°
    │  • ESPACIO: toggle mode
    │
    │  Acciones en AUTO:
    │  • Face en (x,y,w,h) → track_face()
    │  • Calcula ángulos automáticos
    │  • ESPACIO: toggle mode
    └─────────────────────┘

Transiciones:
• STARTUP → MANUAL (inicial)
• MANUAL ←→ AUTO (ESPACIO)
• Cualquier estado → SHUTDOWN (Q o error)
```

---

## 4. Pipeline de Detección y Tracking

```
Frame entrada (640x480)
        │
        ▼
┌─────────────────────┐
│ Frame Skip Check    │
│ (procesar cada 3)   │
└────────┬────────────┘
         │
         ▼
┌──────────────────────────┐
│ Conversión BGR → Gray    │
│ (para detectar caras)    │
└────────┬─────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ cv2.CascadeClassifier.detectMultiScale│
│ Parameters:                            │
│ - scaleFactor: 1.2                    │
│ - minNeighbors: 5                     │
│ - minSize: (60, 60)                   │
└────────┬───────────────────────────────┘
         │
         ├─ Si NO caras detectadas:
         │  └─ Mostrar frame sin cambios
         │
         └─ Si cara detectada (x, y, w, h):
            │
            ├─ Dibujar rectángulo (x, y, w+x, y+h)
            ├─ Dibujar punto centro en (x+w/2, y+h/2)
            │
            └─ Si modo AUTO:
               │
               ▼
            ┌──────────────────────────────┐
            │ FaceTracker.calculate...()   │
            │                              │
            │ Input:                       │
            │ - face_x, face_y, w, h      │
            │ - current_pan, current_tilt │
            │                              │
            │ Cálculos:                    │
            │ - face_center_x = x + w/2   │
            │ - face_center_y = y + h/2   │
            │ - error_x = CENTER_X - fcx  │
            │ - error_y = CENTER_Y - fcy  │
            │                              │
            │ Si abs(error_x) > DEADZONE: │
            │   new_pan -= error_x * SENS │
            │ Si abs(error_y) > DEADZONE: │
            │   new_tilt += error_y * SENS│
            │                              │
            │ Output:                      │
            │ - Constrain to [0, 180]     │
            │ - Return (new_pan, new_tilt)│
            └──────────────┬───────────────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │ Servo Movement  │
                    │                 │
                    │ servo.set_angle │
                    │  (0, new_pan)   │
                    │  (1, new_tilt)  │
                    └─────────────────┘
            │
            ▼
        ┌────────────────────┐
        │ Enviar frame a GUI │
        │ (callback)         │
        └────────────────────┘
```

---

## 5. Entrada de Usuario (Keyboard Input)

```
Usuario presiona tecla
        │
        ▼
cv2.waitKey(1) retorna ASCII code
        │
        ▼
camera.handle_keyboard_input(key)
        │
        ├─ key == ord('w'):  PAN TILT UP
        │  └─ controller.move_tilt_up()
        │     └─ tilt = min(180, tilt + 5)
        │        └─ servo.set_angle(1, tilt)
        │
        ├─ key == ord('s'):  PAN TILT DOWN
        │  └─ controller.move_tilt_down()
        │     └─ tilt = max(0, tilt - 5)
        │        └─ servo.set_angle(1, tilt)
        │
        ├─ key == ord('a'):  PAN LEFT
        │  └─ controller.move_pan_left()
        │     └─ pan = max(0, pan - 5)
        │        └─ servo.set_angle(0, pan)
        │
        ├─ key == ord('d'):  PAN RIGHT
        │  └─ controller.move_pan_right()
        │     └─ pan = min(180, pan + 5)
        │        └─ servo.set_angle(0, pan)
        │
        ├─ key == ord(' '):  TOGGLE MODE
        │  └─ _toggle_face_tracking()
        │     ├─ if tracking: untrack_my_face()
        │     │  └─ set_mode(MANUAL)
        │     └─ else: track_my_face()
        │        └─ set_mode(AUTO)
        │
        ├─ key == ord('q'):  QUIT
        │  └─ break from loop
        │
        └─ key == 255 (no key):  IGNORE
           └─ continue
```

---

## 6. Inicialización del Sistema (Container)

```
Application Start
        │
        ▼
build_gui_adapter() in container.py
        │
        ├─ Crear ThreadPoolExecutor
        ├─ Crear InMemoryEventBus
        │
        ├─ build_assistant(event_bus, executor)
        │  │
        │  ├─ Intentar crear AdafruitServoKitAdapter
        │  │  │
        │  │  ├─ if success:
        │  │  │  └─ servo_kit = AdafruitServoKitAdapter(4)
        │  │  │
        │  │  └─ except RuntimeError:
        │  │     └─ servo_kit = NullServoKitAdapter()  ← FALLBACK
        │  │
        │  ├─ pan_tilt = PanTiltController(servo_kit)
        │  ├─ camera = OpenCVCameraAdapter(pan_tilt)
        │  │
        │  ├─ Registrar skills (música, tiempo, etc.)
        │  ├─ Crear servicios (dispatcher, scheduler)
        │  │
        │  └─ return (assistant, camera, voice_cmd, mic)
        │
        ├─ Crear GUIAdapter con servicios
        ├─ Conectar callbacks:
        │  ├─ camera.set_frame_callback(gui.display_camera_frame)
        │  └─ camera.set_clear_callback(gui.clear_camera_display)
        │
        └─ return gui_adapter (¡Listo!)

Resultados posibles:
┌─ Hardware disponible:
│  └─ ✓ pan_tilt.is_available() = True
│     └─ Servos se moverán realmente
│
└─ Sin hardware:
   └─ ✓ pan_tilt.is_available() = False
      └─ Ángulos se calculan pero sin movimiento
```

---

## 7. Matriz de Responsabilidades

```
                    Domain Logic  Hardware Control  UI/Input  Testing
                    ────────────  ────────────────  ────────  ───────
FaceTracker              ✓                                  ✓
PanTiltController        ✓              (delega)           ✓
ServoKitPort                           (abstracto)         ✓
AdafruitServoKit                       ✓
NullServoKit                           ✓ (no-op)          ✓
OpenCVAdapter            (delega)                  ✓        ✓
Container               ✓ (bootstrap)

Observaciones:
• Separación limpia de responsabilidades
• Cada clase hace UNA cosa bien
• Fácil testear: mock ServoKitPort
• Fácil extender: nuevo adaptador ServoKit
```

---

## 8. Flujo de Datos (Entrada → Proceso → Salida)

```
Entrada:
├─ cv2.VideoCapture: Frames de cámara
└─ cv2.waitKey: Entrada de teclado

Procesa:
├─ Frame Processing:
│  ├─ Frame skip (reduce FPS)
│  ├─ Conversión BGR→Gray
│  ├─ Face detection (Haar)
│  └─ Face annotation (rectángulo + punto)
│
├─ Control Logic:
│  ├─ Keyboard input parsing (WASD + SPACE)
│  ├─ Mode switching (MANUAL ↔ AUTO)
│  ├─ Angle calculation (FaceTracker)
│  └─ Servo angle updating (ServoKitPort)
│
└─ State Management:
   ├─ pan, tilt angles
   ├─ control mode
   ├─ tracking status
   └─ hardware availability

Salida:
├─ GUI:
│  ├─ Frame con rostro detectado
│  ├─ Indicador de modo (MANUAL/AUTO)
│  └─ Indicador de ángulos
│
└─ Hardware:
   ├─ PWM signals a servos (si disponible)
   └─ Or silent no-op (si hardware no disponible)
```

---

## 9. Jerarquía de Directorios

```
src/
├── domain/
│   ├── models/
│   │   ├── face_tracker.py              ← Algoritmo
│   │   └── pan_tilt_controller.py       ← Orquestación
│   │
│   └── ports/
│       └── outbound/
│           └── servo_kit_ports.py       ← Contrato
│
└── adapters/
    ├── container.py                     ← Bootstrap
    │
    └── outbound/
        ├── camera/
        │   └── opencv_camera_adapter.py ← Integración
        │
        └── servo_kit/
            ├── servo_kit_adapter.py     ← Hardware Real
            ├── null_servo_kit_adapter.py ← Null Pattern
            └── __init__.py              ← Exports
```

---

Esta visualización muestra:
- 🔄 **Flujos de datos** entre componentes
- 🏗️ **Arquitectura y relaciones** entre clases
- 🎮 **Estados y transiciones** del controlador
- ⌨️ **Entrada de usuario** y respuesta del sistema
- 🔧 **Inicialización y bootstrap** del sistema
- 📊 **Responsabilidades** de cada componente
- 🗂️ **Organización** de directorios
