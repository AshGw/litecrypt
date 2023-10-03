from typing import Any, Optional

from sqlalchemy import BLOB, Column, Integer, String
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StashBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    ref = Column(String, index=True)


class StashMain(StashBase):
    __tablename__ = "stashMain"
    content = Column(BLOB)


class StashKeys(StashBase):
    __tablename__ = "stashKeys"
    content = Column(String)


class Constructs:
    SQLITE = "sqlite:///"
    POSTGRES = "postgresql//"
    MYSQL = "mysql://"


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


class DBError(DatabaseError):
    ...
