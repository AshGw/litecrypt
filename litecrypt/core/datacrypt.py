"""This module is used to encrypt and decrypt data."""

from __future__ import annotations

import secrets
import string
from dataclasses import dataclass, field
from enum import Enum, unique, auto
from typing import Optional, Union

from litecrypt.core.crypt import Dec, Enc
from litecrypt.utils import exceptions
from litecrypt.utils.consts import Size


@unique
class KeyCheckResult(Enum):
    BAD_LENGTH = auto()
    VALID_LENGTH = auto()
    NON_CONVERTIBLE_TYPE = auto()


@dataclass
class Crypt:
    data: Union[str, bytes] = field()
    key: str = field()
    intensive_compute: bool = field(default=False)
    iteration_rounds: int = field(default=Size.MIN_ITERATIONS)

    def __post_init__(self) -> None:
        if self.key_verify(self.key) != KeyCheckResult.VALID_LENGTH:
            raise exceptions.dynamic.KeyLengthError()

    @staticmethod
    def key_verify(key: str) -> KeyCheckResult:
        try:
            a = bytes.fromhex(key.strip())
            return (
                KeyCheckResult.VALID_LENGTH
                if len(a) == Size.AES_KEY
                else KeyCheckResult.BAD_LENGTH
            )
        except ValueError:
            return KeyCheckResult.NON_CONVERTIBLE_TYPE

    def encrypt(self, get_bytes: Optional[bool] = False) -> Union[str, bytes]:
        """
        Encrypt the given content, which can be of type bytes or str.

        Args:
            get_bytes (Optional[bool], optional): Set to True if you want
             to receive the output as bytes.
                Defaults to False.

        Returns:
            Union[bytes, str]: The encrypted content.

        Raises:
            exceptions.fixed.CryptError: If an error occurs during
             the encryption process.
            exceptions.fixed.EmptyContentError: If the content to be encrypted is empty.
        """
        if self.data:
            try:
                ins = Enc(
                    self.data,
                    self.key,
                    iterations=self.iteration_rounds,
                    compute_intensively=self.intensive_compute,
                )
                return ins.encrypt(get_bytes=True) if get_bytes else ins.encrypt()
            except BaseException as exc:
                raise exceptions.fixed.CryptError() from exc
        raise exceptions.fixed.EmptyContentError()

    def decrypt(self, get_bytes: Optional[bool] = False) -> Union[str, bytes]:
        """
        Decrypt the given content, which can be of type bytes or str.

        Args:
            get_bytes (Optional[bool], optional): Set to True if you
             want to receive the output as bytes.
                Defaults to False.

        Returns:
            Union[bytes, str]: The decrypted content.

        Raises:
            exceptions.fixed.CryptError: If an error occurs during
             the decryption process.
            exceptions.fixed.EmptyContentError: If the content to be decrypted is empty.
        """
        if self.data:
            try:
                dec_instance = Dec(message=self.data, mainkey=self.key)
                return (
                    dec_instance.decrypt(get_bytes=True)
                    if get_bytes
                    else dec_instance.decrypt()
                )
            except BaseException as exc:
                raise exceptions.fixed.CryptError() from exc
        raise exceptions.fixed.EmptyContentError()


def gen_ref(n: int = 6) -> str:
    ref = "#"
    for _ in range(n):
        character = secrets.choice(
            string.ascii_letters
            + string.digits
            + "$"
            + "?"
            + "&"
            + "@"
            + "!"
            + "-"
            + "+"
        )
        ref += character
    return ref


def gen_key() -> str:
    return Enc.gen_key()
