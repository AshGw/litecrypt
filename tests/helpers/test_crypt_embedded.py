import unittest

from litecrypt.core.helpers.funcs import Size, check_iterations, cipher_randomizers, exceptions


class TestCipherFunctions(unittest.TestCase):
    def test_cipher_randomizers(self):
        iv, salt, pepper = cipher_randomizers()
        self.assertIsInstance(iv, bytes)
        self.assertIsInstance(salt, bytes)
        self.assertIsInstance(pepper, bytes)
        self.assertEqual(len(iv), Size.IV)
        self.assertEqual(len(salt), Size.SALT)
        self.assertEqual(len(pepper), Size.PEPPER)

    def test_check_iterations_at_lowest_bound(self):
        check_iterations(Size.MIN_ITERATIONS)

    def test_check_iterations_at_highest_bound(self):
        check_iterations(Size.MAX_ITERATIONS)

    def test_out_of_bound_iterations(self):
        with self.assertRaises(exceptions.dynamic.IterationsOutofRangeError):
            check_iterations(Size.MIN_ITERATIONS - 1)
