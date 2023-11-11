from typing import Any, Dict, List, Optional

from sqlalchemy import BLOB, Column, Integer, MetaData, String
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from litecrypt.mapper.consts import BaseColumns, Status

Base = declarative_base()


class LcMetaData(MetaData):
    ...


class LcSessionMaker(sessionmaker):
    ...


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


class Columns(BaseColumns):
    @staticmethod
    def list():
        l: List[str] = []
        for _, attr_value in BaseColumns.__dict__.items():
            if not _.startswith("__") and not isinstance(attr_value, type):
                l.append(attr_value)
        return l


class DatabaseResponse(Dict):
    def __init__(
        self,
        status: str = None,
        filenames: List[str] = None,
        contents: Any = None,
        keys: list[str] = None,
    ):
        super().__init__(
            status=status, filenames=filenames, contents=contents, keys=keys
        )


class QueryResponse(Dict):
    def __init__(self, status: Status = None, result: Any = None):
        super().__init__(status=status, result=result)


class DatabaseFailureResponse(Dict):
    def __init__(
        self, failure: Any = None, error: Any = None, possible_fix: Any = None
    ):
        super().__init__(failure=failure, error=error, possible_fix=possible_fix)


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
        return DatabaseFailureResponse(
            failure=self.failure, error=self.error, possible_fix=self.fix()
        )

    def fix(self):
        return (self.possible_fix,)

    def debug(self):
        ...

    def additional(self):
        ...


class DBError(DatabaseError):
    ...
