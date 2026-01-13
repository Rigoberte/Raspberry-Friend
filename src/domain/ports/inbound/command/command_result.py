class CommandResult:
    def __init__(self, success: bool, message: str):
        self._success = success
        self._message = message

    def is_successful(self) -> bool:
        return bool(self._success)
    
    def get_message(self) -> str:
        return str(self._message)