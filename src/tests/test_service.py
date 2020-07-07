from service.service import (
    test_database_connection,
    configure_database,
    disconnect_database,
    health_check,
)
from service.service import ReDB_PORT, ReDB_HOST, ReDB_USER, ReDB_PASS
from db.db import connect
from rethinkdb import net
import pytest
import http


unknown_host = "1.1.1.1"
database = "pytest_schema"


@pytest.fixture
def rethink_connect():
    return connect(ReDB_HOST, ReDB_PORT, user=ReDB_USER, password=ReDB_PASS)


def test_successful_database_connection():
    result = test_database_connection(
        ReDB_HOST, ReDB_PORT, user=ReDB_USER, password=ReDB_PASS
    )
    assert result is not None
    assert result is True


def test_unsuccessful_database_connection():
    result = test_database_connection(unknown_host, ReDB_PORT)
    assert result is not None
    assert result is False


def test_successful_configure_database():
    result = configure_database(
        ReDB_HOST, ReDB_PORT, database, user=ReDB_USER, password=ReDB_PASS
    )
    assert result is not None
    assert result.db == database
    assert result.host == ReDB_HOST
    assert result.port == int(ReDB_PORT)
    assert result._conn_type == net.ConnectionInstance


def test_unsuccessful_configure_database():
    result = configure_database(unknown_host, ReDB_PORT)
    assert result is not None
    assert result is False


def test_successful_database_disconnection(rethink_connect):
    result = disconnect_database(rethink_connect)
    assert result is not None
    assert result is True


def test_unsuccessful_database_disconnection():
    conn = None
    result = disconnect_database(conn)
    assert result is not None
    assert result is False


def test_successful_health_check():
    path = "/health"
    message = "Server Up and Running!\n"
    result = health_check(path, None)
    assert result is not None
    assert len(result) == 3
    assert result[0] is http.HTTPStatus.OK
    assert result[1] == []
    assert result[2].decode("utf-8") == message
