# type: ignore

import os
from typing import Union

import qrcode

import litecrypt.core.base as core


def tqr(text: str) -> Union[int, tuple]:
    try:
        qr = qrcode.QRCode(
            version=10,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=1,
        )
        qr.add_data(text.strip())
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.show()
        return 1

    except Exception as e:
        return 0, e


class Crypt:
    def __init__(self, text: Union[str, bytes], key: str):
        self.text = text
        if self.keyverify(key) == 1:
            self.key = key
        else:
            raise ValueError("Key must be 256 Bit long !")

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
