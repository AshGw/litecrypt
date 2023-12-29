import struct
import unittest

from litecrypt.core.crypt import Dec, Enc
from litecrypt.utils import exceptions
from litecrypt.utils.consts import Size

from ..lab.consts import ABOVE_MAX_ITERATIONS_THRESHOLD, MESSAGE_TO_TEST, TAMPERING_BYTES_VALUE


class CoreModuleTesting(unittest.TestCase):
    def setUp(self) -> None:
        self.message: bytes = MESSAGE_TO_TEST
        self.main_key: str = Enc.gen_key()
        self.ins1: Enc = Enc(message=self.message, mainkey=self.main_key)
        self.string_message: str = self.ins1.encrypt()
        self.bytes_message: bytes = self.ins1.encrypt(get_bytes=True)
        self.ins2: Dec = Dec(message=self.bytes_message, mainkey=self.main_key)
        self.h: int = Size.HMAC
        self.k: int = Size.MAIN_KEY
        self.i: int = Size.IV
        self.p: int = Size.PEPPER
        self.s: int = Size.SALT
        self.fi: int = Size.StructPack.FOR_ITERATIONS
        self.fk: int = Size.StructPack.FOR_KDF_SIGNATURE

    def test_HMAC_MismatchError(self) -> None:
        tampered_hmac = (
            self.ins1.encrypt(get_bytes=True)[
                : self.h - TAMPERING_BYTES_VALUE.__len__()
            ]
            + TAMPERING_BYTES_VALUE
        )
        # above mans simply altering the last byte
        tampered_message = tampered_hmac + self.ins1.encrypt(get_bytes=True)[self.h :]
        with self.assertRaises(exceptions.fixed.MessageTamperingError):
            Dec(message=tampered_message, mainkey=self.main_key)

    def test_IterationsOutOfRangeError(self) -> None:
        enb = self.ins1.encrypt(get_bytes=True)
        tampered_message = (
            enb[: self.h + self.i + self.s + self.p]
            + struct.pack("!I", Size.MAX_ITERATIONS + ABOVE_MAX_ITERATIONS_THRESHOLD)
            + enb[self.h + self.i + self.s + self.p + self.fi :]
        )
        with self.assertRaises(exceptions.dynamic.IterationsOutofRangeError):
            Dec(message=tampered_message, mainkey=self.main_key)

    def test_salt(self) -> None:
        self.assertTrue(
            self.bytes_message[self.h + self.i : self.h + self.i + self.s]
            == self.ins1.salt
        )

    def test_pepper(self) -> None:
        self.assertTrue(
            self.bytes_message[
                self.h + self.i + self.s : self.h + self.i + self.s + self.p
            ]
            == self.ins1.pepper
        )

    def test_iterations(self) -> None:
        self.assertTrue(
            self.bytes_message[
                self.h
                + self.i
                + self.s
                + self.p : self.h
                + self.i
                + self.s
                + self.p
                + self.fi
            ]
            == self.ins1._iterations_bytes()
        )

    def test_KDF_signature(self) -> None:
        self.assertTrue(
            self.bytes_message[
                self.h
                + self.i
                + self.s
                + self.p
                + self.fi : self.h
                + self.i
                + self.s
                + self.p
                + self.fi
                + self.fk
            ]
            == self.ins1._signtature_KDF_bytes()
        )

    def test_ciphertext(self) -> None:
        self.assertTrue(
            self.bytes_message[self.h + self.i + self.s + self.p + self.fi + self.fk :]
            == self.ins1._ciphertext()
        )

    def test_HMAC(self) -> None:
        self.assertTrue(self.bytes_message[: self.h] == self.ins1._hmac_final())

    def test_IV(self) -> None:
        self.assertTrue(self.bytes_message[self.h : self.h + self.i] == self.ins1.iv)

    def test_key_length(self) -> None:
        self.assertEqual(self.k, bytes.fromhex(Enc.gen_key()).__len__())

    def test_key_type(self) -> None:
        self.assertIs(str, type(Enc.gen_key()))

    def test_type_iterations(self) -> None:
        self.assertIs(bytes, type(self.ins1._iterations_bytes()))

    def test_typeof_KDF_signature(self) -> None:
        self.assertIs(bytes, type(self.ins1._signtature_KDF_bytes()))

    def test_iterations_fixed_size(self) -> None:
        self.assertEqual(
            Size.StructPack.FOR_ITERATIONS, self.ins1._iterations_bytes().__len__()
        )

    def test_KDF_signature_fixed_size(self) -> None:
        self.assertEqual(
            Size.StructPack.FOR_KDF_SIGNATURE,
            self.ins1._signtature_KDF_bytes().__len__(),
        )

    def test_encryption_output_bytes(self) -> None:
        self.assertIs(bytes, type(self.ins1.encrypt(get_bytes=True)))

    def test_encryption_output_string(self) -> None:
        self.assertIs(str, type(self.ins1.encrypt()))

    def test_HMAC_compare(self) -> None:
        self.assertEqual(self.ins1._hmac_final(), self.ins2.rec_hmac)

    def test_IV_compare(self) -> None:
        self.assertEqual(self.ins1.iv, self.ins2.rec_iv)

    def test_Salt_compare(self) -> None:
        self.assertEqual(self.ins1.salt, self.ins2.rec_salt)

    def test_Pepper_compare(self) -> None:
        self.assertEqual(self.ins1.pepper, self.ins2.rec_pepper)

    def test_Iterations_compare(self) -> None:
        self.assertEqual(self.ins1.iterations, self.ins2.rec_iterations)

    def test_ciphertext_compare(self) -> None:
        self.assertEqual(self.ins1._ciphertext(), self.ins2.rec_ciphertext)

    def test_decryption_output_type(self) -> None:
        self.assertEqual(bytes, type(self.ins2.decrypt(get_bytes=True)))
        self.assertEqual(str, type(self.ins2.decrypt()))


if __name__ == "__main__":
    unittest.main()
