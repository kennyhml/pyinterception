class DriverNotFoundError(Exception):
    """Raised when the interception driver is not installed / found."""

    def __str__(self) -> str:
        return (
            "Interception driver was not found or is not installed.\n"
            "Please confirm that it has been installed properly and is added to PATH."
        )


class UnknownKeyError(LookupError):
    """Raised when attemping to press a key that doesnt exist"""

    def __init__(self, key: str) -> None:
        self.key = key

    def __str__(self) -> str:
        return (
            f"Unknown key requested: {self.key}.\n"
            "Consider running 'pyinterception show_supported_keys' for a list of all supported keys."
        )


class UnknownButtonError(LookupError):
    """Raised when attemping to press a mouse button that doesnt exist"""

    def __init__(self, button: str) -> None:
        self.button = button

    def __str__(self) -> str:
        return (
            f"Unknown button requested: {self.button}.\n"
            "Consider running 'pyinterception show_supported_buttons' for a list of all supported buttons."
        )
