"""This module is used to encrypt and decrypt files"""

import os
from dataclasses import dataclass, field
from typing import Optional, Union

import litecrypt.core.base as core
from litecrypt.core.datacrypt import Crypt
from litecrypt.utils import exceptions
from litecrypt.utils.consts import Colors, Size


@dataclass
class CryptFile:
    """
    Class to encrypt/decrypt a given file. Pass in the filename as well as a 256-bit key.

    Args:
        filename (str): The path to the file to be encrypted/decrypted.
        key (str): The encryption/decryption key.
    """

    filename: str = field()
    key: str = field()
    intensive_compute: bool = field(default=False)
    iteration_rounds: int = field(default=Size.MIN_ITERATIONS)

    def __post_init__(self) -> None:
        if not self.key_verify(self.key):
            raise exceptions.dynamic.KeyLengthError()

    @staticmethod
    def get_binary(filename: str) -> bytes:
        """
        Get the binary data of a given file or path to a file.

        Args:
            filename (str): The path to the file.

        Returns:
            bytes: The binary data of the file.
        """
        with open(filename, "rb") as f:
            binary = f.read()
        return binary

    @staticmethod
    def make_file(
        filename: str,
        content: Union[bytes, str],
    ) -> None:
        """
        Create a file with the specified content.

        Args:
            filename (str): The name of the file to be created.
            content (Union[bytes, str]): The content to be written to the file.
        """
        if isinstance(content, str):
            content = content.encode()
        with open(filename, "wb") as file:
            file.write(content)

    @staticmethod
    def key_verify(key: str) -> int:
        """Method to verify if the key is valid for usage"""
        return Crypt.key_verify(key)

    def encrypt(self, echo: Optional[bool] = False) -> int:
        """
        Encrypt a given file.

        This method attempts to encrypt the specified file using the provided key. If the encryption
        process is successful, it will return 1. Otherwise,
        it will raise an exception specifying the problem.

        Args:
            echo (bool, optional): Whether to print a success message after encryption. Default is False.

        Returns:
            int: 1 if the encryption process was successful.

        Raises:
            exceptions.fixed.GivenDirectoryError: If the provided path is a directory.
            exceptions.fixed.FileDoesNotExistError: If the specified file does not exist.
            exceptions.fixed.AlreadyEncryptedError: If the file is already encrypted.
            exceptions.fixed.FileCryptError: If an error occurs during the encryption process.
            exceptions.fixed.EmptyContentError: If the file's content is empty.
            exceptions.fixed.SysError: If a system error occurs during the encryption process.
        """

        if os.path.isdir(self.filename):
            raise exceptions.fixed.GivenDirectoryError()
        if not os.path.exists(self.filename):
            raise exceptions.fixed.FileDoesNotExistError()
        if os.path.splitext(self.filename)[1] == ".crypt":
            raise exceptions.fixed.AlreadyEncryptedError()
        with open(self.filename, "rb") as f:
            file_content = f.read()
        try:
            with open(self.filename, "wb") as f:
                if file_content:
                    try:
                        ins = core.EncBase(
                            message=file_content,
                            mainkey=self.key,
                            compute_intensively=self.intensive_compute,
                            iterations=self.iteration_rounds,
                        )
                        new_content = ins.encrypt(get_bytes=True)
                        f.write(new_content)
                        go_ahead_rename_crypt = 1
                    except BaseException:
                        f.write(file_content)
                        raise exceptions.fixed.FileCryptError()
                elif not file_content:
                    f.write(file_content)
                    raise exceptions.fixed.EmptyContentError()
            if go_ahead_rename_crypt == 1:
                new_filename = self.filename + ".crypt"
                os.rename(self.filename, new_filename)
                if echo:
                    print(
                        f"{Colors.GREEN}{self.filename} encrypted successfully! "
                        f"==> {new_filename}{Colors.RESET}"
                    )
                return 1
            else:
                if echo:
                    print(
                        f"{Colors.GREEN}{self.filename} encrypted successfully! "
                        f"==> {self.filename}{Colors.RESET}\n"
                        f"{Colors.YELLOW}Filename left unchanged,"
                        f" could not rename it for some rare reason{Colors.RESET}"
                    )
                return -1
        except OSError:
            raise exceptions.fixed.SysError()

    def decrypt(self, echo: Optional[bool] = False) -> int:
        """
        Decrypt a given file.

        This method attempts to decrypt the specified encrypted file using
         the provided key.
        If the decryption process is successful, it will return 1.
        Otherwise, it will raise an exception specifying the problem.

        Args:
            echo (bool, optional): Whether to print a success message after decryption.
             Default is False.

        Returns:
            int: 1 if the decryption process was successful.

        Raises:
            exceptions.fixed.GivenDirectoryError: If the provided path is a directory.
            exceptions.fixed.FileDoesNotExistError: If the specified file does not
             exist.
            exceptions.fixed.AlreadyDecryptedError: If the file is not encrypted.
            exceptions.fixed.EmptyContentError: If the file's encrypted content
             is empty.
            exceptions.fixed.FileCryptError: If an error occurs during
             the decryption process.
            exceptions.fixed.SysError: If a system error occurs during
             the decryption process.
        """

        if os.path.isdir(self.filename):
            raise exceptions.fixed.GivenDirectoryError()
        if not os.path.exists(self.filename):
            raise exceptions.fixed.FileDoesNotExistError()
        if os.path.splitext(self.filename)[1] != ".crypt":
            raise exceptions.fixed.AlreadyDecryptedError()
        with open(self.filename, "rb") as f:
            enc_content = f.read()
        try:
            with open(self.filename, "wb") as f:
                if not enc_content:
                    f.write(enc_content)
                    raise exceptions.fixed.EmptyContentError()
                else:
                    try:
                        ins = core.DecBase(message=enc_content, mainkey=self.key)
                        a = ins.decrypt(get_bytes=True)
                        f.write(a)
                        go_ahead_remove_crypt = 1
                    except Exception:
                        f.write(enc_content)
                        raise exceptions.fixed.FileCryptError()
            if go_ahead_remove_crypt == 1:
                new_filename = os.path.splitext(self.filename)[0]

                os.rename(self.filename, new_filename)
                if echo:
                    print(
                        f"{Colors.GREEN}{self.filename} decrypted successfully! "
                        f"==> {new_filename}{Colors.RESET}"
                    )
                return 1
            else:
                if echo:
                    print(
                        f"{Colors.GREEN}{self.filename} decrypted successfully! "
                        f"==> {self.filename}{Colors.RESET}\n"
                        f"{Colors.YELLOW}Filename left unchanged,"
                        f" could not rename it for some rare reason{Colors.RESET}"
                    )
                return -1
        except OSError:
            raise exceptions.fixed.SysError()
