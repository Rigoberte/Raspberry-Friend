"""
Punto de entrada para la interfaz gráfica (GUI).
Ejecuta el asistente con la nueva interfaz gráfica desacoplada.
El CLI tradicional se mantiene disponible en cli.py
"""

from src.adapters.container import build_gui_adapter

def main():
    print("Inicializando Raspberry Friend...")
    max_workers = 4

    gui_adapter = build_gui_adapter(
        max_workers=max_workers,
        title="🤖 Raspberry Friend",
        width=900,
        height=700,
    )
    
    # Iniciar el loop de la GUI (bloqueante)
    gui_adapter.run()


if __name__ == "__main__":
    main()
