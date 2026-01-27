"""
Servicio de aplicación para parsear entrada de usuario en comandos.
Separación de responsabilidades: parsing vs ejecución.
"""
from src.domain.models.command import Command


class CommandParser:
    """
    Parser que convierte texto de usuario en objetos Command.
    Maneja diferentes formatos de entrada.
    """
    
    def parse(self, user_input: str) -> Command:
        """
        Parsea la entrada del usuario y crea un comando.
        
        Args:
            user_input: Texto ingresado por el usuario
            
        Returns:
            Objeto Command parseado
            
        Raises:
            ValueError: Si la entrada es inválida
        """
        if not user_input or not user_input.strip():
            raise ValueError("La entrada no puede estar vacía")
        
        user_input = user_input.strip()
        parts = user_input.split(maxsplit=1)
        
        command_name = parts[0]
        args = {"text": parts[1]} if len(parts) > 1 else {}
        
        return Command(command_name, args)
    
    def parse_with_args(self, user_input: str) -> tuple[str, dict[str, str]]:
        """
        Parsea la entrada y retorna nombre y argumentos por separado.
        
        Args:
            user_input: Texto ingresado por el usuario
            
        Returns:
            Tupla (nombre_comando, diccionario_args)
        """
        command = self.parse(user_input)
        return command.get_name(), command.get_args()
