import hashlib
import os
import struct
from typing import Tuple

import bcrypt

import litecrypt.utils.exceptions as exceptions
from litecrypt.utils.consts import Size, UseKDF


def parse_message(message: str | bytes) -> bytes:
    msg = message
    if isinstance(message, str):
        msg = message.encode()
    return msg


def cipher_randomizers() -> Tuple[bytes, bytes, bytes]:
    iv = os.urandom(Size.IV)
    salt = os.urandom(Size.SALT)
    pepper = os.urandom(Size.PEPPER)
    return iv, salt, pepper


def check_iterations(iterations: int) -> None:
    if iterations < Size.MIN_ITERATIONS or iterations > Size.MAX_ITERATIONS:
        raise exceptions.dynamic.IterationsOutofRangeError(iterations)


def intensive_KDF(mainkey: str, salt_pepper: bytes, iterations: int) -> bytes:
    """
    AES Key & HMAC derivation function.

    This method derives encryption and HMAC keys using the specified main key,
    salt or pepper, and
    the number of iterations.

    Args:
    mainkey (str): The main encryption key.
    salt_pepper (bytes): The salt or pepper for key derivation.
    iterations (int): The number of iterations for key derivation.

    Returns:
    bytes: The derived key bytes.
    """
    return bcrypt.kdf(
        password=mainkey.encode("UTF-8"),
        salt=salt_pepper,
        desired_key_bytes=Size.AES_KEY,
        rounds=iterations,
    )


def blazingly_fast_KDF(key: bytes, salt: bytes) -> bytes:
    """
    Fast key derivation function.
    Args:
        key (bytes): 256-bit key.
        salt (bytes): 128-bit salt

    Returns:
        bytes: Derived 256-bit  key.
    """
    if len(key) != 32:
        raise ValueError("Key must be 256 bits (32 bytes) long.")
    key_material = key + salt
    derived_key = hashlib.sha256(key_material).digest()
    return derived_key


def signtature_KDF_bytes(compute_intensive: bool) -> bytes:
    """
    Pack the number of iterations into bytes using the 'big-endian' format.

    Returns:
    bytes: The packed bytes representing the number of iterations.
    """
    KDF_singnature = UseKDF.FAST
    if compute_intensive:
        KDF_singnature = UseKDF.SLOW

    signature_bytes = struct.pack("!I", KDF_singnature)
    return signature_bytes
