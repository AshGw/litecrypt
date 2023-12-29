from __future__ import annotations

import hmac as hmc

from typing import Union
from struct import unpack
from cryptography.hazmat.primitives import hashes, hmac
from litecrypt.core.helpers.funcs import (
    check_iterations,
    cipher_randomizers,
    parse_encrypted_message,
    parse_message,
    use_KDF,
)
from litecrypt.utils import exceptions
from litecrypt.utils.consts import Size, UseKDF

DEFAULT_INTENSIVE_COMPUTE = False


class EncBase:
    def __init__(
        self,
        message: Union[str, bytes],
        mainkey: str,
        iterations: int = Size.MIN_ITERATIONS,
        compute_intensively: bool = DEFAULT_INTENSIVE_COMPUTE,
    ) -> None:
        self.message = parse_message(message)
        self.mainkey = mainkey
        self.compute_intensively = compute_intensively
        self.iterations = check_iterations(iterations)
        self.verify_key(self.mainkey)

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
    def verify_key(key: str) -> None:
        if len(bytes.fromhex(key.strip())) < Size.MAIN_KEY:
            raise ValueError(
                f"raw key size must be greater or equal to: {Size.MAIN_KEY} {Size.UNIT}"
            )


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

        self.rec_iterations = check_iterations(
            unpack("!I", self.rec_iters_raw)[0]
        )
        self.rec_KDF_signature = unpack("!I", self.rec_KDF_signature_raw)[0]
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
