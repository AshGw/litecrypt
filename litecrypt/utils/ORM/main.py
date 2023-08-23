import sqlite3
from dataclasses import dataclass
from typing import Any, Optional, Type, Union, overload

# Ok, could've used an actual ORM but why not make one real quick ?


class Connection:
    class SQLite(sqlite3.Connection):
        ...

    class Other:
        ...


class Engine:
    def __init__(self, db_type: str):
        self.db_type = db_type

    @property
    def type(self) -> str:
        return self.db_type

    @overload
    def create(self, *args, **kwargs) -> Connection.SQLite:
        ...

    @overload
    def create(self, *args, **kwargs) -> Connection.Other:
        ...

    @overload
    def create(self, *args, **kwargs) -> Connection:
        ...

    def create(self, *args, **kwargs):
        if self.db_type == "sqlite":
            database = kwargs.pop("database")
            return Connection.SQLite(database, *args, **kwargs)
        elif self.db_type == "other":
            ...


@dataclass
class DatabaseError:
    @staticmethod
    def bind(engine: Engine) -> Union[Type[sqlite3.Error], Any]:
        if engine.type == "sqlite":
            return sqlite3.Error
        else:
            ...


class DatabaseFailure:
    def __init__(
        self,
        error: Any,
        failure: Optional[int] = None,
        possible_fix: Optional[str] = None,
    ):
        self.error = error
        self.failure = failure
        self.possible_fix = possible_fix

    def get(self):
        return {
            "failure": self.failure,
            "error": self.error,
            "possible fix": self.possible_fix,
        }


class Query:
    def __init__(self, *, engine: Engine):
        self.engine = engine

    def size(self) -> Optional[str]:
        if self.engine.type == "sqlite":
            return "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size"
        return None

    def create_table(self, *, tablename: str) -> Optional[str]:
        if self.engine.type == "sqlite":
            return (
                f"CREATE TABLE IF NOT EXISTS {tablename} "
                f"(ID INTEGER PRIMARY KEY, filename Text , content BLOB ,ref TEXT )"
            )
        return None

    def insert(self, *, tablename: str) -> Optional[str]:
        if self.engine.type == "sqlite":
            return (
                f"INSERT INTO {tablename} (filename , content ,ref) VALUES (? , ? , ?) "
            )
        return None

    def update(self, *, tablename: str, column_name: str) -> Optional[str]:
        if self.engine.type == "sqlite":
            return f"UPDATE {tablename} SET {column_name} = ? WHERE ID = ? "
        return None

    def select(
        self,
        *,
        tablename: Optional[str] = None,
        all: Optional[bool] = False,
        id: Optional[bool] = False,
        tables: Optional[bool] = False,
        ref: Optional[bool] = False,
    ) -> Optional[Union[str, None]]:
        if self.engine.type == "sqlite":
            if all and tablename and ref:
                return "SELECT * FROM stash WHERE ref = ?"
            if all and id and tablename:
                return f"SELECT * FROM {tablename} WHERE ID = ? "
            if all and ref and tablename:
                return f"SELECT * FROM {tablename} WHERE ref = ?"
            if all and tablename:
                return f"SELECT * FROM {tablename} "
            if all and tables:
                return "SELECT name FROM sqlite_master WHERE type = 'table'"
        return None

    def drop(
        self, *, tablename: Optional[str] = None, id: Optional[bool] = False
    ) -> Optional[Union[str, None]]:
        if self.engine.type == "sqlite":
            if tablename and id:
                return f"DELETE FROM {tablename} WHERE ID = ?"
            elif tablename and id is False:
                return f"DROP TABLE {tablename}"
        return None
