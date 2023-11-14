"""This module provides classes and functions for AES-256 encryption and decryption"""


import base64
import hmac as hmc
import os
import struct
from typing import Optional, Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    algorithms,
    modes,
    CipherContext
)

from litecrypt.core.helpers.funcs import (check_iterations, cipher_randomizers, parse_encrypted_message,
                                          parse_message, use_KDF)
from litecrypt.utils import exceptions
from litecrypt.utils.consts import Size, UseKDF

DEFAULT_INTENSIVE_COMPUTE = False


class EncBase:
    def __init__(
        self,
        message: Union[str, bytes],
        mainkey: str,
        *,
        iterations: int = Size.MIN_ITERATIONS,
        compute_intensively: bool = DEFAULT_INTENSIVE_COMPUTE,
    ) -> None:
        self.message = parse_message(message)
        self.mainkey = mainkey
        self.compute_intensively = compute_intensively
        self.iterations = iterations

        check_iterations(self.iterations)
        self.key_verify(self.mainkey)

        self.iv, self.salt, self.pepper = cipher_randomizers()

        self.enc_key = use_KDF(
            compute_intensively=compute_intensively,
            key=self.mainkey,
            salt_pepper=self.salt,
            iterations=self.iterations,
        )

        self.hmac_key = use_KDF(
            compute_intensively=compute_intensively,
            key=self.mainkey,
            salt_pepper=self.pepper,
            iterations=self.iterations,
        )

    @staticmethod
    def gen_key(desired_bytes: int = Size.AES_KEY) -> str:
        if desired_bytes < Size.AES_KEY:
            raise ValueError(
                f"desired_bytes must be greater than or equal to {Size.AES_KEY}"
            )
        key = os.urandom(desired_bytes)
        return key.hex()

    @staticmethod
    def key_verify(key: str) -> None:
        if len(bytes.fromhex(key.strip())) < Size.MAIN_KEY:
            raise ValueError(
                f"raw key size must be greater or equal to: {Size.MAIN_KEY} {Size.UNIT}"
            )

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
        iters_bytes = struct.pack("!I", self.iterations)
        return iters_bytes

    def _signtature_KDF_bytes(self) -> bytes:
        KDF_method = UseKDF.FAST
        if self.compute_intensively is True:
            KDF_method = UseKDF.SLOW
        signature_bytes = struct.pack("!I", KDF_method)

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
        return raw if get_bytes else base64.urlsafe_b64encode(raw).decode("UTF-8")


class DecBase:
    def __init__(self, message: Union[str, bytes], mainkey: str) -> None:
        _i = Size.IV
        _s = Size.SALT
        _p = Size.PEPPER
        _h = Size.HMAC
        _fi = Size.StructPack.FOR_ITERATIONS
        _fk = Size.StructPack.FOR_KDF_SIGNATURE
        self.message = parse_encrypted_message(message)
        self.key = mainkey
        self.rec_hmac = self.message[:_h]
        self.rec_iv = self.message[_h : _h + _i]
        self.rec_salt = self.message[_h + _i : _h + _i + _s]
        self.rec_pepper = self.message[_h + _i + _s : _h + _i + _s + _p]
        self.rec_iters_raw = self.message[_h + _i + _s + _p : _h + _i + _s + _p + _fi]
        self.rec_KDF_signature_raw = self.message[
            _h + _i + _s + _p + _fi : _h + _i + _s + _p + _fi + _fk
        ]

        self.rec_iterations = struct.unpack("!I", self.rec_iters_raw)[0]
        self.rec_KDF_signature = struct.unpack("!I", self.rec_KDF_signature_raw)[0]

        check_iterations(self.rec_iterations)
        # pause
        self.rec_ciphertext = self.message[_h + _i + _s + _p + _fi + _fk :]

        compute_intensively = False
        if self.rec_KDF_signature == UseKDF.SLOW:
            compute_intensively = True

        self.dec_key = use_KDF(
            compute_intensively=compute_intensively,
            key=self.key,
            salt_pepper=self.rec_salt,
            iterations=self.rec_iterations,
        )
        self.hmac_k = use_KDF(
            compute_intensively=compute_intensively,
            key=self.key,
            salt_pepper=self.rec_pepper,
            iterations=self.rec_iterations,
        )

        if self._verify_hmac() is False:
            raise exceptions.fixed.MessageTamperingError()

    def _calculated_hmac(self) -> bytes:
        hmac_ = hmac.HMAC(self.hmac_k, hashes.SHA256())
        hmac_.update(
            self.rec_iv
            + self.rec_salt
            + self.rec_pepper
            + self.rec_iters_raw
            + self.rec_KDF_signature_raw
            + self.rec_ciphertext
        )
        return hmac_.finalize()

    def _verify_hmac(self) -> bool:
        return hmc.compare_digest(self._calculated_hmac(), self.rec_hmac)

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
