from litecrypt.mapper.consts import BaseColumns, Default, EngineConstructs, EngineFor, Status


def test_engines():
    assert EngineConstructs.SQLITE == "sqlite:///"
    assert EngineConstructs.POSTGRES == "postgresql://"
    assert EngineConstructs.MYSQL == "mysql://"


def test_columns():
    assert BaseColumns.id == "id"
    assert BaseColumns.content == "content"
    assert BaseColumns.filename == "filename"


def test_status_values():
    assert Status.SUCCESS == "SUCCESS"
    assert Status.FAILURE == "FAILURE"


def test_default_values():
    assert Default.KEY == "STANDALONE"
    assert Default.SPAWN_DIRECTORY == "."
    assert Default.ENGINE == EngineFor.SQLITE
