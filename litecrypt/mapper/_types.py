from __future__ import annotations

from typing import Type, Union

from typing_extensions import ParamSpec

EngineParams = ParamSpec("EngineParams")
FileContent = Type[Union[str, bytes]]
