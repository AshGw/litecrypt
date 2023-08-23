"""This module provides classes and functions for AES-256 encryption and decryption"""


import base64
import hmac as hmc
import os
import struct
from typing import Any, Optional, Union

import bcrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from litecrypt.utils import exceptions
from litecrypt.utils.consts import Size


class EncBase:
    """
    Class to encrypt data of either type bytes or str.

    This class provides the foundation for encrypting data using a specified key.
     It handles the conversion
    of messages to bytes if needed and performs the necessary cryptographic
     operations for encryption.

    Args:
        message (str,bytes): The message to be encrypted, either as a string or bytes.
        mainkey (str): The main key to derive the HMAC & encryption key from.
        iterations (int, optional): The number of iterations for key derivation.
         Default is 50
    """

    def __init__(
        self,
        message: Union[str, bytes],
        mainkey: str,
        *,
        iterations: int = Size.MIN_ITERATIONS
    ) -> None:
        if isinstance(message, str):
            self.message = message.encode()
        elif isinstance(message, bytes):
            self.message = message

        self.mainkey = mainkey
        if not self.key_verify(self.mainkey):
            raise exceptions.dynamic.KeyLengthError()
        self.iv = os.urandom(Size.IV)
        self.salt = os.urandom(Size.SALT)
        self.pepper = os.urandom(Size.PEPPER)
        self.iterations = iterations
        if (
            self.iterations < Size.MIN_ITERATIONS
            or self.iterations > Size.MAX_ITERATIONS
        ):
            raise exceptions.dynamic.IterationsOutofRangeError(self.iterations)

        self.enc_key = self.derkey(self.mainkey, self.salt, self.iterations)
        self.hmac_key = self.derkey(self.mainkey, self.pepper, self.iterations)

    @staticmethod
    def derkey(mainkey: str, salt_pepper: bytes, iterations: int) -> bytes:
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

    @staticmethod
    def gen_key(desired_bytes: int = 32) -> str:
        """
        This function generates a random encryption key in the form of a hex string.
        The key can be used for various cryptographic purposes.

        Args:
            desired_bytes (int, optional): The number of desired bytes for the key.
                The default is 32 bytes (256 bits). Must be greater than or equal to 32.

        Returns:
            str: A random encryption key as a hex string.

        Raises:
            ValueError: If desired_bytes is less than 32.
        """
        if desired_bytes < 32:
            raise ValueError("desired_bytes must be greater than or equal to 32")

        key = os.urandom(desired_bytes)

        return key.hex()

    @staticmethod
    def key_verify(key: str) -> int:
        """
        Verify if a given key is valid.

        This method checks whether a given key is valid by attempting to convert
         it from hexadecimal
        representation and ensuring its length meets the requirements.

        Args:
            key (str): The key to be verified.

        Returns:
            int: 1 if the key is valid, 0 if the key is valid but does not
             meet length requirements,
            or -1 if the key is not valid.
        """
        try:
            a = bytes.fromhex(key.strip())
            if len(a) >= Size.MAIN_KEY:
                return 1
            else:
                return 0
        except ValueError:
            return -1

    def _mode(self) -> modes.CBC:
        """
        Returns:
            modes.CBC: The AES CBC mode with the specified initialization vector.
        """
        return modes.CBC(self.iv)

    def _cipher(self) -> Cipher:
        """
        Creates an AES cipher object using the encryption key and CBC mode.

        Returns:
            Cipher: The AES cipher object configured with the encryption key
             and CBC mode.
        """
        return Cipher(
            algorithms.AES(key=self.enc_key),
            mode=self._mode(),
            backend=default_backend(),
        )

    def _cipher_encryptor(self) -> Any:
        """
        Returns the encryptor for the AES cipher.

        Returns:
            CipherContext: The encryptor context for the AES cipher.
        """
        return self._cipher().encryptor()

    def padded_message(self) -> bytes:
        """
        Pad the message to a multiple of the block size using PKCS#7 padding.

        Returns:
            bytes: The padded message.
        """
        padder = padding.PKCS7(Size.BLOCK * 8).padder()
        return padder.update(self.message) + padder.finalize()

    def ciphertext(self) -> bytes:
        """
        Encrypt the padded message using AES and return the ciphertext.

        Returns:
            bytes: The encrypted ciphertext.
        """
        return (
            self._cipher_encryptor().update(self.padded_message())
            + self._cipher_encryptor().finalize()
        )

    def iterations_bytes(self) -> bytes:
        """
        Pack the number of iterations into bytes using the 'big-endian' format.

        Returns:
            bytes: The packed bytes representing the number of iterations.
        """
        iters_bytes = struct.pack("!I", self.iterations)
        return iters_bytes

    def hmac_final(self) -> bytes:
        """
        Compute the HMAC-SHA256 of the ciphertext bundle.

        Returns:
            bytes: The computed HMAC-SHA256 value.
        """
        hmac_ = hmac.HMAC(self.hmac_key, hashes.SHA256())
        hmac_.update(
            self.iv
            + self.salt
            + self.pepper
            + self.iterations_bytes()
            + self.ciphertext()
        )
        return hmac_.finalize()

    def encrypt(self, get_bytes: Optional[bool] = False) -> Union[bytes, str]:
        """
        Returns the encrypted data as bytes in the format 'HMAC' -> 'IV'
        -> 'Salt value' -> 'pepper value' -> 'iterations' -> 'ciphertext'.
        Or as a URL safe base64 encoded string of the encrypted bytes' data.

        :param get_bytes: Set to True to get the encrypted data as bytes.
         Default is False.
        :return: Encrypted data as bytes or URL safe base64 encoded string.
        """
        raw = (
            self.hmac_final()
            + self.iv
            + self.salt
            + self.pepper
            + self.iterations_bytes()
            + self.ciphertext()
        )
        return raw if get_bytes else base64.urlsafe_b64encode(raw).decode("UTF-8")


class DecBase:
    """
    Class to decrypt data of either type bytes or str.

    This class provides functionality to decrypt data that
    was previously encrypted using the EncBase class.
    It handles key derivation, verification, and decryption.

    Args:
        message (str, bytes): The encrypted message to be decrypted, either as
         a string or bytes.
        mainkey (str): The main key to derive the HMAC & decryption key from.
    """

    def __init__(self, message: Union[str, bytes], mainkey: str) -> None:
        if isinstance(message, str):
            mess = message.encode("UTF-8")
            self.message = base64.urlsafe_b64decode(mess)
        elif isinstance(message, bytes):
            self.message = message

        _i = Size.IV
        _s = Size.SALT
        _p = Size.PEPPER
        _h = Size.HMAC
        self.key = mainkey
        self.rec_hmac = self.message[:_h]
        self.rec_iv = self.message[_h : _h + _i]
        self.rec_salt = self.message[_h + _i : _h + _i + _s]
        self.rec_pepper = self.message[_h + _i + _s : _h + _i + _s + _p]
        self.rec_iters_raw = self.message[_h + _i + _s + _p : _h + _i + _s + _p + 4]
        self.rec_iterations = struct.unpack("!I", self.rec_iters_raw)[0]
        if (
            self.rec_iterations < Size.MIN_ITERATIONS
            or self.rec_iterations > Size.MAX_ITERATIONS
        ):
            raise exceptions.dynamic.IterationsOutofRangeError(self.rec_iterations)

        self.rec_ciphertext = self.message[_h + _i + _s + _p + 4 :]
        self.dec_key = EncBase.derkey(self.key, self.rec_salt, self.rec_iterations)
        self.hmac_k = EncBase.derkey(self.key, self.rec_pepper, self.rec_iterations)

        if self.verify_hmac() is False:
            raise exceptions.fixed.MessageTamperingError()

    def calculated_hmac(self) -> bytes:
        """
        Compute the HMAC-SHA256 of the received ciphertext bundle.

        Returns:
            bytes: The computed HMAC-SHA256 value.
        """
        hmac_ = hmac.HMAC(self.hmac_k, hashes.SHA256())
        hmac_.update(
            self.rec_iv
            + self.rec_salt
            + self.rec_pepper
            + self.rec_iters_raw
            + self.rec_ciphertext
        )
        return hmac_.finalize()

    def verify_hmac(self) -> bool:
        """
        Verify the received HMAC-SHA256 against the calculated HMAC.

        Returns:
            bool: True if the received HMAC matches the calculated HMAC,
             False otherwise.
        """
        return hmc.compare_digest(self.calculated_hmac(), self.rec_hmac)

    def _mode(self) -> modes.CBC:
        """
        Returns the AES Cipher Block Chaining (CBC) mode with the received IV.

        Returns:
            modes.CBC: The AES CBC mode with the specified initialization vector.
        """
        return modes.CBC(self.rec_iv)

    def _cipher(self) -> Cipher:
        """
        Creates an AES cipher object using the decryption key and CBC mode.

        Returns:
            Cipher: The AES cipher object configured with the decryption
             key and CBC mode.
        """
        return Cipher(
            algorithms.AES(key=self.dec_key),
            mode=self._mode(),
            backend=default_backend(),
        )

    def _cipher_decryptor(self):
        """
        Returns the decryptor object for the AES cipher.

        Returns:
            CipherContext: The decryptor context for the AES cipher.
        """
        return self._cipher().decryptor()

    def _pre_unpadding(self) -> bytes:
        return (
            self._cipher_decryptor().update(self.rec_ciphertext)
            + self._cipher_decryptor().finalize()
        )

    def unpadded_message(self) -> bytes:
        """
        Unpads the data and returns the original message.

        Returns:
            bytes: The unpadded original message.
        """
        unpadder = padding.PKCS7(Size.BLOCK * 8).unpadder()
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
        raw = self.unpadded_message()
        return raw if get_bytes else raw.decode("UTF-8")
