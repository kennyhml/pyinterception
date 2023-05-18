class InterceptionNotInstalled(Exception):
    """Raised when the interception driver is not installed."""


class InvalidKeyRequested(LookupError):
    """Raised when attemping to press a key that doesnt exist"""

    def __init__(self, key: str) -> None:
        self.key = key

    def __str__(self) -> str:
        return f"Unsupported key requested: {self.key}"
    
class InvalidMouseButtonRequested(LookupError):
    """Raised when attemping to press a mouse button that doesnt exist"""

    def __init__(self, button: str) -> None:
        self.button = button

    def __str__(self) -> str:
        return f"Unsupported button requested: {self.button}"