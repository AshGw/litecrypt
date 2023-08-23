"""This module is used to encrypt and decrypt files of either type str or bytes
 made only for the GUI"""


import os

from litecrypt import core


class CryptFile:
    def __init__(self, filename: str, key: str):
        self.filename = filename
        self.not_256_bit_key = 0
        if self.keyverify(key) == 1:
            self.key = key
        else:
            self.not_256_bit_key = 1

    @staticmethod
    def genkey() -> str:
        return core.EncBase.gen_key()

    @staticmethod
    def keyverify(key: str) -> int:
        try:
            if isinstance(key, str):
                a = bytes.fromhex(key.strip())
                if len(a) == 32:
                    return 1
                else:
                    return 0
        except BaseException:
            return 2

    def encrypt(self) -> int:
        if os.path.isdir(self.filename):
            return 7
        if self.not_256_bit_key == 1:
            return 5
        try:
            if not os.path.exists(self.filename):
                return 3
            else:
                if os.path.splitext(self.filename)[1] == ".crypt":
                    return 6
                else:
                    with open(self.filename, "rb") as f:
                        filecontent = f.read()
                    with open(self.filename, "wb") as f:
                        if filecontent:
                            try:
                                ins = core.EncBase(
                                    message=filecontent, mainkey=self.key
                                )
                                new_content = ins.encrypt(get_bytes=True)
                                f.write(new_content)
                                go_ahead_rename_crypt = 1
                            except BaseException:
                                f.write(filecontent)
                                return 0
                        else:
                            f.write(filecontent)
                            return 2
                    if go_ahead_rename_crypt == 1:
                        os.rename(self.filename, self.filename + ".crypt")
                        return 1
        except Exception:
            return 4

    def decrypt(self) -> int:
        if os.path.isdir(self.filename):
            return 7
        if self.not_256_bit_key == 1:
            return 5
        try:
            if not os.path.exists(self.filename):
                return 3
            else:
                if os.path.splitext(self.filename)[1] != ".crypt":
                    return 6
                else:
                    with open(self.filename, "rb") as f:
                        enc_content = f.read()
                    with open(self.filename, "wb") as f:
                        if enc_content:
                            try:
                                ins = core.DecBase(
                                    message=enc_content, mainkey=self.key
                                )
                                a = ins.decrypt(get_bytes=True)
                                f.write(a)
                                go_ahead_remove_crypt = 1
                            except Exception:
                                f.write(enc_content)
                                return 0
                        else:
                            f.write(enc_content)
                            return 2
                    if go_ahead_remove_crypt == 1:
                        os.rename(self.filename, os.path.splitext(self.filename)[0])
                        return 1
        except Exception:
            return 4
