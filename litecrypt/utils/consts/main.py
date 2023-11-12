from dataclasses import dataclass


@dataclass
class Size:
    UNIT: str = "bytes"
    IV: int = 16
    SALT: int = 16
    PEPPER: int = 16
    BLOCK: int = 16 * 8  # 128-bit block size
    MAIN_KEY: int = 32
    AES_KEY: int = 32
    HMAC: int = 32
    MIN_ITERATIONS: int = 50
    MAX_ITERATIONS: int = 10**6

    class StructPack:
        FOR_ITERATIONS: int = 4
        FOR_KDF_SIGNATURE: int = 4


@dataclass
class UseKDF:
    SLOW: int = 0
    FAST: int = 1


@dataclass
class Gui:
    THEME: str = "vapor"
    TITLE: str = "Litecrypt"
    DIMENSIONS: str = "1500x800"


@dataclass
class Colors:
    RED: str = "\033[91m"
    GREEN: str = "\033[92m"
    YELLOW: str = "\033[93m"
    BLUE: str = "\033[94m"
    MAGENTA: str = "\033[95m"
    CYAN: str = "\033[96m"
    BROWN: str = "\033[33;1m"
    RESET: str = "\033[0m"
