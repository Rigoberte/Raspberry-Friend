# 🔌 Arquitectura de Integración GUI-Cámara

## Diagrama de Componentes

```
┌────────────────────────────────────────────────────────┐
│                    USER INTERACTION                    │
│                                                        │
│  GUI Window Input: "turn-on-camera"                   │
│          ↓                                             │
│  GUIWindow._on_send_clicked()                         │
│          ↓                                             │
│  on_command callback → ConsolePresenter.handle_input()│
│          ↓                                             │
│  ExecuteCommandUseCase.execute()                      │
│          ↓                                             │
│  CommandDispatcher.dispatch()                         │
│          ↓                                             │
│  CameraSkill.handle() → "turn-on-camera"             │
│          ↓                                             │
│  OpenCVCameraAdapter.start_camera()                   │
│          ↓                                             │
│  self.is_running = True                               │
│  Thread: __display_camera_feed__()                    │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│              CAMERA FRAME STREAMING                    │
│                                                        │
│  while self.is_running:                               │
│    ↓                                                   │
│    ret, frame = camera.read()  # BGR numpy array      │
│    ↓                                                   │
│    if self.frame_callback:                            │
│      ↓                                                 │
│      self.frame_callback(frame)  ←─┐                  │
│                                     │                  │
└─────────────────────────────────────┼──────────────────┘
                                      │
                  ┌───────────────────┘
                  │
                  ↓
┌────────────────────────────────────────────────────────┐
│            GUI FRAME RECEPTION & DISPLAY              │
│                                                        │
│  GUIAdapter.display_camera_frame(frame)               │
│    ↓                                                   │
│    self.window.display_camera_frame(frame)            │
│    ↓                                                   │
│    GUIWindow.display_camera_frame(frame)              │
│    ↓                                                   │
│    1. Convertir BGR→RGB con cv2.cvtColor()            │
│    2. Convertir numpy array → PIL.Image               │
│    3. Redimensionar imagen con thumbnail()           │
│    4. Convertir PIL.Image → PIL.ImageTk.PhotoImage    │
│    5. Mostrar en canvas.create_image()                │
│    ↓                                                   │
│    GUI Window se actualiza en pantalla                │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Secuencia de Inicialización

```
build_gui_adapter(...)
  ├─ event_bus = InMemoryEventBus()
  ├─ executor = ThreadPoolExecutorAdapter()
  ├─ assistant, camera, voice_cmd, mic = build_assistant(...)
  │
  ├─ gui_adapter = GUIAdapter(
  │     assistant_service=assistant,
  │     event_bus=event_bus,
  │     title="Raspberry Friend",
  │     width=900,
  │     height=700
  │  )  # Crea GUILoggerAdapter internamente
  │
  ├─ camera.set_frame_callback(
  │     gui_adapter.display_camera_frame  ←─────┐
  │   )                                         │
  │                                             │
  └─ gui_adapter.set_voice_command_adapter(    │
       voice_command_adapter=voice_cmd,        │
       mic_adapter=mic                          │
     )                                          │
                                                │
  ↓                                             │
  gui_adapter.run()  # Inicia mainloop de Tkinter
```

## Flujo de Datos Completo

```
┌──────────────────────┐
│  USUARIO ESCRIBE:    │
│  "turn-on-camera"    │
└──────────┬───────────┘
           ↓
     ┌─────────────┐
     │  Entry Box  │ (gui_window.py)
     └─────┬───────┘
           ↓
     ┌─────────────────────────────┐
     │ _on_send_clicked()          │
     │ Command: "turn-on-camera"   │
     └─────┬───────────────────────┘
           ↓
     ┌──────────────────────────────┐
     │ on_command callback invoked  │
     │ (presenter.handle_user_input)│
     └─────┬────────────────────────┘
           ↓
     ┌────────────────────────────────┐
     │ ExecuteCommandUseCase.execute()│
     └─────┬──────────────────────────┘
           ↓
     ┌────────────────────────────────┐
     │ CommandDispatcher.dispatch()    │
     └─────┬──────────────────────────┘
           ↓
     ┌────────────────────────────────┐
     │ CameraSkill.handle()            │
     │ → __turn_on_camera__()          │
     └─────┬──────────────────────────┘
           ↓
     ┌────────────────────────────────┐
     │ OpenCVCameraAdapter            │
     │ .start_camera()                │
     │                                │
     │ self.is_running = True          │
     │ Thread: __display_camera_feed()│
     └─────┬──────────────────────────┘
           ↓
    ┌──────────────────────────────────┐
    │  LOOP EN THREAD DE CÁMARA:        │
    │                                  │
    │  while self.is_running:          │
    │    frame = camera.read()         │ BGR (OpenCV)
    │    callback(frame) ─────┐        │
    └──────────────────────────┼───────┘
                               │
                               ↓
    ┌──────────────────────────────────┐
    │  GUI THREAD RECIBE FRAME          │
    │                                  │
    │  GUIAdapter.display_camera_frame()│
    │    ↓                              │
    │  canvas.delete("all")            │
    │    ↓                              │
    │  PIL conversión y redimensionar   │
    │    ↓                              │
    │  PhotoImage = ImageTk.PhotoImage()│
    │    ↓                              │
    │  canvas.create_image(...)         │
    │    ↓                              │
    │  canvas.coords(...)               │
    └──────────────────────────────────┘
           ↓
    ┌──────────────────────────────────┐
    │  PANTALLA SE ACTUALIZA            │
    │  (≈30 FPS típicamente)            │
    └──────────────────────────────────┘
```

## Arquitectura de Callbacks

```
┌─────────────────────────────────────────────────┐
│  OpenCVCameraAdapter                            │
│                                                 │
│  self.frame_callback: Optional[Callable]        │
│                                                 │
│  def set_frame_callback(callback):              │
│      self.frame_callback = callback             │
│                                                 │
│  def __display_camera_feed__():                 │
│      while self.is_running:                     │
│          ret, frame = camera.read()             │
│          if self.frame_callback:                │
│              self.frame_callback(frame) ←────┐  │
│                                            │  │
└────────────────────────────────────────────┼──┘
                                             │
                                             │ Referencias
                                             │
┌─────────────────────────────────────────┬─┘
│  GUIAdapter                             │
│                                         │
│  def display_camera_frame(frame):       │
│      self.window.display_camera_frame() │
│                                         │
└─────────────────┬───────────────────────┘
                  │ Delega a
┌─────────────────┴───────────────────────┐
│  GUIWindow                              │
│                                         │
│  def display_camera_frame(frame):       │
│      # Convierte BGR→RGB con cv2        │
│      # PIL.Image → PhotoImage           │
│      # Muestra en canvas (thread-safe)  │
│                                         │
└─────────────────────────────────────────┘
│      # Convierte BGR→RGB                │
│      # Redimensiona                     │
│      # Muestra en canvas                │
│                                         │
└─────────────────────────────────────────┘
```

## Separación de Responsabilidades

```
OpenCVCameraAdapter
├─ ✅ Capturar frames de la cámara
├─ ✅ Manejar threading
├─ ✅ Invocar callback (sin conocer detalles)
└─ ❌ NO sabe cómo mostrar

GUIAdapter (Fachada)
├─ ✅ Delega a GUIWindow
├─ ✅ Interfaz pública para frames
└─ ❌ NO sabe detalles de Tkinter

GUIWindow (Vista)
├─ ✅ Renderizar en pantalla
├─ ✅ Convertir formatos de imagen
├─ ✅ Manejar eventos de UI
└─ ❌ NO sabe de OpenCV ni threading

CameraSkill (Caso de Uso)
├─ ✅ Orquestar comandos
├─ ✅ Validar estado
└─ ❌ NO sabe de GUI
```

## Manejo de Errores

```
display_camera_frame(frame: np.ndarray)
    ↓
Try:
    ├─ Convertir BGR→RGB
    ├─ Crear PIL Image
    ├─ Redimensionar
    ├─ Crear PhotoImage
    ├─ Dibujar en canvas
    └─ ✅ Frame mostrado
    
Except Exception as e:
    └─ add_output(f"Error: {e}", ERROR)
```

## Estados de la Cámara

```
┌─────────────────┐
│  INITIALIZED    │ (Adapter creado, camera=None)
└────────┬────────┘
         │ start_camera()
         ↓
┌──────────────────────┐
│  RUNNING             │ (Thread activo, mostrando frames)
├──────────────────────┤
│ is_running = True    │
│ frame_callback(...)  │ ← Enviando frames al GUI
└────────┬─────────────┘
         │ stop_camera()
         ↓
┌──────────────────────┐
│  STOPPED             │ (Thread finalizado)
├──────────────────────┤
│ is_running = False   │
│ camera = None        │
└──────────────────────┘
```

## Ventajas de esta Arquitectura

✅ **Desacoplamiento:** Camera no sabe de GUI
✅ **Flexibilidad:** Callback permite múltiples consumidores
✅ **Threading:** Frames capturados sin bloquear UI
✅ **Compatibilidad:** Fallback a ventana si no hay callback
✅ **Modularidad:** Cada componente tiene una responsabilidad clara
✅ **Testing:** Cada módulo puede ser testeado independientemente
