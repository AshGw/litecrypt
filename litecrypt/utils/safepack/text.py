"""This module is used to encrypt and decrypt text data made only for the GUI"""


from typing import Union

from litecrypt import core


class KeyLengthError(Exception):
    def __init__(self):
        self.display = "Key must be 256 Bit long !"
        super().__init__(self.display)


class Crypt:
    def __init__(self, text: Union[str, bytes], key: str):
        self.text = text
        if self.keyverify(key) == 1:
            self.key = key
        else:
            raise KeyLengthError()

    @staticmethod
    def genkey() -> str:
        return core.EncBase.gen_key()

    @staticmethod
    def keyverify(key: str) -> int:
        if isinstance(key, str):
            try:
                a = bytes.fromhex(key.strip())
                if len(a) == 32:
                    return 1
            except Exception:
                return 0

        else:
            return 2

    def encrypt(self) -> tuple:
        if self.text:
            try:
                ins = core.EncBase(self.text, self.key)
                new_content = ins.encrypt()
                return 1, new_content
            except BaseException:
                output = "E"
                return 0, output
        else:
            return 0.0, "Empty"

    def decrypt(self) -> tuple:
        if self.text:
            try:
                dec_instance = core.DecBase(message=self.text, mainkey=self.key)
                a = dec_instance.decrypt()
                output = a
                return 1, output
            except Exception:
                output = self.text
                return 0, output
        else:
            return 0.0, "Empty"
