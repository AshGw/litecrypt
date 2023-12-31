import os
import random
from typing import List, Tuple

from litecrypt import Crypt, CryptFile, gen_key, gen_ref, spawn

from ..lab.main import (
    Database,
    Names,
    Vals,
    create_test_grounds,
    deque,
    force_remove,
    verify_exact,
)


class WorkFlow:
    def __init__(self) -> None:
        self.key: str = gen_key()
        self.ref: str = gen_ref()
        self.main_conn: Database = Vals.main_conn
        self.keys_conn: Database = Vals.keys_conn
        self.original_dir: str = Names.original_dir
        self.new_dir: str = Names.new_dir
        self.files: deque = Names.files
        self.file_contents: List[bytes] = Vals.file_contents

    def setup(self) -> bool:
        create_test_grounds(
            original_directory=self.original_dir,
            new_directory=self.new_dir,
            file1=self.files[0],
            file2=self.files[1],
            file3=self.files[2],
            file1_content=self.file_contents[0],
            file2_content=self.file_contents[1],
            file3_content=self.file_contents[2],
        )

        self.encrypted_contents = [
            Crypt(
                content,
                self.key,
                intensive_compute=False,
                iteration_rounds=random.randint(50, 1000),
            ).encrypt(get_bytes=True)
            for content in self.file_contents
        ]
        return True

    def database_insertion(self) -> bool:
        for file, encrypted_content in zip(self.files, self.encrypted_contents):
            self.main_conn.insert(
                filename=f"does-not-matter/{file}.crypt",
                content=encrypted_content,
                ref=self.ref,
            )
            self.keys_conn.insert(
                filename=f"does-not-matter/{file}.crypt", content=self.key, ref=self.ref
            )
        return True

    def spawn_out(self) -> bool:
        self.spawned = spawn(
            main_connection=self.main_conn,
            keys_connection=self.keys_conn,
            key_reference=self.ref,
            directory=self.new_dir,
            get_all=True,
            echo=True,
        )
        return True

    def check_spawning(self) -> bool:
        for file, key in zip(self.spawned["filenames"], self.spawned["keys"]):
            CryptFile(file, key).decrypt(echo=True)
        return True

    def verify_compatability(self) -> Tuple[bool, bool, bool]:
        is_file1_truthy = verify_exact(
            os.path.join(self.original_dir, self.files[0]),
            os.path.join(self.new_dir, self.files[0]),
        )
        is_file2_truthy = verify_exact(
            os.path.join(self.original_dir, self.files[1]),
            os.path.join(self.new_dir, self.files[1]),
        )
        is_file3_truthy = verify_exact(
            os.path.join(self.original_dir, self.files[2]),
            os.path.join(self.new_dir, self.files[2]),
        )

        return is_file1_truthy, is_file2_truthy, is_file3_truthy

    def end_connection(self) -> bool:
        self.main_conn.end_session()
        self.keys_conn.end_session()
        return True


workflow_output = {
    "setup": False,
    "insertion": False,
    "spawning": False,
    "spawning status": False,
    "files compatibility": False,
    "database connection": False,
}


def run_workflow() -> None:
    workflow = WorkFlow()

    is_setup = workflow.setup()
    workflow_output["setup"] = is_setup

    is_inserted = workflow.database_insertion()
    workflow_output["insertion"] = is_inserted

    is_spawned = workflow.spawn_out()
    workflow_output["spawning"] = is_spawned

    is_spawned_flawlessly = workflow.check_spawning()
    workflow_output["spawning status"] = is_spawned_flawlessly

    is_file1_truthy, is_file2_truthy, is_file3_truthy = workflow.verify_compatability()
    if is_file1_truthy and is_file2_truthy and is_file3_truthy:
        workflow_output["files compatibility"] = True

    is_database_disconnected = workflow.end_connection()
    workflow_output["database connection"] = is_database_disconnected


def test_workflow():
    run_workflow()
    assert workflow_output["setup"]
    assert workflow_output["insertion"]
    assert workflow_output["spawning"]
    assert workflow_output["spawning status"]
    assert workflow_output["files compatibility"]
    assert workflow_output["database connection"]
    force_remove(
        Names.keys_db,
        Names.main_db,
        Names.new_dir,
        Names.original_dir,
        echo=True,
    )
