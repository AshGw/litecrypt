import unittest

from litecrypt.core.helpers.funcs import Size, intensive_KDF


class TestKDFFunction(unittest.TestCase):
    def test_intensive_KDF(self):
        mainkey = "quandale_dingle"
        salt_pepper = b"\x01\x02\x03\x04"
        iterations = 50
        derived_key = intensive_KDF(mainkey, salt_pepper, iterations)
        self.assertIsInstance(derived_key, bytes)
        self.assertEqual(len(derived_key), Size.AES_KEY)

    def test_intensive_KDF_empty_mainkey(self):
        mainkey = ""
        salt_pepper = b"\x01\x02\x03\x04"
        iterations = 50

        with self.assertRaises(ValueError):
            intensive_KDF(mainkey, salt_pepper, iterations)

    def test_intensive_KDF_zero_iterations(self):
        mainkey = "quandale_dingle"
        salt_pepper = b"\x01\x02\x03\x04"
        iterations = 0

        with self.assertRaises(ValueError):
            intensive_KDF(mainkey, salt_pepper, iterations)


if __name__ == "__main__":
    unittest.main()
