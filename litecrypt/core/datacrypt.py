"""This module is used to encrypt and decrypt data."""

import secrets
import string
from dataclasses import dataclass, field
from typing import Optional, Union

from litecrypt.core.base import DecBase, EncBase
from litecrypt.utils import exceptions
from litecrypt.utils.consts import Size


@dataclass
class Crypt:
    """
    Class to encrypt & decrypt data of type bytes or str.

    :param:
        dat (str, bytes): The data to be encrypted/decrypted.
        key (str): The encryption/decryption key.
    """

    data: Union[str, bytes] = field()
    key: str = field()
    intensive_compute: bool = field(default=False)
    iteration_rounds: int = field(default=Size.MIN_ITERATIONS)

    def __post_init__(self) -> None:
        """
        Initialize the Crypt object and verify the provided key.

        Raises:
            exceptions.dynamic.KeyLengthError: If the provided key is invalid.
        """
        if self.key_verify(self.key) != 1:
            raise exceptions.dynamic.KeyLengthError()

    @staticmethod
    def key_verify(key: str) -> int:
        """
        Verify if a given key is valid for usage.

        This function checks whether a given key is valid by attempting
         to convert it from hexadecimal
        representation and ensuring its length is the required 32 bytes.

        Args:
            key (str): The key to be verified.

        Returns:
            int: 1 if the key is valid, 0 if the key is valid but doesn't meet
             length requirements,
            or -1 if the key is not valid.
        """
        try:
            a = bytes.fromhex(key.strip())
            return 1 if len(a) == 32 else 0
        except ValueError:
            return -1

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
                ins = EncBase(
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
                dec_instance = DecBase(message=self.data, mainkey=self.key)
                return (
                    dec_instance.decrypt(get_bytes=True)
                    if get_bytes
                    else dec_instance.decrypt()
                )
            except BaseException as exc:
                raise exceptions.fixed.CryptError() from exc
        raise exceptions.fixed.EmptyContentError()


def gen_ref(n: int = 6) -> str:
    """
    generates a random key reference value using a combination of letters,
    digits, and special characters. The length of the reference can be specified using
    the 'n' parameter.

    Example:
        #-rs&u!

    Args:
        n (int, optional): The length of the key reference value. Default is 6.

    Returns:
        str: The generated key reference value containing a mix of characters.



    """
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
    """
    This function generates a random encryption key in the form of a hex string.
    The key can be used for various cryptographic purposes.

    Returns:
        str: A random 256-bit encryption key as a hex string.
    """
    return EncBase.gen_key()
