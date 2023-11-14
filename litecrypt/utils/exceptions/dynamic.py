from litecrypt.utils.consts import Size


class IterationsOutofRangeError(Exception):
    def __init__(self, num: int) -> None:
        self.display = (
            f"Iterations must be between {Size.MIN_ITERATIONS} and "
            f"{Size.MAX_ITERATIONS}."
            f" RECEIVED : {num}"
        )
        super().__init__(self.display)


class KeyLengthError(Exception):
    def __init__(self) -> None:
        self.display = f"Key must be hexadecimal and " f"{Size.MAIN_KEY} bytes long !"
        super().__init__(self.display)
