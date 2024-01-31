class LiteCryptError(Exception):
    pass


class MessageTamperingError(LiteCryptError):
    def __init__(self) -> None:
        self.display = (
            "HMAC mismatch ! Message has been TAMPERED with ,\n"
            " or Possible key difference"
        )
        super().__init__(self.display)


class EmptyContentError(LiteCryptError):
    def __init__(self) -> None:
        self.display = "Empty content !"
        super().__init__(self.display)


class GivenDirectoryError(LiteCryptError):
    def __init__(self) -> None:
        self.display = "Given directory instead of file"
        super().__init__(self.display)


class FileDoesNotExistError(LiteCryptError):
    def __init__(self) -> None:
        self.display = "Given path does not contain the specified file !"
        super().__init__(self.display)


class SysError(LiteCryptError):
    def __init__(self) -> None:
        self.display = "System related Error."
        super().__init__(self.display)


class FileCryptError(LiteCryptError):
    def __init__(self) -> None:
        self.display = (
            "Error in cryptographic operation for the file, probable distortion."
        )
        super().__init__(self.display)


class CryptError(LiteCryptError):
    def __init__(self) -> None:
        self.display = "Error in cryptographic operation, probable distortion."
        super().__init__(self.display)


class AlreadyEncryptedError(LiteCryptError):
    def __init__(self) -> None:
        self.display = "File is already encrypted !"
        super().__init__(self.display)


class AlreadyDecryptedError(LiteCryptError):
    def __init__(self) -> None:
        self.display = "File is already decrypted !"
        super().__init__(self.display)


class ColumnDoesNotExist(LiteCryptError):
    def __init__(self) -> None:
        self.display = "Specified column does not include: ['name','content','ref']"
        super().__init__(self.display)
