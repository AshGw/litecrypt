"""This module provides classes and functions for AES-256 encryption and decryption"""

from __future__ import annotations

from base64 import urlsafe_b64encode
from os import urandom
from struct import pack
from typing import Optional, Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.ciphers import Cipher, CipherContext, algorithms, modes

from litecrypt.core._base import DecBase, EncBase
from litecrypt.utils.consts import Size, UseKDF

DEFAULT_INTENSIVE_COMPUTE = False


class Enc(EncBase):
    def __init__(
        self,
        message: Union[str, bytes],
        mainkey: str,
        *,
        iterations: int = Size.MIN_ITERATIONS,
        compute_intensively: bool = DEFAULT_INTENSIVE_COMPUTE,
    ) -> None:
        super().__init__(
            message=message,
            mainkey=mainkey,
            iterations=iterations,
            compute_intensively=compute_intensively,
        )

    @staticmethod
    def gen_key(desired_bytes: int = Size.AES_KEY) -> str:
        if desired_bytes < Size.AES_KEY:
            raise ValueError(
                f"desired_bytes must be greater than or equal to {Size.AES_KEY}"
            )
        key = urandom(desired_bytes)
        return key.hex()

    def _mode(self) -> modes.CBC:
        return modes.CBC(self.iv)

    def _cipher(self) -> Cipher[modes.CBC]:
        return Cipher(
            algorithms.AES(key=self.enc_key),
            mode=self._mode(),
            backend=default_backend(),
        )

    def _cipher_encryptor(self) -> CipherContext:
        return self._cipher().encryptor()

    def _padded_message(self) -> bytes:
        padder = padding.PKCS7(Size.BLOCK).padder()
        return padder.update(self.message) + padder.finalize()

    def _ciphertext(self) -> bytes:
        return (
            self._cipher_encryptor().update(self._padded_message())
            + self._cipher_encryptor().finalize()
        )

    def _iterations_bytes(self) -> bytes:
        iters_bytes = pack("!I", self.iterations)
        return iters_bytes

    def _signtature_KDF_bytes(self) -> bytes:
        KDF_method = UseKDF.FAST
        if self.compute_intensively is True:
            KDF_method = UseKDF.SLOW
        signature_bytes = pack("!I", KDF_method)

        return signature_bytes

    def _hmac_final(self) -> bytes:
        hmac_ = hmac.HMAC(self.hmac_key, hashes.SHA256())
        hmac_.update(
            self.iv
            + self.salt
            + self.pepper
            + self._iterations_bytes()
            + self._signtature_KDF_bytes()
            + self._ciphertext()
        )
        return hmac_.finalize()

    def encrypt(self, get_bytes: Optional[bool] = False) -> Union[bytes, str]:
        """
        Returns the encrypted data as bytes in the format 'HMAC' -> 'IV'
        -> 'Salt value' -> 'pepper value' -> 'iterations' -> 'KDF identifier'
         -> 'ciphertext'.
        Or as a URL safe base64 encoded string of the encrypted bytes' data.

        :param get_bytes: Set to True to get the encrypted data as bytes.
         Default is False.
        :return: Encrypted data as bytes or URL safe base64 encoded string.
        """
        raw = (
            self._hmac_final()
            + self.iv
            + self.salt
            + self.pepper
            + self._iterations_bytes()
            + self._signtature_KDF_bytes()
            + self._ciphertext()
        )
        return raw if get_bytes else urlsafe_b64encode(raw).decode("UTF-8")


class Dec(DecBase):
    def __init__(self, message: Union[str, bytes], mainkey: str) -> None:
        super().__init__(message=message, mainkey=mainkey)

    def _mode(self) -> modes.CBC:
        return modes.CBC(self.rec_iv)

    def _cipher(self) -> Cipher[modes.CBC]:
        return Cipher(
            algorithms.AES(key=self.dec_key),
            mode=self._mode(),
            backend=default_backend(),
        )

    def _cipher_decryptor(self) -> CipherContext:
        return self._cipher().decryptor()

    def _pre_unpadding(self) -> bytes:
        return (
            self._cipher_decryptor().update(self.rec_ciphertext)
            + self._cipher_decryptor().finalize()
        )

    def _unpadded_message(self) -> bytes:
        unpadder = padding.PKCS7(Size.BLOCK).unpadder()
        return unpadder.update(self._pre_unpadding()) + unpadder.finalize()

    def decrypt(self, get_bytes: Optional[bool] = False) -> Union[bytes, str]:
        """
        Returns the decrypted data as bytes if 'get_bytes' is set to True.
        Or as a URL safe base64 encoded string of the decrypted bytes data,
        which is the default return value.

        :param get_bytes: Set to True to get the decrypted data as bytes.
         Default is False.
        :return: Decrypted data as bytes or URL safe base64 encoded string.
        """
        raw = self._unpadded_message()
        return raw if get_bytes else raw.decode("UTF-8")
