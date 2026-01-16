import tkinter as tk
from tkinter import scrolledtext
from typing import Callable, Optional
from PIL import Image, ImageTk
import numpy as np


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
        self.on_listen = None  # Callback para comandos por voz
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg=self.BG_PRIMARY)
        
        # Iconografía y estilo
        self.root.configure(bg=self.BG_PRIMARY)
        
        # Configurar cierre de ventana para terminar la aplicación
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
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

        # Frame principal con PanedWindow para separar cámara y consola
        paned_window = tk.PanedWindow(
            self.root,
            orient=tk.VERTICAL,
            bg=self.BG_PRIMARY,
            sashwidth=8,
            relief=tk.FLAT,
            borderwidth=0
        )
        paned_window.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # === Panel Superior: Cámara/Contenido ===
        camera_frame = tk.Frame(paned_window, bg=self.BG_PRIMARY)
        paned_window.add(camera_frame, stretch='always')

        camera_label = tk.Label(
            camera_frame,
            text="📹 Vista en Vivo",
            font=("Arial", 11, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_ACCENT,
        )
        camera_label.pack(anchor=tk.W, padx=15, pady=(15, 8))

        # Canvas para mostrar frames de cámara
        self.camera_canvas = tk.Canvas(
            camera_frame,
            bg=self.BG_SECONDARY,
            highlightbackground=self.BG_SECONDARY,
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.camera_canvas.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Placeholder de texto cuando no hay cámara
        self.camera_placeholder = tk.Label(
            self.camera_canvas,
            text="Esperando stream de cámara...",
            font=("Arial", 12),
            bg=self.BG_SECONDARY,
            fg=self.FG_TEXT
        )
        self.camera_placeholder_id = self.camera_canvas.create_window(
            0, 0, window=self.camera_placeholder, anchor=tk.CENTER
        )

        def on_canvas_resize(event):
            """Centra el placeholder cuando se redimensiona el canvas."""
            self.camera_canvas.coords(
                self.camera_placeholder_id,
                event.width // 2,
                event.height // 2
            )

        self.camera_canvas.bind("<Configure>", on_canvas_resize)

        # === Panel Inferior: Consola ===
        console_frame = tk.Frame(paned_window, bg=self.BG_PRIMARY)
        paned_window.add(console_frame, stretch='always')

        console_label = tk.Label(
            console_frame,
            text="📋 Consola",
            font=("Arial", 11, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_ACCENT,
        )
        console_label.pack(anchor=tk.W, padx=15, pady=(15, 8))

        # Sección de salida (consola)
        output_frame = tk.Frame(console_frame, bg=self.BG_PRIMARY)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

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
            font=("Courier New", 9),
            state=tk.DISABLED,
            height=8,
            bg=self.BG_SECONDARY,
            fg=self.FG_TEXT,
            insertbackground=self.FG_ACCENT,
            selectbackground=self.FG_ACCENT,
            selectforeground=self.BG_SECONDARY,
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 12))

        # Configurar tags para colores
        self._configure_text_tags()

        # Sección de entrada (ahora dentro del console_frame)
        input_frame = tk.Frame(console_frame, bg=self.BG_PRIMARY)
        input_frame.pack(fill=tk.X, padx=15, pady=(0, 0))

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
            font=("Courier New", 10),
            bg=self.BG_SECONDARY,
            fg=self.FG_TEXT,
            insertbackground=self.FG_ACCENT,
            relief=tk.FLAT,
            bd=1,
        )
        self.input_text.pack(fill=tk.X, ipady=6)
        self.input_text.bind("<Return>", self._on_enter_pressed)

        # Frame para botones (dentro de console_frame)
        button_frame = tk.Frame(console_frame, bg=self.BG_PRIMARY)
        button_frame.pack(fill=tk.X, padx=15, pady=(12, 15))

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

        self.listen_button = tk.Button(
            button_frame,
            text="🎤 Escuchar",
            command=self._on_listen_clicked,
            bg="#9b59b6",  # Color púrpura para distinguir
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
        )
        self.listen_button.pack(side=tk.LEFT, padx=(0, 10))

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

    def _on_listen_clicked(self) -> None:
        """Maneja el click del botón escuchar."""
        if self.on_listen:
            self.add_output("🎤 Escuchando...", MessageType.INFO)
            # Deshabilitar botón mientras escucha
            self.listen_button.config(state=tk.DISABLED, text="⏺️ Grabando...")
            self.root.update()
            
            # Ejecutar callback en thread para no bloquear UI
            import threading
            def listen_thread():
                try:
                    self.on_listen()
                finally:
                    # Re-habilitar botón
                    self.root.after(0, lambda: self.listen_button.config(
                        state=tk.NORMAL, 
                        text="🎤 Escuchar"
                    ))
            
            thread = threading.Thread(target=listen_thread, daemon=True)
            thread.start()
        else:
            self.add_output("⚠️ Comandos por voz no configurados", MessageType.WARNING)

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
    
    def _on_closing(self) -> None:
        """Maneja el evento de cierre de ventana."""
        import sys
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

    def display_camera_frame(self, frame: np.ndarray) -> None:
        """
        Muestra un frame de cámara (array de numpy) en el canvas.

        Args:
            frame: Array numpy con formato BGR (OpenCV) o RGB
        """
        try:
            # Convertir BGR a RGB si es necesario
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # Asumir BGR de OpenCV y convertir a RGB
                import cv2
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = frame

            # Convertir numpy array a PIL Image
            image = Image.fromarray(frame_rgb)
            
            # Redimensionar la imagen al tamaño del canvas manteniendo aspecto
            canvas_width = self.camera_canvas.winfo_width()
            canvas_height = self.camera_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:  # Evitar valores inválidos
                image.thumbnail((canvas_width - 30, canvas_height - 30), Image.Resampling.LANCZOS)
                
                # Convertir a PhotoImage
                self.camera_photo = ImageTk.PhotoImage(image)
                
                # Ocultar placeholder en la primera actualización
                if hasattr(self, 'camera_placeholder') and hasattr(self, 'camera_placeholder_id'):
                    try:
                        self.camera_canvas.itemconfig(self.camera_placeholder_id, state='hidden')
                    except:
                        pass
                
                # Actualizar o crear la imagen en el canvas (sin borrar todo)
                if not hasattr(self, 'camera_image_id'):
                    # Primera vez: crear la imagen
                    self.camera_image_id = self.camera_canvas.create_image(
                        canvas_width // 2,
                        canvas_height // 2,
                        image=self.camera_photo
                    )
                else:
                    # Actualizaciones posteriores: solo cambiar la imagen
                    self.camera_canvas.coords(
                        self.camera_image_id,
                        canvas_width // 2,
                        canvas_height // 2
                    )
                    self.camera_canvas.itemconfig(self.camera_image_id, image=self.camera_photo)
        except Exception as e:
            self.add_output(f"Error al mostrar frame de cámara: {str(e)}", MessageType.ERROR)

    def clear_camera_display(self) -> None:
        """Limpia la pantalla de cámara y muestra el placeholder."""
        try:
            # Eliminar la imagen de la cámara si existe
            if hasattr(self, 'camera_image_id'):
                self.camera_canvas.delete(self.camera_image_id)
                delattr(self, 'camera_image_id')
            
            # Mostrar el placeholder nuevamente
            if hasattr(self, 'camera_placeholder') and hasattr(self, 'camera_placeholder_id'):
                try:
                    self.camera_canvas.itemconfig(self.camera_placeholder_id, state='normal')
                except:
                    # Si el placeholder fue eliminado, recrearlo
                    self.camera_placeholder_id = self.camera_canvas.create_window(
                        self.camera_canvas.winfo_width() // 2,
                        self.camera_canvas.winfo_height() // 2,
                        window=self.camera_placeholder,
                        anchor=tk.CENTER
                    )
        except Exception as e:
            self.add_output(f"Error al limpiar pantalla de cámara: {str(e)}", MessageType.ERROR)

    def run(self) -> None:
        """Inicia el loop de la GUI."""
        self.input_text.focus()
        self.root.mainloop()

    def close(self) -> None:
        """Cierra la ventana GUI."""
        self.root.quit()