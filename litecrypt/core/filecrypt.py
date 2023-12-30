"""This module is used to encrypt and decrypt files"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional, Union

import litecrypt.core.crypt as core
from litecrypt.core.datacrypt import Crypt, KeyCheckResult
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
    def key_verify(key: str) -> KeyCheckResult:
        return Crypt.key_verify(key)

    def encrypt(self, echo: Optional[bool] = False) -> None:
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
                        ins = core.Enc(
                            message=file_content,
                            mainkey=self.key,
                            compute_intensively=self.intensive_compute,
                            iterations=self.iteration_rounds,
                        )
                        new_content = ins.encrypt(get_bytes=True)
                        f.write(new_content)  # type: ignore
                        _go_ahead_rename_crypt = 1
                    except BaseException:
                        f.write(file_content)
                        raise exceptions.fixed.FileCryptError()
                elif not file_content:
                    f.write(file_content)
                    raise exceptions.fixed.EmptyContentError()
            if _go_ahead_rename_crypt == 1:
                new_filename = self.filename + ".crypt"
                os.rename(self.filename, new_filename)
                if echo:
                    print(
                        f"{Colors.GREEN}{self.filename} encrypted successfully! "
                        f"==> {new_filename}{Colors.RESET}"
                    )
            else:
                if echo:
                    print(
                        f"{Colors.GREEN}{self.filename} encrypted successfully! "
                        f"==> {self.filename}{Colors.RESET}\n"
                        f"{Colors.YELLOW}Filename left unchanged,"
                        f" could not rename it for some rare reason{Colors.RESET}"
                    )
        except OSError:
            raise exceptions.fixed.SysError()

    def decrypt(self, echo: Optional[bool] = False) -> None:
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
                        ins = core.Dec(message=enc_content, mainkey=self.key)
                        a = ins.decrypt(get_bytes=True)
                        f.write(a)  # type: ignore
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
            else:
                if echo:
                    print(
                        f"{Colors.GREEN}{self.filename} decrypted successfully! "
                        f"==> {self.filename}{Colors.RESET}\n"
                        f"{Colors.YELLOW}Filename left unchanged,"
                        f" could not rename it for some rare reason{Colors.RESET}"
                    )
        except OSError:
            raise exceptions.fixed.SysError()
