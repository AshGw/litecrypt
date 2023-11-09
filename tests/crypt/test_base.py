import struct
import unittest

import litecrypt.core.base as lc
from litecrypt.utils import exceptions
from litecrypt.utils.consts import Size


class CoreModuleTesting(unittest.TestCase):
    def setUp(self) -> None:
        self.message = b'MESSAGE123#"/?.@$%'
        self.main_key = lc.EncBase.gen_key()
        self.ins1 = lc.EncBase(message=self.message, mainkey=self.main_key)
        self.string_message = self.ins1.encrypt()
        self.bytes_message = self.ins1.encrypt(get_bytes=True)
        self.ins2 = lc.DecBase(message=self.bytes_message, mainkey=self.main_key)
        self.h = Size.HMAC
        self.k = Size.MAIN_KEY
        self.i = Size.IV
        self.p = Size.PEPPER
        self.s = Size.SALT
        self.fi = Size.StructPack.FOR_ITERATIONS
        self.fk = Size.StructPack.FOR_KDF_SIGNATURE

    def test_HMAC_MismatchError(self):
        tampered_hmac = self.ins1.encrypt(get_bytes=True)[: self.h - 1] + b"1"
        tampered_message = tampered_hmac + self.ins1.encrypt(get_bytes=True)[self.h :]
        with self.assertRaises(exceptions.fixed.MessageTamperingError):
            lc.DecBase(message=tampered_message, mainkey=self.main_key)

    def test_IterationsOutOfRangeError(self):
        enb = self.ins1.encrypt(get_bytes=True)
        tampered_message = (
            enb[: self.h + self.i + self.s + self.p]
            + struct.pack("!I", Size.MAX_ITERATIONS + 10)
            + enb[self.h + self.i + self.s + self.p + self.fi :]
        )
        with self.assertRaises(exceptions.dynamic.IterationsOutofRangeError):
            lc.DecBase(message=tampered_message, mainkey=self.main_key)

    def test_Salt(self):
        self.assertTrue(
            self.bytes_message[self.h + self.i : self.h + self.i + self.s]
            == self.ins1.salt
        )

    def test_Pepper(self):
        self.assertTrue(
            self.bytes_message[
                self.h + self.i + self.s : self.h + self.i + self.s + self.p
            ]
            == self.ins1.pepper
        )

    def test_Iterations(self):
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
            == self.ins1.iterations_bytes()
        )

    def test_Ciphertext(self):
        self.assertTrue(
            self.bytes_message[self.h + self.i + self.s + self.p + self.fi + self.fk :]
            == self.ins1.ciphertext()
        )

    def test_HMAC(self):
        self.assertTrue(self.bytes_message[: self.h] == self.ins1.hmac_final())

    def test_IV(self):
        self.assertTrue(self.bytes_message[self.h : self.h + self.i] == self.ins1.iv)

    def test_KeyLength(self):
        self.assertEqual(self.k, bytes.fromhex(lc.EncBase.gen_key()).__len__())

    def test_KeyType(self):
        self.assertIs(str, type(lc.EncBase.gen_key()))

    def test_TypeIterations(self):
        self.assertIs(bytes, type(self.ins1.iterations_bytes()))

    def test_IterationsFixed_size(self):
        self.assertEqual(4, self.ins1.iterations_bytes().__len__())

    def test_EncOutputBytes(self):
        self.assertIs(bytes, type(self.ins1.encrypt(get_bytes=True)))

    def test_EncOutputString(self):
        self.assertIs(str, type(self.ins1.encrypt()))

    def test_HMAC_Comp(self):
        self.assertEqual(self.ins1.hmac_final(), self.ins2.rec_hmac)

    def test_IV_Comp(self):
        self.assertEqual(self.ins1.iv, self.ins2.rec_iv)

    def test_Salt_Comp(self):
        self.assertEqual(self.ins1.salt, self.ins2.rec_salt)

    def test_Pepper_Comp(self):
        self.assertEqual(self.ins1.pepper, self.ins2.rec_pepper)

    def test_Iterations_Comp(self):
        self.assertEqual(self.ins1.iterations, self.ins2.rec_iterations)

    def test_Ciphertext_Comp(self):
        self.assertEqual(self.ins1.ciphertext(), self.ins2.rec_ciphertext)

    def test_DecOutputBytes(self):
        self.assertEqual(bytes, type(self.ins2.decrypt(get_bytes=True)))

    def test_DecOutputString(self):
        self.assertEqual(str, type(self.ins2.decrypt()))


if __name__ == "__main__":
    unittest.main()
