from db.db import (
    connect,
    close_connection,
    desc_table,
    insert,
    get_all,
    get,
    update,
    delete,
    delete_all,
    drop_table,
    create_table,
    drop_db,
    create_db,
)
from service.service import ReDB_HOST, ReDB_PORT, ReDB_DEFAULT_DB, ReDB_USER, ReDB_PASS
import pytest

database = "pytest_schema"
table = "pytest_table"
empty_table = "pytest_empty_table"
keys = [
    "actors",
    "categories",
    "director",
    "id",
    "name",
    "release-date",
    "runtime",
    "storyline",
    "writer",
    "year",
]
unique_id = ""


@pytest.fixture(scope="session", autouse=True)
def configure_database():
    connection = connect(ReDB_HOST, ReDB_PORT, user=ReDB_USER, password=ReDB_PASS)
    create_table(database, empty_table, connection)
    delete_all(database, table, connection)
    data = [
        {
            "name": "The Dark Knight Rises",
            "year": 2012,
            "runtime": 163,
            "categories": ["adventure", "thriller"],
            "release-date": "2012-07-20",
            "director": "Christopher Nolan",
            "writer": [
                "Jonathan Nolan",
                "David S. Goyer",
                "Christopher Nolan",
                "Bob Kane",
            ],
            "actors": ["Christian Bale", "Tom Hardy", "Anne Hathway"],
            "storyline": "Eight years after the Joker's reign of anarchy,"
            " the Dark Knight, with the help of the enigmatic"
            " Catwoman, is forced from his imposed exile to save"
            " Gotham City, now on the edge of total annihilation,"
            " from the brutal guerrilla terrorist Bane.",
        },
        {
            "name": "Avengers: Infinity War",
            "year": 2018,
            "runtime": 149,
            "categories": ["Action", "Adventure", "Fantasy"],
            "release-date": "2018-04-27",
            "director": ["Anthony Russo", "Joe Russo"],
            "writer": ["Christopher Markus", "Stephen McFeely"],
            "actors": [
                "Robert Downey Jr.",
                "Chris Hemsworth",
                "Mark Ruffalo",
                "Chris Evans",
                "Scarlett Johansson",
                "Benedict Cumberbatch",
            ],
            "storyline": "The Avengers and their allies must be willing to"
            " sacrifice all in an attempt to defeat the"
            " powerful Thanos before his blitz of devastation"
            " and ruin puts an end to the universe.",
        },
    ]

    result = insert(database, table, data, connection)

    global unique_id
    unique_id = result["generated_keys"][0]


@pytest.fixture
def rethink_connect():
    return connect(ReDB_HOST, ReDB_PORT, user=ReDB_USER, password=ReDB_PASS)


def test_successful_connection():
    connection = connect(
        ReDB_HOST, ReDB_PORT, ReDB_DEFAULT_DB, user=ReDB_USER, password=ReDB_PASS
    )
    assert connection is not None


def test_unsuccessful_connection():
    connection = connect("localhost", 1234)
    assert connection is None


def test_successful_disconnection():
    connection = connect(
        ReDB_HOST, ReDB_PORT, ReDB_DEFAULT_DB, user=ReDB_USER, password=ReDB_PASS
    )
    assert connection is not None
    assert close_connection(connection) is True


# TODO Encontrar um jeito melhor de testar erros de fechamento de conexão
def test_unsuccessful_disconnection():
    connection = object
    assert close_connection(connection) is False


def test_successful_insertion(rethink_connect):
    data = {
        "name": "A Star is Born",
        "year": 2018,
        "runtime": 135,
        "categories": ["drama", "music", "romance"],
        "release-date": "2018-09-07",
        "director": "Bradley Cooper",
        "writer": ["Lady Gaga", "Bradley Cooper", "Sam Elliot"],
        "actors": [
            "Eric Roth",
            "Bradley Cooper",
            "Will Fetters",
            "William A. Wellman",
            "Robert Carson",
        ],
        "storyline": "Seasoned musician Jackson Maine (Bradley Cooper) "
        "discovers-and falls in love with-struggling artist "
        "Ally (Gaga). She has just about given up on her "
        "dream to make it big as a singer - until Jack coaxes "
        "her into the spotlight. But even as Ally's career "
        "takes off, the personal side of their relationship is "
        "breaking down, as Jack fights an ongoing battle with "
        "his own internal demons. Written by Warner Bros.",
    }

    result = insert(database, table, data, rethink_connect)

    assert result is not None
    assert result["inserted"] == 1


def test_unsuccessful_insertion(rethink_connect):
    global unique_id
    data = {
        "name": "The Dark Knight Rises",
        "year": 2012,
        "runtime": 163,
        "categories": ["adventure", "thriller"],
        "release-date": "2012-07-20",
        "director": "Christopher Nolan",
        "writer": ["Jonathan Nolan", "David S. Goyer", "Christopher Nolan", "Bob Kane"],
        "actors": ["Christian Bale", "Tom Hardy", "Anne Hathway"],
        "storyline": "Eight years after the Joker's reign of anarchy,"
        " the Dark Knight, with the help of the enigmatic"
        " Catwoman, is forced from his imposed exile to save"
        " Gotham City, now on the edge of total annihilation,"
        " from the brutal guerrilla terrorist Bane.",
    }
    data.update({"id": unique_id})
    result = insert(database, table, data, rethink_connect)

    assert result is not None
    assert len(result) == 0


def test_successful_desc_table(rethink_connect):
    result = desc_table(database, table, rethink_connect)
    assert result is not None
    assert len(result) > 0 and len(result) == 10
    assert set(keys).difference(result) == set()


def test_unsuccessful_desc_table(rethink_connect):
    result = desc_table(database, empty_table, rethink_connect)
    assert result is not None
    assert len(result) == 0
    assert result == set()


def test_successful_get_all(rethink_connect):
    result = get_all(database, table, rethink_connect)
    assert result is not None
    assert len(result) == 3


def test_unsuccessful_get_all(rethink_connect):
    result = get_all(database, empty_table, rethink_connect)
    assert result is not None
    assert len(result) == 0
    assert result == {}


def test_successful_get(rethink_connect):
    global unique_id
    result = get(database, table, unique_id, rethink_connect)
    assert result is not None
    assert len(result) == 10
    assert result["name"] == "The Dark Knight Rises"
    assert set(keys).difference(result) == set()


def test_unsuccessful_get(rethink_connect):
    global unique_id
    result = get(database, empty_table, unique_id, rethink_connect)
    assert result is not None
    assert len(result) == 0
    assert result == {}


def test_successful_update(rethink_connect):
    global unique_id
    update_statement = {"runtime": 164}
    result = update(database, table, unique_id, update_statement, rethink_connect)
    assert result is not None
    assert len(result) == 2
    assert result["objects_updated"] == 1
    assert result["changes"][0]["new_val"]["runtime"] == 164 \
        and result["changes"][0]["old_val"]["runtime"] == 163


def test_unsuccessful_update(rethink_connect):
    global unique_id
    update_statement = {"runtime": 164}
    result = update(database, empty_table, unique_id, update_statement, rethink_connect)
    assert result is not None
    assert len(result) == 1
    assert result["objects_updated"] == 0


def test_successful_delete(rethink_connect):
    global unique_id
    result = delete(database, table, unique_id, rethink_connect)
    assert result is not None
    assert len(result) == 1
    assert result["objects_deleted"] == 1


def test_unsuccessful_delete(rethink_connect):
    global unique_id
    result = delete(database, empty_table, unique_id, rethink_connect)
    assert result is not None
    assert len(result) == 1
    assert result["objects_deleted"] == 0


def test_successful_delete_all(rethink_connect):
    result = delete_all(database, table, rethink_connect)
    assert result is not None
    assert len(result) == 1
    assert result["objects_deleted"] == 2


def test_unsuccessful_delete_all(rethink_connect):
    result = delete_all(database, empty_table, rethink_connect)
    assert result is not None
    assert len(result) == 1
    assert result["objects_deleted"] == 0


def test_successful_drop_table(rethink_connect):
    result = drop_table(database, empty_table, rethink_connect)
    assert result is not None
    assert len(result) == 1
    assert result["tables_dropped"] == 1


def test_unsuccessful_drop_table(rethink_connect):
    result = drop_table(database, empty_table, rethink_connect)
    assert result is not None
    assert len(result) == 1
    assert result["tables_dropped"] == 0


def test_successful_create_table(rethink_connect):
    result = create_table(database, empty_table, rethink_connect)
    assert result is not None
    assert len(result) == 1
    assert result["tables_created"] == 1


def test_unsuccessful_create_table(rethink_connect):
    result = create_table(database, empty_table, rethink_connect)
    assert result is not None
    assert len(result) == 1
    assert result["tables_created"] == 0


def test_successful_create_database(rethink_connect):
    test_database = "pytest_db_test"
    result = create_db(test_database, rethink_connect)
    assert result is not None
    assert len(result) == 1
    assert result["dbs_created"] == 1


def test_unsuccessful_create_database(rethink_connect):
    test_database = "pytest_db_test"
    result = create_db(test_database, rethink_connect)
    assert result is not None
    assert len(result) == 1
    assert result["dbs_created"] == 0


def test_successful_drop_database(rethink_connect):
    test_database = "pytest_db_test"
    result = drop_db(test_database, rethink_connect)
    assert result is not None
    assert len(result) == 2
    assert result["dbs_dropped"] == 1
    assert result["tables_dropped"] == 0


def test_unsuccesful_drop_database(rethink_connect):
    test_database = "pytest_db_test"
    result = drop_db(test_database, rethink_connect)
    assert result is not None
    assert len(result) == 2
    assert result["dbs_dropped"] == 0
    assert result["tables_dropped"] == 0
