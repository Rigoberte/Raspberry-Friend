"""
Script de demostración del nuevo GUI con soporte de cámara.
Muestra cómo se integra el stream de cámara en la ventana principal.
"""

import sys
from pathlib import Path

# Agregar el directorio al path
sys.path.insert(0, str(Path(__file__).parent))

from src.adapters.container import build_gui_adapter


def main():
    """Ejecuta el GUI con la nueva estructura."""
    print("Inicializando Raspberry Friend con nuevo layout...")
    print("")
    print("Características nuevas:")
    print("  ✅ Panel grande superior para streaming de cámara")
    print("  ✅ Consola reducida inferior para logs")
    print("  ✅ Divisor redimensionable entre paneles")
    print("")
    print("Comandos para probar:")
    print("  1. Escribe: turn-on-camera")
    print("  2. Verás el stream en el panel superior")
    print("  3. Escribe: turn-off-camera para detener")
    print("")
    print("=" * 60)
    print("")
    
    # Crear el GUI con dimensiones apropiadas
    gui_adapter = build_gui_adapter(
        title="🤖 Raspberry Friend - Nuevo Layout",
        width=1000,      # Ancho aumentado para mejor visualización
        height=800,      # Alto aumentado
    )
    
    # Mostrar mensaje de bienvenida
    gui_adapter.display_message("Bienvenido al nuevo Raspberry Friend", "info")
    gui_adapter.display_message("Panel superior: Cámara/Contenido (70%)", "info")
    gui_adapter.display_message("Panel inferior: Consola (30%)", "info")
    gui_adapter.display_message("Intenta con: turn-on-camera", "info")
    
    # Iniciar el loop
    gui_adapter.run()


if __name__ == "__main__":
    main()
