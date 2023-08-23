"""Module to interact with a database for litecrypt"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Union

from litecrypt.filecrypt import CryptFile
from litecrypt.utils.consts import Colors
from litecrypt.utils.exceptions.fixed import ColumnDoesNotExist
from litecrypt.utils.ORM import DatabaseError, DatabaseFailure, Engine, Query


@dataclass
class Database:
    """
    Represents a database class with various methods to interact with a given database.

    This class provides a simplified interface to interact with a database,
    designed for various database systems.
    It includes methods to connect to the database, perform basic operations, and more.

    :param dbname: The identifier or connection details for the target database.
    :param tablename: The name of the table within the database. Default is 'stash'.
    :param db_type: The type of database to connect to. Default is 'sqlite'.
    """

    dbname: str = field()
    tablename: Optional[str] = field(default="stash")
    db_type: Optional[str] = "sqlite"
    _columns = ["filename", "content", "ref"]

    def __post_init__(self) -> None:
        """
        Initialize the database connection and cursor after object creation.

        This method establishes a connection to the database specified by the 'dbname' attribute
        and creates a cursor for executing queries. It also initializes the
        'custom_query' and 'DatabaseError'
        attributes for executing custom queries and handling database errors respectively.
        Additionally, it ensures the specified table exists in the database by invoking
        the 'create_table' method.
        """
        self.engine = Engine(db_type=self.db_type)
        self._conn = self.engine.create(database=self.dbname)
        self._c = self._conn.cursor()
        self.custom_query = Query(engine=self.engine)
        self.DatabaseError = DatabaseError.bind(engine=self.engine)
        self.create_table()

    @property
    def size(self) -> Union[float, DatabaseFailure]:
        """
        Property to get the size of the database in megabytes (MB).

        Returns:
            Union[int, DatabaseFailure]: The size of the database in MB if successful,
            or a DatabaseFailure object if an error occurs.
        """
        try:
            with self._conn:
                self._c.execute(self.custom_query.size())
                size_info = self._c.fetchone()
                size = size_info[0] / 1024 / 1024
                return size
        except self.DatabaseError as e:
            return DatabaseFailure(failure=1, error=e).get()

    @property
    def last_mod(self) -> Union[datetime, DatabaseFailure]:
        """
        Property to get the last modification time of the Database.

        Returns:
            Union[datetime, DatabaseFailure]: The last modification time as a datetime object if successful,
            or a DatabaseFailure object if an error occurs.
        """
        try:
            time_stat = datetime.fromtimestamp(os.stat(self.dbname).st_mtime)
            return time_stat
        except OSError as e:
            return DatabaseFailure(failure=1, error=e).get()

    @property
    def default_routing(self) -> str:
        """Get the default routing table of the Database class."""
        return self.tablename

    @default_routing.setter
    def default_routing(self, tablename: str):
        """Setter method to set the current table name to operate on.

        Args:
            tablename (str): The name of the table to set as the current default.
            If the table exists in the database, it will switch to it; otherwise, it will pass.
        """
        tables = [tab[0] for tab in self.show_tables()]
        if tablename in tables:
            self.tablename = tablename

    def end_session(self):
        """
         Closes the database session and commits pending transactions.

        If there is an active session, this method commits any pending transactions and then closes
        the session to the SQLite database. It's important to call this method when you're done using
        the database to ensure proper cleanup and release of resources.

        Usage example:
            >>> conn = Database('database.db')
            >>> # Perform database operations
            >>> conn.end_session()  # End the session when done
        """
        if self._conn:
            self._conn.commit()
            self._conn.close()

    def _query(self, *queries: str) -> list:
        result = []
        for i, query in enumerate(queries):
            if not isinstance(query, str):
                result.append({f"query {i}": (-1, TypeError)})
            try:
                with self._conn:
                    self._c.execute(query)
                    if self._c.rowcount == 1:
                        result.append({f"query {i}": ["SUCCESS", self._c.fetchone()]})
                    else:
                        result.append({f"query {i}": ["SUCCESS", self._c.fetchall()]})

            except self.DatabaseError as e:
                result.append({f"query {i}": ("FAILURE", e.__str__())})
        return result

    def query(self, query: str, params: Optional[tuple] = None) -> dict:
        """Executes an SQL query with parameters and returns the result.

        Args:
            query (str): The SQL query to execute.
            params (tuple): The parameters to be passed to the query.

        Returns:
            dict: A dictionary containing the query execution status, and the result if successful.
            If the query fails, it includes the status as "FAILURE" and the error information.
        """
        try:
            with self._conn:
                if params:
                    self._c.execute(query, params)
                else:
                    self._c.execute(query)
                if self._c.rowcount == 1:
                    return {"status": "SUCCESS", "result": self._c.fetchone()}
                else:
                    return {"status": "SUCCESS", "result": self._c.fetchall()}
        except self.DatabaseError as e:
            return {"status": "FAILURE", "result": e.__str__()}

    def create_table(
        self, tablename: Optional[str] = None
    ) -> Union[int, DatabaseFailure]:
        """Creates a new table in the database with the given table name.
        If the table name is not provided, it uses the default table name: 'stash'.

        Args:
            tablename (str, optional): The name of the table to create. Defaults to None.

        Returns:
            Union[int, DatabaseFailure]: Returns 1 if the table creation is successful,
            or a DatabaseFailure object
            if an error occurs during table creation.
        """
        if tablename is None:
            try:
                with self._conn:
                    self._c.execute(
                        self.custom_query.create_table(tablename=self.tablename)
                    )
                return 1
            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

        else:
            try:
                with self._conn:
                    self._c.execute(self.custom_query.create_table(tablename=tablename))
                    self.tablename = tablename
                return 1

            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

    def insert(
        self,
        filename: str,
        content: Union[bytes, str],
        ref: Optional[str] = "STANDALONE",
        tablename: Optional[str] = None,
    ) -> Union[int, DatabaseFailure]:
        """Inserts a new row into the specified table or the default table.

        Args:
            filename (str): The name of the file to be inserted.
            content (Union[bytes, str]): The content to be stored in the row.
            ref (str, optional): The ref associated with the row. Defaults to "STANDALONE".
            tablename (str, optional): The name of the table to insert into. Defaults to None.

        Returns:
            Union[int, DatabaseFailure]: Returns 1 if the insertion is successful,
            or a DatabaseFailure object
            if an error occurs during insertion.
        """
        if tablename is None:
            try:
                with self._conn:
                    self._c.execute(
                        self.custom_query.insert(tablename=self.tablename),
                        (filename, content, ref),
                    )
                return 1
            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

        else:
            try:
                with self._conn:
                    self._c.execute(
                        self.custom_query.insert(tablename=tablename),
                        (filename, content, ref),
                    )
                return 1
            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

    def update(
        self,
        column_name: str,
        new_column_val: str,
        id_: int,
        tablename: Optional[str] = None,
    ) -> Union[int, DatabaseFailure]:
        """Updates a specific column of a row based on the given ID in the specified table
        or the default table
        if no argument is passed.

        :param column_name: The name of the column to be updated must be in the attribute '_columns'.
        :param new_column_val: The new value to be assigned to the column.
        :param id_: The ID of the row to be updated.
        :param tablename: The name of the table to update the row in. Default is None for the default table.
        :return: 1 if the update was successful, or a DatabaseFailure object if there was an error.
        """
        if column_name.lower() not in ["filename", "content", "ref"]:
            raise ColumnDoesNotExist()
        if tablename is None:
            try:
                with self._conn:
                    self._c.execute(
                        self.custom_query.update(
                            tablename=self.tablename, column_name=column_name
                        ),
                        (new_column_val, id_),
                    )
                    return 1

            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

        else:
            try:
                with self._conn:
                    self._c.execute(
                        self.custom_query.update(
                            tablename=tablename, column_name=column_name
                        ),
                        (new_column_val, id_),
                    )
                    return 1

            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

    def content(
        self, tablename: Optional[str] = None
    ) -> Union[Generator, DatabaseFailure]:
        """Yields all rows from the specified table, or the default table
        if no arguments are passed ( as a Generator object ) ."""
        if tablename is None:
            try:
                with self._conn:
                    self._c.execute(
                        self.custom_query.select(tablename=self.tablename, all=True)
                    )
                    yield from self._c.fetchall()

            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

        else:
            try:
                with self._conn:
                    self._c.execute(
                        self.custom_query.select(tablename=tablename, all=True)
                    )
                    yield from self._c.fetchall()

            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

    def content_by_id(
        self, id_: int, tablename: Optional[str] = None
    ) -> Union[Generator, DatabaseFailure]:
        """
        Yields a specific row from the specified table or the default table based on a given ID.

        Args:
            id_ (int): The ID of the row to retrieve.
            tablename (Optional[str]): The name of the table to retrieve the row from.
            If None, the default table is used.

        :returns:
            Generator: A generator yielding the row from the specified table,
             or a DatabaseFailure object if there's an error.
        """
        if tablename is None:
            try:
                with self._conn:
                    self._c.execute(
                        self.custom_query.select(
                            tablename=self.tablename, id=True, all=True
                        ),
                        (id_,),
                    )
                    yield from self._c.fetchall()

            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

        else:
            try:
                with self._conn:
                    self._c.execute(
                        self.custom_query.select(
                            tablename=tablename, id=True, all=True
                        ),
                        (id_,),
                    )
                    yield from self._c.fetchall()

            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

    def content_all(self, *tablenames: str) -> Union[Generator, DatabaseFailure]:
        """
        Yields all rows from specified tables or the default table.

        Args:
            *tablenames (str): Names of the tables to retrieve rows from 0 or many.

        :returns:
            Union[Generator, DatabaseFailure]: Generator yielding rows from specified tables,
             or a DatabaseFailure object if there's an error.
        """
        if tablenames:
            try:
                for tablename in tablenames:
                    with self._conn:
                        self._c.execute(
                            self.custom_query.select(tablename=tablename, all=True)
                        )
                        for row in self._c.fetchall():
                            yield {tablename: row}

            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

        else:
            try:
                with self._conn:
                    self._c.execute(
                        self.custom_query.select(tablename=self.tablename, all=True)
                    )
                    for row in self._c.fetchall():
                        yield {self.tablename: row}

            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

    def show_tables(self) -> Union[Generator, DatabaseFailure]:
        """
        Yields the names of all tables in the Database.

        Yields:
            Union[Generator, DatabaseFailure]: Generator yielding table names,
             or a DatabaseFailure object if there's an error.
        """
        try:
            with self._conn:
                self._c.execute(self.custom_query.select(tables=True, all=True))
                yield from self._c.fetchall()

        except self.DatabaseError as e:
            return DatabaseFailure(failure=1, error=e).get()

    def drop_table(self, *tablenames: str) -> Union[int, DatabaseFailure]:
        """
        Drops specific table(s) in the Database.

        Args:
            *tablenames (str): Name(s) of the table(s) to drop.

        Returns:
            Union[int, DatabaseFailure]: 1 if successful,
            or a DatabaseFailure object if there's an error.
        """
        if tablenames:
            try:
                with self._conn:
                    for tablename in tablenames:
                        self._c.execute(self.custom_query.drop(tablename=tablename))
                return 1
            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

        else:
            try:
                with self._conn:
                    self._c.execute(self.custom_query.drop(tablename=self.tablename))
                return 1

            except self.DatabaseError as e:
                return DatabaseFailure(failure=1, error=e).get()

    def drop_all_tables(self) -> Union[int, DatabaseFailure]:
        """
        Drops ALL tables in the Database.

        Returns:
            Union[int, DatabaseFailure]: 1 if successful,
            or a DatabaseFailure object if there's an error.
        """
        try:
            with self._conn:
                self._c.execute(self.custom_query.select(tables=True, all=True))
                for table_inf in self._c.fetchall():
                    self._c.execute(self.custom_query.drop(tablename=table_inf[0]))
                return 1

        except self.DatabaseError as e:
            return DatabaseFailure(failure=1, error=e).get()

    def drop_content(
        self, id_: int, tablename: Optional[str] = None
    ) -> Union[int, DatabaseFailure]:
        """
        Deletes a row from the specified table or the default table based on the given ID.

        Args:
            id_ (int): The ID of the row to be deleted.
            tablename (str, optional): The name of the table to delete from.
            Default is None (uses default table).

        Returns:
            Union[int, DatabaseFailure]: 1 if successful, or a DatabaseFailure object if there's an error.
        """
        try:
            with self._conn:
                if tablename is None:
                    self._c.execute(
                        self.custom_query.drop(tablename=self.tablename, id=True),
                        (id_,),
                    )
                else:
                    self._c.execute(
                        self.custom_query.drop(tablename=tablename, id=True), (id_,)
                    )
            return 1

        except self.DatabaseError as e:
            return DatabaseFailure(failure=1, error=e).get()


def reference_linker(
    *,
    connection: Database,
    key_reference: str,
    get_filename: Optional[bool] = False,
    get_content_or_key: Optional[bool] = False,
    get_all: Optional[bool] = False,
    tablename: Optional[str] = "stash",
) -> Union[str, bytes, List[Any]]:
    """
    Retrieve specific information from the database linked with a key_reference value.

    This function allows you to retrieve various types of data associated with a given
    key reference value from the specified database connection.

    Args:
        connection (Database): A connected Database object.
        key_reference (str): The key reference to link with.
        get_filename (bool, optional): Retrieve the filename(s) associated with the key reference.
            Default is False.
        get_content_or_key (bool, optional): Retrieve content(s) associated with the key reference
            if connected to the main database, or retrieve key(s) if connected to the keys database.
            Default is False.
        get_all (bool, optional): Retrieve all filenames or all contents/keys.
            If True, fetches all matches; otherwise, only the first match is retrieved.
            Default is False.
        tablename (str, optional): The name of the table in the database. Default is 'stash'.

    Returns:
        Union[str, bytes, List[Union[str, bytes]]]: Depending on the options, returns:
            * If 'get_filename' is True, retrieved filename(s) (str) or an empty string.
            * If 'get_content_or_key' is True, retrieved content(s) or key(s) (str | bytes) or None.
            * If get_all is True, returns a list of retrieved items; otherwise, a single item.

    Note:
        If retrieving all content, consider memory consumption for large files, as data will be stored
        in memory until released. This may lead to slower performance for large files.
    """
    engine = connection.engine
    if get_filename and get_content_or_key:
        raise ValueError(
            "Cannot select both 'get_filename' and 'get_content_or_key' simultaneously."
        )
    if not get_filename and not get_content_or_key:
        raise ValueError("Select either 'get_filename' or 'get_content_or_key'.")
    if get_all:
        data_list = connection.query(
            Query(engine=engine).select(tablename=tablename, all=True, ref=True),
            (key_reference,),
        )["result"]
        all_matches_list = [(e[1], e[2], e[3]) for e in data_list]
        # e[1] is the file name / e[2] is the file content / e[3] is the key reference value

        # each trio is representative of the info of one file at once
        filenames_list = [trio[0] for trio in all_matches_list]
        file_content_or_keys_list = [trio[1] for trio in all_matches_list]

        return file_content_or_keys_list if get_content_or_key else filenames_list

    elif not get_all:
        data = connection.query(
            Query(engine=engine).select(tablename=tablename, all=True, ref=True),
            (key_reference,),
        )["result"][0]
        return data[2] if get_content_or_key else data[1]
        # conn[2] == content column content containing the first content it matches
        # conn[1] == filename column containing the first filename it matches


def spawn(
    *,
    main_connection: Database,
    keys_connection: Database,
    key_reference: str,
    tablename: Optional[str] = "stash",
    directory: Optional[str] = ".",
    get_all: Optional[bool] = False,
    ignore_duplicate_files: Optional[bool] = False,
    echo: Optional[bool] = False,
) -> Dict[str, Any]:
    """
    Retrieve file content and related data from specified databases and create files
    in the designated directory.

    Depending on the parameters, this function can fetch a single file or multiple
    files associated with the provided key_reference.
    The fetched files are then created in the specified directory.

    Args:
        main_connection (Database): Connection to the main database.
        keys_connection (Database): Connection to the keys' database.
        key_reference (str): The reference key to link with.
        tablename (str, optional): The name of the table in the databases. Default is 'stash'.
        directory (str, optional): The directory where files will be created.
        Default is the current directory.
        get_all (bool, optional): Retrieve and create all files associated with the key_reference.
            Default is False, indicating retrieval of a single file.
        ignore_duplicate_files (bool, optional): When True, duplicate filenames
        are ignored during creation.
            Default is False.
        echo (bool, optional): Whether to print result information. Default is False.

    Returns:
        dict: A dictionary containing the outcome of the retrieval and creation process.
            - 'status' (str): The operation status, either 'SUCCESS' or 'FAILURE'.
            - 'filenames' (List[str]): The names of the created files.
            - 'contents' (List[Any]): The contents of the created files.
            - 'keys' (List[str]): The associated encryption/decryption keys.

    """

    if main_connection is keys_connection:
        raise ValueError("Main and keys databases must be different")

    if not os.path.isdir(directory):
        raise ValueError("Provide a valid directory")
    result = {
        "status": "FAILURE",
        "filenames": None,
        "contents": None,
        "keys": None,
    }

    if get_all:
        try:
            keys_list = reference_linker(
                connection=keys_connection,
                key_reference=key_reference,
                get_content_or_key=True,
                get_all=True,
                tablename=tablename,
            )
            for key in keys_list:
                if CryptFile.key_verify(key) != 1 and key != "STANDALONE":
                    raise ValueError(
                        "Invalid key for cryptographic usage detected, mismatch found"
                        " check if Database object placement is correct."
                    )

            contents_list = reference_linker(
                connection=main_connection,
                key_reference=key_reference,
                get_content_or_key=True,
                get_all=True,
                tablename=tablename,
            )
            paths_list = reference_linker(
                connection=main_connection,
                key_reference=key_reference,
                get_filename=True,
                get_all=True,
                tablename=tablename,
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

            # The creation of the extracted files in the specified directory
            full_paths_list = [
                os.path.join(directory, os.path.split(path)[1])
                for path in filenames_list
            ]
            for full_path, content in zip(full_paths_list, contents_list):
                CryptFile.make_file(filename=full_path, content=content)
                if echo:
                    print(
                        f"{Colors.GREEN}{full_path} has been spawned successfully.{Colors.RESET}"
                    )
            # done with that
            files_in_new_directory = []
            for file in filenames_list:
                files_in_new_directory.append(os.path.join(directory, file))

            result = {
                "status": "SUCCESS",
                "filenames": [os.path.join(directory, file) for file in filenames_list],
                "contents": contents_list,
                "keys": keys_list,
            }

        except Exception as e:
            raise e

        _echo_dict(echo=echo, dictionnary=result)
        return result

    else:
        try:
            content = reference_linker(
                connection=main_connection,
                key_reference=key_reference,
                get_content_or_key=True,
                tablename=tablename,
            )
            path = reference_linker(
                connection=main_connection,
                key_reference=key_reference,
                get_filename=True,
                tablename=tablename,
            )
            filename = os.path.split(path)[1]

            key = reference_linker(
                connection=keys_connection,
                key_reference=key_reference,
                get_content_or_key=True,
                tablename=tablename,
            )

            if CryptFile.key_verify(key) != 1 and key != "STANDALONE":
                raise ValueError(
                    "Invalid key, check if Database object placement is correct."
                )

            full_path = os.path.join(directory, filename)

            CryptFile.make_file(filename=full_path, content=content)

            if echo:
                print(
                    f"{Colors.GREEN}{filename} has been successfully spawned in the directory: "
                    f"{directory}{Colors.RESET}"
                )

            result = {
                "status": "SUCCESS",
                "filenames": [
                    os.path.join(directory, filename)
                ],  # made lists out of them for easy exec
                "contents": [content],
                "keys": [key],
            }
        except BaseException:
            pass

        _echo_dict(echo=echo, dictionnary=result)

        return result


def _echo_dict(dictionnary: dict, echo: Optional[bool] = False):
    if echo:
        for key, value in dictionnary.items():
            key_colored = Colors.YELLOW + key + Colors.RESET

            if key == "status" and value == "SUCCESS":
                value_colored = Colors.GREEN + str(value) + Colors.RESET
            elif key == "status" and value == "FAILURE":
                value_colored = Colors.RED + str(value) + Colors.RESET
            else:
                value_colored = Colors.CYAN + str(value) + Colors.RESET

            print(f"{key_colored}: {value_colored}")
