# Arquitectura Detallada: Control de Servomotores Pan/Tilt

## Diagrama de Capas

```
┌────────────────────────────────────────────────────────────┐
│                    PRESENTACIÓN (GUI)                       │
│                   OpenCV Window / PyQt                       │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     │ Frames + Keyboard Input
                     ▼
┌────────────────────────────────────────────────────────────┐
│            ADAPTADORES DE ENTRADA (Inbound)                │
│                                                             │
│  OpenCVCameraAdapter                                        │
│  ├─ Recibe frames de OpenCV                               │
│  ├─ Procesa teclado WASD + ESPACIO                        │
│  ├─ Inyecta PanTiltController                             │
│  └─ Integra face detection + tracking automático           │
└────────────────────┬─────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐  ┌──────────┐  ┌─────────────┐
    │ Camera │  │Pan/Tilt  │  │Face Tracker │
    │ (Port) │  │Controller│  │(Model)      │
    └────────┘  └──────────┘  └─────────────┘
        │            │            │
        │ Dominio    │            │
        │            │            │
        └────────────┼────────────┘
                     │
        ┌────────────▼──────────────┐
        │                           │
        │    ServoKitPort           │
        │    (Outbound Port)        │
        │                           │
        │  Abstracción de Hardware  │
        └────────────┬──────────────┘
                     │
        ┌────────────┴──────────────┐
        │                           │
        ▼                           ▼
   ┌─────────────────┐   ┌──────────────────┐
   │ AdafruitServoKit│   │ NullServoKit     │
   │   Adapter       │   │  Adapter         │
   │ (Real Hardware) │   │ (No-op Pattern)  │
   └─────────────────┘   └──────────────────┘
        │                           │
        ▼                           ▼
   ┌─────────────────┐   ┌──────────────────┐
   │ Raspberry Pi    │   │  Testing / Dev   │
   │ with I2C bus    │   │  without hardware│
   │ PCA9685 driver  │   │                  │
   └─────────────────┘   └──────────────────┘
```

---

## Flujo de Interacción Detallado

### 1. INICIALIZACIÓN

```
Build Container
    │
    ├─ Intenta crear AdafruitServoKitAdapter
    │  ├─ Si RuntimeError → Usa NullServoKitAdapter
    │  └─ Si éxito → Usa adaptador real
    │
    ├─ Crea PanTiltController(servo_kit)
    │  ├─ Inicializa pan = 90°
    │  ├─ Inicializa tilt = 90°
    │  ├─ Modo = MANUAL
    │  └─ Crea FaceTracker interno
    │
    └─ Crea OpenCVCameraAdapter(pan_tilt_controller)
       ├─ Almacena referencia al controlador
       └─ Listo para recibir frames
```

### 2. CONTROL MANUAL (WASD)

```
Usuario presiona 'D'
    │
    └─ cv2.waitKey() retorna key=100 (ord('d'))
       │
       └─ camera.handle_keyboard_input(100)
          │
          ├─ Verifica modo == MANUAL
          │
          └─ pan_tilt_controller.move_pan_right()
             │
             ├─ pan = min(180, pan + 5) → 95°
             │
             └─ servo_kit.set_angle(port=0, angle=95)
                │
                ├─ Si AdafruitServoKitAdapter:
                │  └─ kit.servo[0].angle = 95
                │     └─ I2C → PCA9685 → PWM signal → Servo
                │
                └─ Si NullServoKitAdapter:
                   └─ return {"success": False, ...}
                      (sin error, solo registro silencioso)
```

### 3. CONTROL AUTOMÁTICO (ESPACIO)

```
Usuario presiona ESPACIO
    │
    └─ cv2.waitKey() retorna key=32 (ord(' '))
       │
       └─ camera.handle_keyboard_input(32)
          │
          └─ camera._toggle_face_tracking()
             │
             ├─ if is_tracking:
             │  └─ untrack_my_face()
             │     ├─ is_tracking = False
             │     ├─ controller.set_mode(MANUAL)
             │     └─ window_name = "Camera"
             │
             └─ else:
                └─ track_my_face()
                   ├─ Carga Haar Cascade
                   ├─ is_tracking = True
                   ├─ controller.set_mode(AUTO)
                   └─ window_name = "Face Tracking"
```

### 4. FRAME PROCESSING CON TRACKING AUTOMÁTICO

```
En cada frame (10fps después del frame skip):
    │
    ├─ camera.__display_camera_feed__()
    │  │
    │  ├─ camera.read() → frame
    │  │
    │  ├─ if is_tracking:
    │  │  └─ __annotate_faces__(frame)
    │  │     │
    │  │     ├─ gray = cvtColor(frame, BGR2GRAY)
    │  │     │
    │  │     ├─ faces = face_cascade.detectMultiScale(...)
    │  │     │  └─ Retorna lista de (x, y, w, h)
    │  │     │
    │  │     └─ for (x, y, w, h) in faces[:1]:  # Primera cara
    │  │        │
    │  │        ├─ cv2.rectangle(...)  # Dibujar bounding box
    │  │        ├─ cv2.circle(...)     # Dibujar centro
    │  │        │
    │  │        └─ if controller.mode == AUTO:
    │  │           │
    │  │           └─ controller.track_face(x, y, w, h)
    │  │              │
    │  │              ├─ face_tracker.calculate_servo_angles(...)
    │  │              │  │
    │  │              │  ├─ face_center_x = x + w//2
    │  │              │  ├─ face_center_y = y + h//2
    │  │              │  │
    │  │              │  ├─ error_x = CENTER_X(320) - face_center_x
    │  │              │  ├─ error_y = CENTER_Y(240) - face_center_y
    │  │              │  │
    │  │              │  ├─ if abs(error_x) > DEADZONE(10):
    │  │              │  │  └─ new_pan = pan - (error_x * SENSITIVITY)
    │  │              │  │
    │  │              │  ├─ if abs(error_y) > DEADZONE(10):
    │  │              │  │  └─ new_tilt = tilt + (error_y * SENSITIVITY)
    │  │              │  │
    │  │              │  └─ return (constrain to 0-180)
    │  │              │
    │  │              ├─ pan = new_pan
    │  │              ├─ tilt = new_tilt
    │  │              │
    │  │              ├─ servo_kit.set_angle(0, pan)
    │  │              └─ servo_kit.set_angle(1, tilt)
    │  │
    │  └─ view_callback(frame)  # Enviar a GUI
    │
    └─ Repetir cada ~100ms (10fps)
```

---

## Interacciones de Clases

### OpenCVCameraAdapter → PanTiltController

```python
class OpenCVCameraAdapter(CameraPort):
    def __init__(self, pan_tilt_controller: Optional[PanTiltController] = None):
        self.pan_tilt_controller = pan_tilt_controller
        # ...
    
    def handle_keyboard_input(self, key: int) -> None:
        if self.pan_tilt_controller is None:
            return
        
        # Delegación de responsabilidad:
        if key == ord('w'):
            self.pan_tilt_controller.move_tilt_up()
        elif key == ord(' '):
            self.pan_tilt_controller.set_mode(...)
        # ...
    
    def __annotate_faces__(self, frame):
        # ...
        if self.pan_tilt_controller.get_mode() == PanTiltControlMode.AUTO:
            self.pan_tilt_controller.track_face(x, y, w, h)
        # ...
```

### PanTiltController → ServoKitPort

```python
class PanTiltController:
    def __init__(self, servo_kit: ServoKitPort, pan_port: int, tilt_port: int):
        self.servo_kit = servo_kit  # ← Inyección de dependencia
        self.pan_port = pan_port
        self.tilt_port = tilt_port
    
    def move_pan_right(self) -> None:
        self.pan = min(180, self.pan + self.MANUAL_STEP)
        self.servo_kit.set_angle(self.pan_port, self.pan)
        # ↑ Abstracción: no importa si es Real o Null
    
    def track_face(self, face_x, face_y, face_w, face_h) -> None:
        self.pan, self.tilt = self.face_tracker.calculate_servo_angles(...)
        self.servo_kit.set_angle(self.pan_port, self.pan)
        self.servo_kit.set_angle(self.tilt_port, self.tilt)
        # ↑ Delega lógica de cálculo a FaceTracker
```

### PanTiltController → FaceTracker

```python
class PanTiltController:
    def __init__(self, servo_kit, pan_port, tilt_port):
        self.face_tracker = FaceTracker()  # ← Composición
        # ...
    
    def track_face(self, face_x, face_y, face_w, face_h):
        # FaceTracker es responsable SOLO de cálculos
        self.pan, self.tilt = self.face_tracker.calculate_servo_angles(
            face_x, face_y, face_w, face_h,
            self.pan, self.tilt
        )
        # ← FaceTracker no conoce servomotores
```

---

## Manejo de Errores y Estados

### Estado del Sistema

```
OpenCVCameraAdapter
├─ is_running: bool          ← Cámara encendida
├─ is_tracking: bool         ← Face tracking activo
├─ pan_tilt_controller: Optional[PanTiltController]
│  ├─ mode: PanTiltControlMode (MANUAL | AUTO)
│  ├─ pan: float (0-180)
│  ├─ tilt: float (0-180)
│  ├─ servo_kit: ServoKitPort
│  │  └─ is_available(): bool ← Hardware disponible
│  └─ face_tracker: FaceTracker
│     ├─ sensitivity: float
│     └─ deadzone: int
└─ face_cascade: cv2.CascadeClassifier
```

### Transiciones de Estado

```
INICIO:
  is_running=False, is_tracking=False, mode=MANUAL
    │
    ├─ start_camera() → is_running=True
    │
    ├─ track_my_face() → is_tracking=True, mode=AUTO
    │
    └─ untrack_my_face() → is_tracking=False, mode=MANUAL
       │
       └─ stop_camera() → is_running=False
```

---

## Manejo del Null Object Pattern

```
Bootstrap (Container.py):
    │
    ├─ try:
    │  └─ servo_kit = AdafruitServoKitAdapter(num_ports=4)
    │
    └─ except RuntimeError:
       └─ servo_kit = NullServoKitAdapter()  ← Fallback

Desde la perspectiva de PanTiltController:
    │
    └─ No importa cual sea el adaptador
       ├─ Mismo puerto (ServoKitPort)
       ├─ Misma interfaz (set_angle, get_angle, etc.)
       ├─ Mismo comportamiento (retorna dict con success/error)
       └─ Diferencia: Real mueve servo, Null retorna success=False silenciosamente

Ventajas:
    ├─ Sin excepciones
    ├─ Sin chequeos nulos en cliente
    ├─ Permite testing sin hardware
    ├─ Funcionalidad parcial en desarrollo
    └─ Código limpio y predecible
```

---

## Responsabilidades Claras

```
OpenCVCameraAdapter (Adapter):
├─ Responsabilidad: Captura de frames + integración
├─ Maneja: Camera I/O, threading, callbacks
├─ NO maneja: Lógica de movimiento
└─ Delega a: PanTiltController

PanTiltController (Domain):
├─ Responsabilidad: Orquestación de control
├─ Maneja: Estados (MANUAL/AUTO), movimientos
├─ NO maneja: Cálculos de tracking
├─ Delega a: FaceTracker (cálculos), ServoKitPort (hardware)
└─ Usa: inyección de dependencias

FaceTracker (Domain - Model):
├─ Responsabilidad: Algoritmo de seguimiento
├─ Maneja: Cálculos de ángulos basado en posición de cara
├─ NO maneja: Control de hardware
└─ NO maneja: Detección de caras

AdafruitServoKitAdapter / NullServoKitAdapter (Adapter):
├─ Responsabilidad: Abstraer hardware
├─ Maneja: Comunicación I2C/PWM (real) o no-op (null)
├─ NO maneja: Lógica de control
└─ Implementa: ServoKitPort
```

---

## Extensibilidad

```
Para agregar novo control (ej: velocidad de tracking):

1. Agregar parámetro a FaceTracker:
   sensitivity_high = 0.02
   sensitivity_low = 0.01

2. Agregar método a PanTiltController:
   def set_tracking_sensitivity(self, level: str)

3. Llamar desde OpenCVCameraAdapter:
   if key == ord('+'): controller.set_tracking_sensitivity('high')

4. Sin cambios en hardware (ServoKitPort)
5. Totalmente compatible con NullServoKitAdapter
```

---

## Testing Strategy

```
Unit Tests:
├─ test_pan_tilt_controller.py
│  ├─ Usa MockServoKitAdapter
│  ├─ Tests sin I/O
│  └─ Tests rápidos y determinísticos
│
├─ test_face_tracker.py
│  ├─ Tests de algoritmo puro
│  ├─ Validación de cálculos
│  └─ Parámetros configurables
│
└─ test_servo_kit_adapters.py (futuro)
   ├─ NullServoKitAdapter
   ├─ AdafruitServoKitAdapter (mocked)
   └─ Interface compliance

Integration Tests:
└─ test_camera_with_pan_tilt.py (futuro)
   ├─ Camera + Controller + Tracking
   └─ Flujos completos
```

---

## Conclusión

La arquitectura implementa:
- ✅ **Hexagonal Architecture**: Puertos y adaptadores claros
- ✅ **Separation of Concerns**: Cada clase una responsabilidad
- ✅ **Dependency Injection**: Inyección explícita
- ✅ **Design Patterns**: Null Object, Strategy
- ✅ **Testability**: Fácil de mockear y testear
- ✅ **Maintainability**: Código limpio y documentado
- ✅ **Extensibility**: Fácil agregar nuevas funcionalidades
