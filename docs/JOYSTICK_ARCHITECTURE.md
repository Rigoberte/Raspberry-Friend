# 🏗️ Arquitectura del Joystick Virtual - Diagrama Detallado

## Capas de la Arquitectura Hexagonal

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO                                   │
│                   (Interacción UI)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INBOUND ADAPTERS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  GUIWindow (Implementa PanTiltUIPort)                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ - Dibuja el joystick (canvas + círculos)                  │ │
│  │ - Detecta eventos del mouse                               │ │
│  │ - Calcula pan_dir y tilt_dir                              │ │
│  │ - Emite callback: pan_tilt_control_callback(pan, tilt)    │ │
│  │ - Métodos: show/hide_pan_tilt_controls()                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         ▲                                         │
│                         │ Pan/Tilt Control Callback               │
│                         │                                         │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
                          │ (Callback desacoplado)
                          │
┌─────────────────────────┼─────────────────────────────────────────┐
│             APPLICATION LAYER (Orquestación)                      │
├─────────────────────────┼─────────────────────────────────────────┤
│                         │                                         │
│              GUIAdapter (Orquestador)                             │
│  ┌───────────────────────┴──────────────────────────────────────┐ │
│  │ Métodos públicos:                                            │ │
│  │ - set_camera_adapter(camera_adapter)    [CLAVE]             │ │
│  │                                                              │ │
│  │ Métodos privados (callbacks):                               │ │
│  │ - _on_camera_mode_changed(mode)                             │ │
│  │   └─ Llama: window.show/hide_pan_tilt_controls()            │ │
│  │                                                              │ │
│  │ - _on_joystick_control(pan_dir, tilt_dir)                  │ │
│  │   └─ Llama: pan_tilt_controller.move_*()                    │ │
│  │                                                              │ │
│  └───────────────────────┬──────────────────────────────────────┘ │
└────────────────────────┬─┼──────────────────────────────────────────┘
                         │ │
         ┌───────────────┘ └──────────────┐
         │                                │
         ▼                                ▼
┌─────────────────────────────────┐  ┌──────────────────────────────┐
│  OUTBOUND ADAPTERS              │  │  DOMAIN MODELS               │
├─────────────────────────────────┤  ├──────────────────────────────┤
│                                 │  │                              │
│ PiCameraAdapter (Camera Impl)   │  │ PanTiltController            │
│ ┌─────────────────────────────┐ │  │ ┌──────────────────────────┐ │
│ │ Métodos claves:             │ │  │ │ - mode: manual/auto      │ │
│ │ - start_camera()            │ │  │ │ - pan_angle: 0-180       │ │
│ │   └─ Llama:                 │ │  │ │ - tilt_angle: 0-180      │ │
│ │     mode_change_callback("m")   │  │                              │ │
│ │ - track_my_face()           │ │  │ │ Métodos:                 │ │
│ │   └─ Llama:                 │ │  │ │ - move_pan_left()        │ │
│ │     mode_change_callback("a")   │  │ │ - move_pan_right()       │ │
│ │ - untrack_my_face()         │ │  │ │ - move_tilt_up()         │ │
│ │   └─ Llama:                 │ │  │ │ - move_tilt_down()       │ │
│ │     mode_change_callback("m")   │  │ │ - set_manual_mode()      │ │
│ │ - stop_camera()             │ │  │ │ - set_auto_mode()        │ │
│ │   └─ Llama:                 │ │  │ │                          │ │
│ │     mode_change_callback(None)  │  │ └──────────────────────────┘ │
│ │                             │ │  │                              │
│ │ Atributos callback:         │ │  │ Comunicación:               │
│ │ - mode_change_callback      │ │  │ - Sin imports de GUI       │ │
│ │   ↓                          │ │  │ - Solo través de callbacks │ │
│ │   (se asigna desde GUI)     │ │  │                              │
│ └─────────────────────────────┘ │  └──────────────────────────────┘
│                                 │
└─────────────────────────────────┘
```

---

## Flujo de Datos Completo

### 1️⃣ USUARIO INICIA CÁMARA

```
usuario.click("Start Camera")
         ↓
   GUIAdapter.presenter (maneja comando)
         ↓
   camera_adapter.start_camera()
         ↓
   Inicializa hardware PiCamera2
         ↓
   is_tracking = False
   pan_tilt_controller.set_manual_mode()
         ↓
   mode_change_callback("manual")  ← ¡CALLBACK!
         ↓
   GUIAdapter._on_camera_mode_changed("manual")
         ↓
   window.show_pan_tilt_controls()
         ↓
   🎮 JOYSTICK APARECE EN PANTALLA ✨
```

### 2️⃣ USUARIO MUEVE JOYSTICK

```
usuario.mueve_mouse(x=150, y=120)
         ↓
   GUIWindow._on_joystick_motion(event)
         ↓
   Calcula: pan_dir=-1 (izquierda), tilt_dir=1 (arriba)
   Dibuja: knob rojo en nueva posición
         ↓
   pan_tilt_control_callback(-1, 1)  ← ¡CALLBACK!
         ↓
   GUIAdapter._on_joystick_control(-1, 1)
         ↓
   pan_tilt_controller.move_pan_left()
   pan_tilt_controller.move_tilt_up()
         ↓
   🔄 SERVOS SE MUEVEN
```

### 3️⃣ USUARIO ACTIVA FACE TRACKING

```
usuario.click("Track Face") o comando de voz
         ↓
   camera_adapter.track_my_face()
         ↓
   is_tracking = True
   pan_tilt_controller.set_auto_mode()
   Carga cascade haarcascade_frontalface_default.xml
         ↓
   mode_change_callback("auto")  ← ¡CALLBACK!
         ↓
   GUIAdapter._on_camera_mode_changed("auto")
         ↓
   window.hide_pan_tilt_controls()
         ↓
   🚫 JOYSTICK DESAPARECE ✓
   🤖 SERVOS AHORA BAJO CONTROL AUTOMÁTICO
```

### 4️⃣ USUARIO DESACTIVA FACE TRACKING

```
usuario.comando("disable tracking")
         ↓
   camera_adapter.untrack_my_face()
         ↓
   is_tracking = False
   pan_tilt_controller.set_manual_mode()
         ↓
   mode_change_callback("manual")  ← ¡CALLBACK!
         ↓
   GUIAdapter._on_camera_mode_changed("manual")
         ↓
   window.show_pan_tilt_controls()
         ↓
   🎮 JOYSTICK REAPARECE ✓
```

### 5️⃣ USUARIO DETIENE CÁMARA

```
usuario.click("Stop Camera")
         ↓
   camera_adapter.stop_camera()
         ↓
   is_running = False
   is_tracking = False
         ↓
   mode_change_callback(None)  ← ¡CALLBACK ESPECIAL!
         ↓
   GUIAdapter._on_camera_mode_changed(None)
         ↓
   window.hide_pan_tilt_controls()
         ↓
   🚫 JOYSTICK OCULTO
   🎥 CÁMARA DETENIDA
```

---

## Puntos de Acoplamiento (Callbacks)

```
┌─ Camera Adapter ─────────────────────────────────────┐
│                                                      │
│ self.mode_change_callback = ??? (asignado de afuera)│
│                                                      │
│ Cuando necesita notificar:                          │
│ if self.mode_change_callback:                       │
│     self.mode_change_callback("manual"|"auto"|None) │
│                                                      │
└──────────────┬───────────────────────────────────────┘
               │
               │ (Se asigna en GUI Adapter)
               ▼
┌─ GUI Adapter ─────────────────────────────────────────┐
│                                                       │
│ # En set_camera_adapter():                           │
│ camera_adapter.set_mode_change_callback(            │
│     self._on_camera_mode_changed                     │
│ )                                                    │
│                                                       │
│ # Cuando se ejecuta el callback:                     │
│ def _on_camera_mode_changed(self, mode):             │
│     if mode == "manual":                             │
│         self.window.show_pan_tilt_controls()         │
│     elif mode == "auto":                             │
│         self.window.hide_pan_tilt_controls()         │
│     elif mode is None:                               │
│         self.window.hide_pan_tilt_controls()         │
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

## Verificación de Desacoplamiento

| Capa | Importa | No Importa |
|------|---------|-----------|
| **PanTiltController** (Domain) | - | GUI, Camera Adapter, anything |
| **CameraPort** (Domain Port) | ABC | GUI, Camera Impl details |
| **PanTiltUIPort** (Inbound Port) | ABC | Camera, any hardware |
| **GUIWindow** (Inbound Adapter) | PanTiltUIPort | Camera, Domain |
| **GUIAdapter** (Application) | GUI, Camera ✓ | OK: Responsable |
| **PiCameraAdapter** (Outbound) | CameraPort | GUI ✓ Desacoplado |

✅ **Resultado:** Arquitectura completamente desacoplada

---

## Casos de Prueba (Testing)

```python
# TEST 1: Joystick aparece en modo manual
camera_adapter.start_camera()
assert window.joystick_frame.winfo_viewable() == True

# TEST 2: Joystick desaparece en modo auto
camera_adapter.track_my_face()
assert window.joystick_frame.winfo_viewable() == False

# TEST 3: Callback del joystick controla servos
gui_adapter._on_joystick_control(-1, 0)  # Pan left, tilt center
assert camera_adapter.pan_tilt_controller.current_pan < 90

# TEST 4: Mode change callback se ejecuta
mock_callback = Mock()
camera_adapter.set_mode_change_callback(mock_callback)
camera_adapter.start_camera()
mock_callback.assert_called_with("manual")

# TEST 5: Sin acoplamientos
assert "GUI" not in dir(PanTiltController)
assert "Camera" not in GUIWindow.__bases__
```

---

## Principios SOLID Respetados

✅ **S**ingle Responsibility
   - PanTiltController: Lógica de servos
   - GUIWindow: Dibujar UI
   - GUIAdapter: Conectar adaptadores

✅ **O**pen/Closed
   - Puedes cambiar implementación de servos sin cambiar GUI
   - Puedes cambiar tema de GUI sin cambiar camera

✅ **L**iskov Substitution
   - Cualquier implementación de CameraPort funciona
   - Cualquier implementación de PanTiltUIPort funciona

✅ **I**nterface Segregation
   - PanTiltUIPort solo define lo necesario
   - CameraPort separado en métodos específicos

✅ **D**ependency Inversion
   - GUIAdapter depende de puertos (abstracciones)
   - No depende de implementaciones específicas
