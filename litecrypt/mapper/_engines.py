from __future__ import annotations

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from litecrypt.mapper._consts import EngineConstructs, EngineFor
from litecrypt.mapper._types import EngineParams


def get_engine(
    url: str,
    engine_for: Optional[str] = EngineFor.SQLITE,
    echo: Optional[bool] = False,
    **kwargs: EngineParams,
) -> Engine:
    engine = engine_for.lower().strip()
    if engine == EngineFor.SQLITE:
        engine_type = EngineConstructs.SQLITE + url
    elif engine == EngineFor.POSTGRESQL:
        # Assuming db_url is in the format 'username:password@host:port/database'
        engine_type = EngineConstructs.POSTGRES + url
    elif engine == EngineFor.MYSQL:
        # Also assuming db_url is in the format 'username:password@host:port/database'
        engine_type = EngineConstructs.MYSQL + url
    else:
        raise ValueError(f"Unsupported engine type: {engine}")
    return create_engine(engine_type, echo=echo, **kwargs)
