from dataclasses import dataclass
from typing import Final


@dataclass
class Size:
    UNIT: Final = "bytes"
    IV: Final = 16
    SALT: Final = 16
    PEPPER: Final = 16
    BLOCK: Final = 16 * 8  # 128-bit block size
    MAIN_KEY: Final = 32
    AES_KEY: Final = 32
    HMAC: Final = 32
    MIN_ITERATIONS: Final = 50
    MAX_ITERATIONS: Final = 10**6

    class StructPack:
        FOR_ITERATIONS: Final = 4
        FOR_KDF_SIGNATURE: Final = 4


@dataclass
class UseKDF:
    SLOW: Final = 0
    FAST: Final = 1


@dataclass
class Gui:
    THEME: Final = "vapor"
    TITLE: Final = "Litecrypt"
    DIMENSIONS: Final = "1500x800"


@dataclass
class Colors:
    RED: Final = "\033[91m"
    GREEN: Final = "\033[92m"
    YELLOW: Final = "\033[93m"
    BLUE: Final = "\033[94m"
    MAGENTA: Final = "\033[95m"
    CYAN: Final = "\033[96m"
    BROWN: Final = "\033[33;1m"
    RESET: Final = "\033[0m"
