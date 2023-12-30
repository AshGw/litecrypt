from __future__ import annotations

from typing import Union, List, TypeVar
from datetime import datetime
from typing_extensions import ParamSpec
from sqlalchemy.engine.row import Row

_T = TypeVar("_T")

EngineParams = ParamSpec("EngineParams")
FileContent = Union[str, bytes]
MainContent = bytes
KeysContent = str
FetchResult = Union[List[Row], None]
QueryResult = List[_T]
SqliteSize = Union[float, None]
LastMod = Union[datetime, None]
