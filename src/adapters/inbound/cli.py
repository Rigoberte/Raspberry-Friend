import sys
import pathlib
import colorama
import time
import threading
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from src.infrastructure.container import build_assistant
from src.domain.models.command import Command

def main():
    assistant = build_assistant()
    print("Welcome to Raspberry-Friend CLI! Type 'exit' to quit.")

    _progress_stop = threading.Event()
    _progress_thread: threading.Thread | None = None
    
    session = PromptSession()
    
    while True:
        with patch_stdout():
            user_input = session.prompt("> ").strip().lower()
        
        if user_input in ("exit", "quit"):
            break
        
        if not user_input:
            continue
        
        # Parsear: primera palabra = comando, resto = args
        parts = user_input.split(maxsplit=1)
        name = parts[0]
        args = {"text": parts[1]} if len(parts) > 1 else {}
        
        command = Command(name, args)
        result = assistant.handle_command(command)
        print(result.get_message())

        """
        if command.get_name() == "play-song" and result.metadata:
            _progress_stop.clear()
            _progress_thread = threading.Thread(
                target=__show_progress_bar__,
                args=(result.metadata["duration"]),
                daemon=True
            )
            _progress_thread.start()
        else:
            print(result.get_message())

    def __show_progress_bar__(audio_total_length: int) -> str:
        bar_length = 30
        current_song = ""
        while not _progress_stop.is_set():
            if current_song != service.current_song():
                try:
                    current_song = service.current_song()
                except Exception:
                    return "No song is currently playing"

            pos_ms = 1 #self.__get_pos__()
            current_length = pos_ms / 1000.0
            filled_length = int(bar_length * current_length // audio_total_length)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            time_text = f"{__format_time__(current_length)} / {__format_time__(audio_total_length)}"

            out = sys.__stdout__  # stdout real (no el wrap de prompt_toolkit)

            #if last line starts with |, overwrite it
            out.write("\033[s")       # save cursor
            out.write("\033[1A")  # up 1 line
            out.write("\r\033[2K")    # clear line
            out.write(f"|{bar}| {time_text}")
            out.write("\033[u")       # restore cursor (vuelve al prompt)
            out.flush()

            time.sleep(1)

        _progress_stop.clear()

        return ""
        """

    def __format_time__(self, seconds: int) -> str:
        """
        Formats seconds into MM:SS format.
        """
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

if __name__ == "__main__":
    sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
    colorama.just_fix_windows_console()
    main()