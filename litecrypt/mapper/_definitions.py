from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from sqlalchemy.exc import DatabaseError

from litecrypt.mapper._consts import BaseColumns, Status
from litecrypt.mapper._types import QueryResult, FileContent


class Columns(BaseColumns):
    @staticmethod
    def list() -> List[str]:
        columns_list: List[str] = []
        for _, attr_value in BaseColumns.__dict__.items():
            if not _.startswith("__") and not isinstance(attr_value, type):
                columns_list.append(attr_value)
        return columns_list


class DatabaseResponse(Dict):
    def __init__(
        self,
        status: Optional[str] = None,
        filenames: Optional[List[str]] = None,
        contents: Optional[FileContent,Union[List[FileContent]]] = None,
        keys: Optional[List[Union[str, bytes]]] = None,
    ) -> None:
        super().__init__(
            status=status, filenames=filenames, contents=contents, keys=keys
        )


class QueryResponse(Dict):
    def __init__(
        self,
        status: Optional[type(Status.FAILURE)] = None,
        result: Optional[QueryResult] = None,
    ) -> None:
        super().__init__(status=status, result=result)


class DatabaseFailureResponse(Dict):
    def __init__(
        self,
        failure: Optional[Any] = None,
        error: Optional[BaseException] = None,
        possible_fix: Optional[str] = None,
    ) -> None:
        super().__init__(failure=failure, error=error, possible_fix=possible_fix)


class DatabaseFailure:
    def __init__(
        self,
        error: BaseException,
        failure: Optional[int] = None,
        possible_fix: Optional[str] = None,
    ) -> None:
        self.error = error
        self.failure = failure
        self.possible_fix = possible_fix

    def get(self) -> DatabaseFailureResponse:
        return DatabaseFailureResponse(
            failure=self.failure, error=self.error, possible_fix=self.fix()
        )

    def fix(self) -> Union[str, None]:
        return self.possible_fix

    def debug(self) -> None:
        ...

    def additional(self) -> None:
        ...


class DBError(DatabaseError):
    ...
