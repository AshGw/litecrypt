import os
import shutil
from collections import deque
from typing import Optional
from uuid import uuid4

from litecrypt.core.filecrypt import CryptFile
from litecrypt.mapper.database import Database
from litecrypt.utils.consts import Colors


class Names:
    MAIN_DB = "main" + uuid4().hex + ".db"
    KEYS_DB = "keys" + uuid4().hex + ".db"
    ORIGINAL_DIRECTORY = "original" + uuid4().hex
    NEW_DIRECTORY = "new" + uuid4().hex
    FILES = deque(["file.txt", "file", "file.png"], maxlen=3)


class Vals:
    MAIN_DB = Database(Names.MAIN_DB, echo=True)
    KEYS_DB = Database(Names.KEYS_DB, for_keys=True, echo=True)
    FILE_CONTENTS = [uuid4().bytes for _ in range(len(Names.FILES))]


def create_test_grounds(
    *,
    original_directory: str,
    new_directory: str,
    file1: str,
    file2: str,
    file3: str,
    file1_content: bytes,
    file2_content: bytes,
    file3_content: bytes,
):
    os.mkdir(original_directory)
    os.mkdir(new_directory)
    files = [file1, file2, file3]
    file_contents = [file1_content, file2_content, file3_content]

    for file, content in zip(files, file_contents):
        CryptFile.make_file(f"{original_directory}/{file}", content=content)


def verify_exact(filepath1: str, filepath2: str) -> bool:
    try:
        with open(filepath1, "rb") as file1, open(filepath2, "rb") as file2:
            content1 = file1.read()
            content2 = file2.read()

            return content1 == content2
    except IOError:
        return False


def force_remove(*paths: str, echo: Optional[bool] = False):
    for path in paths:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                if echo:
                    print(
                        f"{Colors.GREEN}Folder '{path}' has been removed.{Colors.RESET}"
                    )
            elif os.path.isfile(path):
                os.remove(path)
                if echo:
                    print(
                        f"{Colors.GREEN}File '{path}' has been removed.{Colors.RESET}"
                    )
            else:
                if echo:
                    print(
                        f"{Colors.YELLOW}'{path}' is neither a folder nor a file.{Colors.RESET}"
                    )
        except Exception as e:
            if echo:
                print(f"{Colors.RED}Error while removing '{path}': {e}{Colors.RESET}")
