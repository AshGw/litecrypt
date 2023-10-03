from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from litecrypt.mapper.models import Constructs


def get_engine(
    url: str, engine_for: str = "sqlite", echo: Optional[bool] = False, **kwargs
) -> Engine:
    engine = engine_for.lower().strip()
    if engine == "sqlite":
        engine_type = Constructs.SQLITE + url
    elif engine == "postgres":
        # Assuming db_url is in the format 'username:password@host:port/database'
        engine_type = Constructs.POSTGRES + url
    elif engine == "mysql":
        # Also assuming db_url is in the format 'username:password@host:port/database'
        engine_type = Constructs.MYSQL + url
    else:
        raise ValueError(f"Unsupported engine type: {engine}")
    return create_engine(engine_type, echo=echo, **kwargs)
