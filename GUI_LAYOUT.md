# 🤖 Nuevo Layout del GUI - Raspberry Friend

## Estructura Visual

```
╔════════════════════════════════════════════════════════╗
║              🤖 Raspberry Friend Console               ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║                 📹 Vista en Vivo                       ║
║  ╔──────────────────────────────────────────────────╗ ║
║  │                                                  │ ║
║  │     [Aquí se muestra el stream de cámara]       │ ║
║  │     cuando ejecutas "turn-on-camera"            │ ║
║  │                                                  │ ║
║  │     (70% del espacio de la ventana)              │ ║
║  │                                                  │ ║
║  ╚──────────────────────────────────────────────────╝ ║
║                                                        ║
║ ════ [Divisor Redimensionable] ════════════════════  ║
║                                                        ║
║                   📋 Consola                          ║
║  ╔──────────────────────────────────────────────────╗ ║
║  │ > turn-on-camera                                 │ ║
║  │ Camera is now on...                              │ ║
║  │                  (Altura reducida)               │ ║
║  ╚──────────────────────────────────────────────────╝ ║
║                                                        ║
║  ⌨️  Comando                                           ║
║  ┌──────────────────────────────────────────────────┐ ║
║  │ turn-off-camera                                  │ ║
║  └──────────────────────────────────────────────────┘ ║
║                                                        ║
║  [▶ Enviar] [🗑️  Limpiar]                             ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
```

## Cambios Implementados

### 1. **gui_window.py**
- ✅ Rediseñado con `PanedWindow` vertical para dividir la pantalla
- ✅ Panel superior (70%) para video/contenido
- ✅ Panel inferior (30%) para consola y entrada
- ✅ Divisor redimensionable entre paneles
- ✅ Agregados métodos:
  - `display_camera_frame(frame: np.ndarray)` - Muestra frames de OpenCV
  - `clear_camera_display()` - Limpia la pantalla de cámara
- ✅ Canvas dedicado para mostrar video

### 2. **gui_adapter.py**
- ✅ Agregados métodos:
  - `display_camera_frame(frame: np.ndarray)` - Envía frames al GUI
  - `clear_camera_display()` - Limpia la pantalla

### 3. **opencv_camera_adapter.py**
- ✅ Implementado sistema de callbacks
- ✅ Agregado método `set_frame_callback(callback)` 
- ✅ Frames se envían a través del callback al GUI
- ✅ Fallback a ventana si no hay callback configurado
- ✅ Cambio de índice de cámara: `1 → 0` (valor estándar)

### 4. **camera_ports.py**
- ✅ Agregado método abstracto `set_frame_callback()`
- ✅ Soporte para callbacks de frames

### 5. **container.py**
- ✅ Refactorizado `build_gui_adapter()` 
- ✅ Conexión automática de cámara → GUI mediante callbacks
- ✅ Ya no reutiliza `build_assistant()`, evita duplicaciones

## Características

- 📺 **Stream de cámara en tiempo real** en el panel principal
- 📋 **Consola siempre visible** para ver logs y comandos
- 🔄 **Divisor redimensionable** para ajustar proporción
- 🎨 **Tema oscuro** mantenido en toda la interfaz
- 🚀 **Carga de frames eficiente** con PIL/Pillow
- 💾 **Futura expansión** - Espacio listo para más widgets

## Cómo Usar

```bash
# Ejecutar el GUI
python src/adapters/inbound/gui_main.py

# En el GUI, escribir:
turn-on-camera    # Inicia el stream en el panel principal
turn-off-camera   # Detiene el stream
```

## Notas Técnicas

- Los frames se convierten de BGR (OpenCV) a RGB (PIL)
- Las imágenes se redimensionan manteniendo aspecto
- El placeholder "Esperando stream..." se muestra cuando la cámara no está activa
- Los imports de PIL/Pillow y numpy están disponibles en requirements.txt
