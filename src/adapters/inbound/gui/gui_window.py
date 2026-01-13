import tkinter as tk
from tkinter import scrolledtext
from typing import Callable, Optional


class MessageType:
    """Tipos de mensajes para la consola."""
    USER_INPUT = "user_input"
    RESPONSE = "response"
    ERROR = "error"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"


class GUIWindow:
    """
    Interfaz gráfica moderna con tema oscuro.
    Proporciona una consola para escribir comandos y mostrar respuestas.
    """

    # Colores del tema oscuro
    BG_PRIMARY = "#1e1e1e"
    BG_SECONDARY = "#2d2d2d"
    FG_TEXT = "#e0e0e0"
    FG_ACCENT = "#64b5f6"
    
    COLOR_USER = "#a1d595"      # Verde claro para entrada del usuario
    COLOR_RESPONSE = "#64b5f6"  # Azul para respuestas
    COLOR_ERROR = "#ff6b6b"     # Rojo para errores
    COLOR_INFO = "#ffd93d"      # Amarillo para info
    COLOR_SUCCESS = "#6bcf7f"   # Verde para éxito
    COLOR_WARNING = "#ff9f00"   # Naranja para advertencias

    def __init__(
        self,
        title: str = "Raspberry Friend",
        width: int = 900,
        height: int = 700,
        on_command: Optional[Callable[[str], None]] = None,
    ):
        """
        Inicializa la ventana GUI con tema oscuro.

        Args:
            title: Título de la ventana
            width: Ancho de la ventana en píxeles
            height: Alto de la ventana en píxeles
            on_command: Callback cuando se ejecuta un comando
        """
        self.on_command = on_command
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg=self.BG_PRIMARY)
        
        # Iconografía y estilo
        self.root.configure(bg=self.BG_PRIMARY)
        
        self._setup_styles()
        self._setup_ui()

    def _setup_styles(self) -> None:
        """Configura estilos globales."""
        self.root.option_add("*Background", self.BG_PRIMARY)
        self.root.option_add("*Foreground", self.FG_TEXT)

    def _setup_ui(self) -> None:
        """Construye la interfaz de usuario."""
        # Header
        header_frame = tk.Frame(self.root, bg=self.BG_SECONDARY, height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🤖 Raspberry Friend Console",
            font=("Arial", 16, "bold"),
            bg=self.BG_SECONDARY,
            fg=self.FG_ACCENT,
        )
        title_label.pack(pady=10)

        # Separador
        separator = tk.Frame(self.root, bg=self.FG_ACCENT, height=2)
        separator.pack(fill=tk.X)

        # Frame principal con padding
        main_frame = tk.Frame(self.root, bg=self.BG_PRIMARY)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Sección de salida (consola)
        output_frame = tk.Frame(main_frame, bg=self.BG_PRIMARY)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        output_label = tk.Label(
            output_frame,
            text="📋 Consola",
            font=("Arial", 11, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_ACCENT,
        )
        output_label.pack(anchor=tk.W, pady=(0, 8))

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=("Courier New", 10),
            state=tk.DISABLED,
            height=18,
            bg=self.BG_SECONDARY,
            fg=self.FG_TEXT,
            insertbackground=self.FG_ACCENT,
            selectbackground=self.FG_ACCENT,
            selectforeground=self.BG_SECONDARY,
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Configurar tags para colores
        self._configure_text_tags()

        # Sección de entrada
        input_frame = tk.Frame(main_frame, bg=self.BG_PRIMARY)
        input_frame.pack(fill=tk.X, pady=(0, 12))

        input_label = tk.Label(
            input_frame,
            text="⌨️  Comando",
            font=("Arial", 11, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_ACCENT,
        )
        input_label.pack(anchor=tk.W, pady=(0, 6))

        self.input_text = tk.Entry(
            input_frame,
            font=("Courier New", 11),
            bg=self.BG_SECONDARY,
            fg=self.FG_TEXT,
            insertbackground=self.FG_ACCENT,
            relief=tk.FLAT,
            bd=1,
        )
        self.input_text.pack(fill=tk.X, ipady=8)
        self.input_text.bind("<Return>", self._on_enter_pressed)

        # Frame para botones
        button_frame = tk.Frame(main_frame, bg=self.BG_PRIMARY)
        button_frame.pack(fill=tk.X, pady=(0, 0))

        self.send_button = tk.Button(
            button_frame,
            text="▶ Enviar",
            command=self._on_send_clicked,
            bg=self.FG_ACCENT,
            fg=self.BG_PRIMARY,
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
        )
        self.send_button.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_button = tk.Button(
            button_frame,
            text="🗑️  Limpiar",
            command=self._clear_output,
            bg=self.BG_SECONDARY,
            fg=self.FG_TEXT,
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
        )
        self.clear_button.pack(side=tk.LEFT)

    def _configure_text_tags(self) -> None:
        """Configura los tags de colores para diferentes tipos de mensajes."""
        self.output_text.tag_configure(MessageType.USER_INPUT, foreground=self.COLOR_USER, font=("Courier New", 10, "bold"))
        self.output_text.tag_configure(MessageType.RESPONSE, foreground=self.COLOR_RESPONSE)
        self.output_text.tag_configure(MessageType.ERROR, foreground=self.COLOR_ERROR, font=("Courier New", 10, "bold"))
        self.output_text.tag_configure(MessageType.INFO, foreground=self.COLOR_INFO)
        self.output_text.tag_configure(MessageType.SUCCESS, foreground=self.COLOR_SUCCESS, font=("Courier New", 10, "bold"))
        self.output_text.tag_configure(MessageType.WARNING, foreground=self.COLOR_WARNING)

    def _on_enter_pressed(self, event) -> None:
        """Maneja cuando se presiona Enter en el campo de entrada."""
        self._on_send_clicked()

    def _on_send_clicked(self) -> None:
        """Maneja el click del botón enviar."""
        command = self.input_text.get().strip()
        if command:
            self.add_output(f"> {command}", MessageType.USER_INPUT)
            self.input_text.delete(0, tk.END)
            self.input_text.focus()
            if self.on_command:
                self.on_command(command)

    def add_output(self, message: str, message_type: str = MessageType.RESPONSE) -> None:
        """
        Añade un mensaje a la consola de salida con tipo.

        Args:
            message: Mensaje a mostrar
            message_type: Tipo de mensaje para colorear
        """
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n", message_type)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def _clear_output(self) -> None:
        """Limpia la consola de salida."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def clear_output(self) -> None:
        """Limpia la consola (método público para el presenter)."""
        self._clear_output()

    def set_on_command_callback(self, callback: Callable[[str], None]) -> None:
        """
        Establece el callback para cuando se ejecuta un comando.

        Args:
            callback: Función a ejecutar cuando se envía un comando
        """
        self.on_command = callback

    def run(self) -> None:
        """Inicia el loop de la GUI."""
        self.input_text.focus()
        self.root.mainloop()

    def close(self) -> None:
        """Cierra la ventana GUI."""
        self.root.quit()

