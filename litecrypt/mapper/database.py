"""Module to interact with a database for litecrypt"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generator, List, Optional, Tuple, Union
from typing_extensions import Literal
from sqlalchemy import MetaData
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import sessionmaker

from litecrypt.mapper._types import (
    KeysContent,
    MainContent,
    QueryResult,
    SqliteSize,
    LastMod,
)
from litecrypt.mapper._consts import Default, EngineFor, Status
from litecrypt.mapper._definitions import (
    Columns,
    DatabaseFailure,
    DatabaseFailureResponse,
    DBError,
    QueryResponse,
)
from litecrypt.mapper._engines import get_engine
from litecrypt.mapper._models import Base, StashKeys, StashMain
from litecrypt.utils.exceptions.fixed import ColumnDoesNotExist


@dataclass
class Database:
    """
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
    engine_for: Literal["postgres", "sqlite", "mysql"] = field(default=Default.ENGINE)
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
    def size(self) -> Union[SqliteSize, DatabaseFailureResponse]:
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
    def last_mod(self) -> Union[LastMod, DatabaseFailureResponse]:
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
        # TODO: have this as a context manager
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

    def insert(
        self,
        filename: str,
        content: Union[MainContent, KeysContent],
        ref: str,
    ) -> None:
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

    def content(self) -> Union[Generator[QueryResult], DatabaseFailureResponse]:
        """
        Queries and returns ALL records from the current table.
        """
        try:
            result = self.session.query(self.Table).all()
            for row in result:
                yield [row.id, row.filename, row.content, row.ref]  # type: ignore
        except DBError as e:
            if self.silent_errors:
                return DatabaseFailure(error=e, failure=1).get()
            raise e

    def content_by_id(
        self, id: int
    ) -> Union[List[Union[MainContent, KeysContent]], DatabaseFailureResponse]:
        """
        Retrieve a specific record from the current table by its ID.
        """
        try:
            result = self.session.query(self.Table).filter_by(id=id).first()
            return [result.id, result.filename, result.content, result.ref]  # type: ignore
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

    def _query(self, *queries: str) -> List[Any]:  # DO NOT USE THIS OUTSIDE OF GUI
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
                rows: List[Row] = self.session.execute(query, params).fetchall()
            else:
                rows: List[Row] = self.session.execute(query).fetchall()
            if len(rows) == 1:
                return QueryResponse(status=Status.SUCCESS, result=rows)
            else:
                return QueryResponse(status=Status.SUCCESS, result=rows)
        except DBError as e:
            if self.silent_errors:
                return QueryResponse(status=Status.FAILURE, result=[str(e)])
            raise e
