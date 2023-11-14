"""Module to interact with a database for litecrypt"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generator, List, Optional, Union, Dict, Tuple

from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker

from litecrypt.core.filecrypt import CryptFile
from litecrypt.mapper.consts import Default, EngineFor, Status
from litecrypt.mapper.engines import get_engine
from litecrypt.mapper.interfaces import (
    Columns,
    DatabaseResponse,
    DatabaseFailure,
    DatabaseFailureResponse,
    DBError,
    QueryResponse,
)
from litecrypt.mapper.models import Base, StashKeys, StashMain
from litecrypt.utils.consts import Colors
from litecrypt.utils.exceptions.fixed import ColumnDoesNotExist


@dataclass
class Database:
    """
    Represents a database class with various methods to interact with a given database.

    This class provides a simplified interface to interact with a database,
    designed for various database systems (MySQL, PostgreSQL and SQLite).
    It includes methods to connect to the database, perform basic operations, and more.

    :param url: The URL or connection string for the database.
    :param echo: If True, the engine will log all statements as well as a table of execution times.
    :param engine_for: The database engine to use (default is "sqlite").
    :param for_main: If True, the Database instance is associated with the StashMain table.
    :param for_keys: If True, the Database instance is associated with the StashKeys table.
    """

    url: str = field()
    echo: bool = field(default=False)
    engine_for: str = field(default=Default.ENGINE)
    for_main: Optional[bool] = True
    for_keys: Optional[bool] = False
    silent_errors: Optional[bool] = True

    def __post_init__(self) -> None:
        self.engine = get_engine(
            engine_for=self.engine_for, echo=self.echo, url=self.url
        )
        self.create_all()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.columns: List[str] = Columns.list()
        self.Table = StashKeys if self.for_keys else StashMain

    @property
    def size(self) -> Union[float, DatabaseFailureResponse, None]:
        """Get the size of the SQLite database in megabytes."""
        if self.engine_for != EngineFor.SQLITE:
            if self.echo:
                print(f"This function only supports {EngineFor.SQLITE} databases.")
                return None
        try:
            raw = "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size"
            return self.session.execute(statement=raw).fetchall()[0][0] / 1024 / 1024
        except DBError as e:
            if self.silent_errors:
                return DatabaseFailure(error=e, failure=1).get()
            raise e

    @property
    def last_mod(self) -> Union[datetime, DatabaseFailureResponse, None]:
        """Get the last modification timestamp of the SQLite database file."""
        if self.engine_for != EngineFor.SQLITE:
            if self.echo:
                print(f"This function only supports {EngineFor.SQLITE} databases.")
            return None
        try:
            return datetime.fromtimestamp(os.stat(self.url).st_mtime)
        except OSError as e:
            if self.silent_errors:
                return DatabaseFailure(failure=1, error=e).get()
            raise e

    @property
    def current_table(self) -> str:
        """Returns the table name of the current database"""
        return self.Table.__name__

    def end_session(self) -> None:
        """
        Closes the database session and commits pending transactions.

        If there is an active session, this method commits any pending
        transactions and then closes the session to the SQLite database.
        It's important to call this method when you're done using
        the database to ensure proper cleanup and release of resources.

        Usage example:
            >>> conn = Database('database.db')
            >>> # Perform database operations
            >>> conn.end_session()  # End the session when done
        """
        self.session.commit()
        self.session.close()

    def create_all(self) -> None:
        """Creates all the tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    def insert(self, filename: str, content: Union[bytes, str], ref: str) -> None:
        """
        Adds a new record to the current table with the specified
        filename, content, and reference values.

        :param filename: The name of the file.
        :type filename: str
        :param content: The content of the file, either as bytes or a string.
        :type content: Union[bytes, str]
        :param ref: A reference identifier for the file.
        :type ref: str
        """
        record = self.Table(filename=filename, ref=ref, content=content)
        self.session.add(record)
        self.session.commit()

    def update(self, *, column: str, id: int, value) -> None:
        """
        Updates the value of the specified column for a record with
        the given ID in the current table.

        :param column: The name of the column to update.
        :type column: str
        :param id: The ID of the record to update.
        :type id: int
        :param value: The new value to set for the specified column.
        :type value: Any

        :raises ColumnDoesNotExist: If the specified column does not exist in the table.
        """
        if column not in self.columns:
            raise ColumnDoesNotExist
        row = self.session.query(self.Table).filter(self.Table.id == id).one_or_none()
        if row is not None:
            setattr(row, column, value)
            self.session.commit()

    def content(self) -> Union[Generator, DatabaseFailureResponse]:
        """
        Queries and returns ALL records from the current table.

        :return: A generator yielding lists representing records.
        :rtype: Union[Generator, DatabaseFailureResponse]
        """
        try:
            result = self.session.query(self.Table).all()
            for row in result:
                yield [row.id, row.filename, row.content, row.ref]
        except DBError as e:
            if self.silent_errors:
                return DatabaseFailure(error=e, failure=1).get()
            raise e

    def content_by_id(self, id: int) -> Union[List[Union[str, bytes]], DatabaseFailureResponse]:
        """
        Retrieve a specific record from the current table by its ID.

        :param id: The ID of the record to retrieve.
        :type id: int

        :return: A list representing the record.
        """
        try:
            result = self.session.query(self.Table).filter_by(id=id).first()
            return [result.id, result.filename, result.content, result.ref]
        except DBError as e:
            if self.silent_errors:
                return DatabaseFailure(error=e, failure=1).get()
            raise e

    def show_tables(self) -> Union[List[str], DatabaseFailureResponse]:
        """Retrieve a list of table names in the database."""
        try:
            metadata = MetaData()
            metadata.reflect(bind=self.engine)
            return list(metadata.tables.keys())
        except DBError as e:
            if self.silent_errors:
                return DatabaseFailure(error=e, failure=1).get()
            raise e

    def drop_all_tables(self) -> None:
        """Drop all defined tables within the database"""
        Base.metadata.drop_all(self.engine)

    def drop_content(self, id_: int) -> Union[None, DatabaseFailureResponse]:
        """Delete a specific record from the current table by its ID."""
        try:
            row = (
                self.session.query(self.Table)
                .filter(self.Table.id == id_)
                .one_or_none()
            )
            if row is not None:
                self.session.delete(row)
                self.session.commit()
        except DBError as e:
            if self.silent_errors:
                return DatabaseFailure(error=e, failure=1).get()
            raise e

    def _query(self, *queries: str) -> List[Any]: # GUI use
        result = []
        for i, query in enumerate(queries):
            if not isinstance(query, str):
                result.append({f"query {i}": (-1, TypeError)})
            try:
                rows = self.session.execute(statement=query).fetchall()
                if len(rows) == 1:
                    result.append({f"query {i}": [Status.SUCCESS, rows[0]]})
                else:
                    result.append({f"query {i}": [Status.SUCCESS, rows]})

            except DBError as e:
                if self.silent_errors:
                    result.append({f"query {i}": (Status.FAILURE, e.__str__())})
                raise e
        return result

    def query(self, query: str, params: Optional[Tuple[Any]] = None) -> QueryResponse:
        try:
            if params:
                rows = self.session.execute(query, params).fetchall()
            else:
                rows = self.session.execute(query).fetchall()
            if len(rows) == 1:
                return QueryResponse(status=Status.SUCCESS, result=rows)
            else:
                return QueryResponse(status=Status.SUCCESS, result=rows)
        except DBError as e:
            if self.silent_errors:
                return QueryResponse(status=Status.FAILURE, result=str(e))
            raise e


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
        files_in_new_directory = [
            os.path.join(dir, file) for file in filenames_list
        ]
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
