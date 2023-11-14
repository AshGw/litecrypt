from typing import Any, Dict, List, Optional, Union

from sqlalchemy.exc import DatabaseError

from litecrypt.mapper.consts import BaseColumns, Status


class QueryResponse(Dict):
    def __init__(self, status: type(Status.FAILURE) = None, result: Any = None) -> None:
        super().__init__(status=status, result=result)


class DatabaseFailureResponse(Dict):
    def __init__(
        self, failure: Any = None, error: Any = None, possible_fix: Any = None
    ) -> None:
        super().__init__(failure=failure, error=error, possible_fix=possible_fix)


class DatabaseResponse(Dict):
    def __init__(
        self,
        status: str = None,
        filenames: List[str] = None,
        contents: Any = None,
        keys: List[Union[str,bytes]] = None,
    ) -> None:
        super().__init__(
            status=status, filenames=filenames, contents=contents, keys=keys
        )


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

    def fix(self) -> Union[str,None]:
        return self.possible_fix

    def debug(self) -> None:
        ...

    def additional(self) -> None:
        ...


class Columns(BaseColumns):
    @staticmethod
    def list() -> List[str]:
        l: List[str] = []
        for _, attr_value in BaseColumns.__dict__.items():
            if not _.startswith("__") and not isinstance(attr_value, type):
                l.append(attr_value)
        return l


class DBError(DatabaseError):
    ...
