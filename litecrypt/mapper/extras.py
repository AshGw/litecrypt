import os
from typing import Any, List, Optional, Union, Dict
from litecrypt.mapper.database import Database
from litecrypt.core.filecrypt import CryptFile
from litecrypt.mapper.consts import Default, Status
from litecrypt.mapper.interfaces import (
    DatabaseResponse,
)
from litecrypt.mapper.models import StashKeys, StashMain
from litecrypt.utils.consts import Colors


def reference_linker(
    *,
    connection: Database,
    key_reference: str,
    get_filename: Optional[bool] = False,
    get_content_or_key: Optional[bool] = False,
    get_all: Optional[bool] = False,
) -> Union[str, bytes, List[Any]]:
    """
    Retrieve specific information from the database linked with a key_reference value.

    This function allows you to retrieve various types of data associated with a given
    key reference value from the specified database connection.

    Args:
        connection (Database): A connected Database object.
        key_reference (str): The key reference to link with.
        get_filename (bool, optional): Retrieve the filename(s) associated with
        the key reference. Default is False.
        get_content_or_key (bool, optional): Retrieve content(s) associated with
        the key reference if connected to the main database, or retrieve key(s) if
        connected to the keys database. Default is False.
        get_all (bool, optional): Retrieve all filenames or all contents/keys.
            If True, fetches all matches; otherwise, only the first match is retrieved.
            Default is False.
    Returns:
        Union[str, bytes, List[Union[str, bytes]]]: Depending on the options, returns:
            * If 'get_filename' is True, retrieved filename(s) (str) or an empty string.
            * If 'get_content_or_key' is True, retrieved content(s) or key(s) (str | bytes) or None.
            * If 'get_all' is True, returns a list of retrieved items; otherwise, a single item.

    Note:
        If retrieving all content, consider memory consumption for large files, as data will be stored
        in memory until released. This may lead to slower performance for large files.
    """
    if get_filename and get_content_or_key:
        raise ValueError(
            "Cannot select both 'get_filename' and 'get_content_or_key' simultaneously."
        )
    if not get_filename and not get_content_or_key:
        raise ValueError("Select either 'get_filename' or 'get_content_or_key'.")
    if get_all:
        all_matches_list = []
        if connection.Table == StashMain:
            data = (
                connection.session.query(StashMain)
                .filter(StashMain.ref == key_reference)
                .all()
            )
            all_matches_list = [(row.filename, row.content, row.ref) for row in data]
        elif connection.Table == StashKeys:
            data = (
                connection.session.query(StashKeys)
                .filter(StashKeys.ref == key_reference)
                .all()
            )
            all_matches_list = [(row.filename, row.content, row.ref) for row in data]

        filenames_list = [trio[0] for trio in all_matches_list]
        file_content_or_keys_list = [trio[1] for trio in all_matches_list]

        return file_content_or_keys_list if get_content_or_key else filenames_list

    else:
        if connection.Table == StashMain:
            first_match = (
                connection.session.query(StashMain)
                .filter(StashMain.ref == key_reference)
                .first()
            )
            if first_match:
                return (
                    first_match.content if get_content_or_key else first_match.filename
                )

        elif connection.Table == StashKeys:
            first_match = (
                connection.session.query(StashKeys)
                .filter(StashKeys.ref == key_reference)
                .first()
            )
            if first_match:
                return (
                    first_match.content if get_content_or_key else first_match.filename
                )


def _spawn_single_file(
    main_connection: Database,
    keys_connection: Database,
    key_reference: str,
    directory: Optional[str] = Default.SPAWN_DIRECTORY,
    echo: Optional[bool] = False,
) -> Union[DatabaseResponse, None]:
    try:
        content = reference_linker(
            connection=main_connection,
            key_reference=key_reference,
            get_content_or_key=True,
        )
        path = reference_linker(
            connection=main_connection,
            key_reference=key_reference,
            get_filename=True,
        )
        filename = os.path.split(path)[1]

        key = reference_linker(
            connection=keys_connection,
            key_reference=key_reference,
            get_content_or_key=True,
        )

        if CryptFile.key_verify(key) != 1 and key != Default.KEY:
            raise ValueError(
                f"Invalid key, check if {Database.__name__} object placement is correct."
            )

        full_path = os.path.join(directory, filename)

        CryptFile.make_file(filename=full_path, content=content)

        if echo:
            print(
                f"{Colors.GREEN}{filename} has been successfully"
                f" spawned in the directory: "
                f"{directory}{Colors.RESET}"
            )

        return DatabaseResponse(
            status=Status.SUCCESS,
            filenames=[os.path.join(directory, filename)],
            contents=[content],
            keys=[key],
        )

    except Exception as e:
        if main_connection.silent_errors and keys_connection.silent_errors:
            return None
        raise e


def _spawn_all_files(
    main_connection: Database,
    keys_connection: Database,
    key_reference: str,
    directory: Optional[str],
    ignore_duplicate_files: Optional[bool] = False,
    echo: Optional[bool] = False,
) -> Union[DatabaseResponse, None]:
    try:
        keys_list = reference_linker(
            connection=keys_connection,
            key_reference=key_reference,
            get_content_or_key=True,
            get_all=True,
        )
        for key in keys_list:
            if CryptFile.key_verify(key) != 1 and key != Default.KEY:
                raise ValueError(
                    "Invalid key for cryptographic usage detected, mismatch found"
                    f" check if {Database.__name__} object placement is correct."
                )

        contents_list = reference_linker(
            connection=main_connection,
            key_reference=key_reference,
            get_content_or_key=True,
            get_all=True,
        )
        paths_list = reference_linker(
            connection=main_connection,
            key_reference=key_reference,
            get_filename=True,
            get_all=True,
        )
        filenames_list = [os.path.basename(path) for path in paths_list]

        if ignore_duplicate_files:
            seen_filenames = {}
            duplicate_indexes = []

            for index, filename in enumerate(filenames_list):
                if filename in seen_filenames:
                    duplicate_indexes.append(index)
                else:
                    seen_filenames[filename] = index

            # Removing duplicates from the lists using the collected indexes
            filenames_list[:] = [
                filename
                for index, filename in enumerate(filenames_list)
                if index not in duplicate_indexes
            ]
            contents_list[:] = [
                content
                for index, content in enumerate(contents_list)
                if index not in duplicate_indexes
            ]
            keys_list[:] = [
                key
                for index, key in enumerate(keys_list)
                if index not in duplicate_indexes
            ]
        dir = directory if directory is not None else Default.SPAWN_DIRECTORY

        # The creation of the extracted files in the specified directory
        full_paths_list = [
            os.path.join(dir, os.path.split(path)[1]) for path in filenames_list
        ]
        for full_path, content in zip(full_paths_list, contents_list):
            CryptFile.make_file(filename=full_path, content=content)
            if echo:
                print(
                    f"{Colors.GREEN}{full_path} has been spawned"
                    f" successfully.{Colors.RESET}"
                )
        files_in_new_directory = [os.path.join(dir, file) for file in filenames_list]
        return DatabaseResponse(
            status=Status.SUCCESS,
            filenames=files_in_new_directory,
            contents=contents_list,
            keys=keys_list,
        )

    except Exception as e:
        if main_connection.silent_errors and keys_connection.silent_errors:
            return None
        raise e


def spawn(
    *,
    main_connection: Database,
    keys_connection: Database,
    key_reference: str,
    directory: Optional[str],
    get_all: Optional[bool] = False,
    ignore_duplicate_files: Optional[bool] = False,
    echo: Optional[bool] = False,
) -> DatabaseResponse:
    """
    Depending on the parameters, this function can fetch a single file or multiple
    files associated with the provided key_reference.
    The fetched files are then created in the specified directory.

    Args:
        main_connection (Database): Connection to the main database.
        keys_connection (Database): Connection to the keys' database.
        key_reference (str): The reference key to link with.
        directory (str, optional): The directory where files will be created.
        Default is the current directory.
        get_all (bool, optional): Retrieve and create all files associated
        with the key_reference. Default is False, indicating retrieval of a single file.
        ignore_duplicate_files (bool, optional): When True, duplicate filenames
        are ignored during creation. Default is False.
        echo (bool, optional): Whether to print result information. Default is False.

    Returns:
            DatabaseResponse Object containing the outcome of the retrieval and creation process.
    """
    dir = directory if directory is not None else Default.SPAWN_DIRECTORY
    if main_connection is keys_connection:
        raise ValueError("Main and keys databases must be different")

    elif not os.path.isdir(dir):
        raise ValueError(f"{dir} is not a valid directory")
    result = DatabaseResponse(status=Status.FAILURE)

    if get_all:
        result = _spawn_all_files(
            main_connection=main_connection,
            keys_connection=keys_connection,
            key_reference=key_reference,
            directory=directory,
            ignore_duplicate_files=ignore_duplicate_files,
            echo=echo,
        )
    elif not get_all:
        result = _spawn_single_file(
            main_connection=main_connection,
            keys_connection=keys_connection,
            key_reference=key_reference,
            directory=directory,
            echo=echo,
        )
    _echo_dict(echo=echo, dictionary=result)
    return result


def _echo_dict(dictionary: Dict[str, Any], echo: Optional[bool] = False) -> None:
    if echo:
        for key, value in dictionary.items():
            key_colored = Colors.YELLOW + key + Colors.RESET

            if key == Status.__name__.lower() and value == Status.SUCCESS:
                value_colored = Colors.GREEN + str(value) + Colors.RESET
            elif key == Status.__name__.lower() and value == Status.FAILURE:
                value_colored = Colors.RED + str(value) + Colors.RESET
            else:
                value_colored = Colors.CYAN + str(value) + Colors.RESET

            print(f"{key_colored}: {value_colored}")
