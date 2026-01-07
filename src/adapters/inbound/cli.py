import sys
from pathlib import Path
import colorama
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from src.infrastructure.container import build_assistant
from src.domain.models.command import Command

def main():
    assistant = build_assistant()
    print("Welcome to Raspberry-Friend CLI! Type 'exit' to quit.")

    session = PromptSession()
    
    while True:
        with patch_stdout():
            user_input = session.prompt("> ").strip().lower()
        
        if not user_input:
            continue
        
        if user_input in ("exit", "quit"):
            break
        
        # Parsear: primera palabra = comando, resto = args
        parts = user_input.split(maxsplit=1)
        name = parts[0]
        args = {"text": parts[1]} if len(parts) > 1 else {}
        
        command = Command(name, args)
        result = assistant.handle_command(command)
        # TODO: No deberia de imprimirlo. Si no que la pantalla (a parte) deberia de estar 
        # mirando los logs y resultados.
        print(result.get_message())

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent.resolve()))
    colorama.just_fix_windows_console()
    main()