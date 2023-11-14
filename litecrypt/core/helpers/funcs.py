import base64
import hashlib
import os
import bcrypt

import litecrypt.utils.exceptions as exceptions

from litecrypt.utils.consts import Size
from typing import Tuple, Union


def parse_message(message: Union[str, bytes]) -> bytes:
    msg = message.strip()
    if isinstance(message, str):
        msg = message.encode()
    return msg


def parse_encrypted_message(message: Union[str, bytes]) -> bytes:
    if isinstance(message, str):
        return base64.urlsafe_b64decode(message.encode("UTF-8"))
    elif isinstance(message, bytes):
        return message


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


def blazingly_fast_KDF(key: str, salt: bytes) -> bytes:
    """
        Fast key derivation function.
        Args:
            key (bytes): 256-bit key.
            salt (bytes): 128-bit salt

        Returns:
            bytes: Derived 256-bit  key.
    """
    use_key = key.encode("UTF-8")
    key_material = use_key + salt
    derived_key = hashlib.sha256(key_material).digest()
    return derived_key


def use_KDF(
    *, compute_intensively: bool, key: str, salt_pepper: bytes, iterations: int
) -> bytes:
    if compute_intensively:
        return intensive_KDF(
            mainkey=key, salt_pepper=salt_pepper, iterations=iterations
        )
    return blazingly_fast_KDF(key=key, salt=salt_pepper)
