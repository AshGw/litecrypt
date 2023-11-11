from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from litecrypt.mapper.consts import EngineConstructs, remove_protocol


class EngineFor:
    SQLITE = remove_protocol(EngineConstructs.SQLITE)
    MYSQL = remove_protocol(EngineConstructs.MYSQL)
    POSTGRESQL = remove_protocol(EngineConstructs.POSTGRES)


def get_engine(
    url: str, engine_for: str = EngineFor.SQLITE, echo: Optional[bool] = False, **kwargs
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


if __name__ == "__main__":
    print(EngineFor.POSTGRESQL)
