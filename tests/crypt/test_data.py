import unittest

from litecrypt.core.datacrypt import Crypt, gen_key
from litecrypt.utils.exceptions.fixed import CryptError, EmptyContentError


class DataTesting(unittest.TestCase):
    def setUp(self) -> None:
        self.key = gen_key()
        self.message = "fixed message"
        self.bytes_message = self.message.encode("UTF-8")

    def test_strings(self):
        mess = Crypt(self.message, self.key).encrypt()
        Crypt(mess, self.key).decrypt()

    def test_bytes(self):
        mess = Crypt(self.bytes_message, self.key).encrypt(get_bytes=False)
        Crypt(mess, self.key).decrypt()

    def test_void_message(self):
        with self.assertRaises(EmptyContentError):
            Crypt("", self.key).encrypt()

    def test_crypt_err(self):
        with self.assertRaises(CryptError):
            Crypt(self.message, self.key).decrypt()


if __name__ == "__main__":
    unittest.main()
