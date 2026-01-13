"""
Punto de entrada para la interfaz gráfica (GUI).
Ejecuta el asistente con la nueva interfaz gráfica desacoplada.
El CLI tradicional se mantiene disponible en cli.py
"""

from src.adapters.container import build_gui_adapter
from src.application.events.event_bus import InMemoryEventBus


def main():
    print("Inicializando Raspberry Friend...")
    
    # Crear event bus para capturar eventos
    events_bus = InMemoryEventBus()
    
    # Construir adaptador GUI con event bus
    gui_adapter = build_gui_adapter(
        event_bus=events_bus,
        title="🤖 Raspberry Friend",
        width=900,
        height=700,
    )
    
    gui_adapter.display_message("Bienvenido a Raspberry Friend", "info")
    gui_adapter.display_message("Escribe un comando para comenzar (ej: 'echo Hola')", "info")
    print("¡GUI iniciada! Esperando comandos...")
    
    # Iniciar el loop de la GUI (bloqueante)
    gui_adapter.run()


if __name__ == "__main__":
    main()
