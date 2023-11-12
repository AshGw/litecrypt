import unittest

from litecrypt.core.helpers.funcs import blazingly_fast_KDF


class TestFastKDFFunction(unittest.TestCase):
    def test_blazingly_fast_KDF(self):
        key = "my_secret_key"
        salt = b"\x01\x02\x03\x04"

        derived_key = blazingly_fast_KDF(key, salt)
        self.assertIsInstance(derived_key, bytes)
        self.assertEqual(len(derived_key), 32)  # SHA-256 pops a 256-bit hash


if __name__ == "__main__":
    unittest.main()
