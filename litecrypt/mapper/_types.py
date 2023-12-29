from __future__ import annotations

from typing_extensions import ParamSpec
from typing import Type, Union

EngineParams = ParamSpec('EngineParams')
FileContent = Type[Union[str,bytes]]
