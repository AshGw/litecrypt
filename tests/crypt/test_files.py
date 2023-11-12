import os
import secrets
import tempfile
import unittest
from unittest.mock import mock_open, patch

from litecrypt import CryptFile, gen_key
from litecrypt.utils.exceptions.fixed import (AlreadyDecryptedError, AlreadyEncryptedError,
                                              EmptyContentError, FileCryptError, FileDoesNotExistError,
                                              GivenDirectoryError, SysError)


class CryptFileModuleTesting(unittest.TestCase):
    def setUp(self) -> None:
        self.data = secrets.token_bytes(50)
        self.key1 = gen_key()
        self.key2 = gen_key()
        self.tempdir = tempfile.TemporaryDirectory()
        self.empty_file = os.path.join(self.tempdir.name, "empty")
        self.filename = os.path.join(self.tempdir.name, "file")
        self.filename_crypt = os.path.join(self.tempdir.name, "file2.crypt")

        open(self.empty_file, "wb").close()
        with open(self.filename, "wb") as f:
            f.write(self.data)
        with open(self.filename_crypt, "wb") as f:
            f.write(os.urandom(64))

    @patch("builtins.open", new_callable=mock_open, create=True)
    def test_empty_file(self, mock_file):
        mock_file.return_value.read.return_value = b""
        with self.assertRaises(EmptyContentError):
            CryptFile(self.empty_file, self.key1).encrypt()

    @patch("os.path.isfile", return_value=False)
    def test_does_not_exist(self, mock_isfile):
        with self.assertRaises(FileDoesNotExistError):
            CryptFile(self.filename + "x", self.key2).encrypt()

    @patch("litecrypt.CryptFile.decrypt")
    def test_already_decrypted(self, mock_decrypt):
        mock_decrypt.side_effect = AlreadyDecryptedError
        with self.assertRaises(AlreadyDecryptedError):
            CryptFile(self.filename, self.key2).decrypt()

    @patch("litecrypt.CryptFile.encrypt")
    def test_already_encrypted(self, mock_encrypt):
        mock_encrypt.side_effect = AlreadyEncryptedError
        with self.assertRaises(AlreadyEncryptedError):
            CryptFile(self.filename_crypt, self.key2).encrypt()

    @patch("litecrypt.CryptFile.decrypt")
    def test_crypt_error(self, mock_decrypt):
        mock_decrypt.side_effect = FileCryptError
        with self.assertRaises(FileCryptError):
            CryptFile(self.filename_crypt, self.key2).decrypt()

    @patch("litecrypt.CryptFile.encrypt", return_value=1)
    def test_success(self, mock_encrypt):
        self.assertEqual(1, CryptFile(self.filename, self.key1).encrypt())

    @patch("os.path.isdir", return_value=True)
    def test_directory_input(self, mock_isdir):
        with self.assertRaises(GivenDirectoryError):
            CryptFile(".", self.key1).encrypt()

    @patch("builtins.open", new_callable=mock_open, create=True)
    def test_os_error(self, mock_file):
        mock_file.side_effect = SysError
        with self.assertRaises(SysError):
            CryptFile(self.filename, self.key1).encrypt()

    def tearDown(self) -> None:
        self.tempdir.cleanup()


if __name__ == "__main__":
    unittest.main()
