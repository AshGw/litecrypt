from __future__ import annotations

from typing import Optional, Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from litecrypt.mapper._consts import EngineConstructs, EngineFor


def get_engine(
    url: str,
    engine_for: Optional[str] = EngineFor.SQLITE,
    echo: Optional[bool] = False,
    **kwargs: Any,
) -> Engine:
    engine = engine_for.lower().strip()
    if engine == EngineFor.SQLITE:
        engine_type = EngineConstructs.SQLITE + url
    elif engine == EngineFor.POSTGRESQL:
        engine_type = EngineConstructs.POSTGRES + url
    elif engine == EngineFor.MYSQL:
        engine_type = EngineConstructs.MYSQL + url
    else:
        raise ValueError(f"Unsupported engine type: {engine}")
    return create_engine(engine_type, echo=echo, **kwargs)
