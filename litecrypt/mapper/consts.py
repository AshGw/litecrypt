class BaseColumns:
    id: str = "id"
    content: str = "content"
    filename: str = "filename"
    ref: str = "ref"


class EngineConstructs:
    SQLITE = "sqlite:///"
    POSTGRES = "postgresql://"
    MYSQL = "mysql://"


def remove_protocol(engine_string: str) -> str:
    colon_index = engine_string.find(":")
    return engine_string[:colon_index] if colon_index != -1 else engine_string


class EngineFor:
    SQLITE = remove_protocol(EngineConstructs.SQLITE)
    MYSQL = remove_protocol(EngineConstructs.MYSQL)
    POSTGRESQL = remove_protocol(EngineConstructs.POSTGRES)



class Status(str):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class Default(str):
    KEY = "STANDALONE"
    SPAWN_DIRECTORY = "."
    ENGINE = EngineFor.SQLITE
