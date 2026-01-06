class CommandResult:
    """Immutable result returned after executing a command."""
    def __init__(self, success: bool, message: str):
        self.success = success
        self.message = message