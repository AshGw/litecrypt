from re import sub


class BaseColumns:
    id: str = "id"
    content: str = "content"
    filename: str = "filename"
    ref: str = "ref"


class EngineConstructs:
    SQLITE = "sqlite:///"
    POSTGRES = "postgresql://"
    MYSQL = "mysql://"


def remove_protocol(engine_string: str):
    # Use regex to remove ":" and anything after it
    return sub(r":.*", "", engine_string)


class Status(str):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class Default(str):
    KEY = "STANDALONE"
    SPAWN_DIRECTORY = "."
