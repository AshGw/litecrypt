import unittest

from litecrypt.utils.consts import Size


class ConstsTesting(unittest.TestCase):
    def test_sizes(self):
        assert Size.PEPPER >= 0 and Size.PEPPER % 16 == 0
        assert Size.SALT >= 0 and Size.SALT % 16 == 0
        assert Size.IV == 16
        assert Size.BLOCK == 16
        assert Size.MAIN_KEY == 32
        assert Size.AES_KEY == 32
        assert Size.HMAC == 32
        assert Size.MIN_ITERATIONS == 50
        assert Size.MAX_ITERATIONS == 10**6


if __name__ == "__main__":
    unittest.main()
