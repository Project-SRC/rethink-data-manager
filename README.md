# Rethink Data Manager

[![codecov](https://codecov.io/gh/Project-SRC/rethink-data-manager/branch/develop/graph/badge.svg)](https://codecov.io/gh/Project-SRC/rethink-data-manager)
[![Build Status](https://travis-ci.com/Project-SRC/rethink-data-manager.svg?branch=develop)](https://travis-ci.com/Project-SRC/rethink-data-manager)

**RDM (Rethink Data Manager)** is a service to comunicate other systems to the database of the project, using a RethinkDB. An interface with database operations are available through a websocket server.

## Parameters

**RDM** runs in the [websocket](https://tools.ietf.org/html/rfc6455) format, so it expects a message on the communication channel, the initial message must be an __JSON__ in the following format:

```shell
{
    "id": "4bb803f2-68d8-4464-879f-3bf65aa9cc9f", # UUID packet identifier
    "type": "rethink-manager-call", # Expected call type for RDM, different calls will be ignored
    "payload": { # Inside the payload you will have the data that will be used for database transactions. They will vary according to the call
        "database": "test", # The operation database schema (required)
        "table": "test", # The operation database table (required)
        "data": { # JSON object of the operation (insert and update)
            "key": "value",
            "other_key": 2
        },
        "identifier": "a02263d6-fb4e-4cc0-ab81-0684fbe72df8" # Operation identifier (selection or deletion)
    },
    "time": "2019-05-18T20:59:26.346996Z" # Request date and time in RFC3339 format
}
```

## Dependencies

- [Websockets 8.1 (Python)](https://websockets.readthedocs.io/en/stable/index.html)
- [Async IO (Python)](https://docs.python.org/3/library/asyncio.html)
- [RethinkDB 2.4.7 (Python)](https://pypi.org/project/rethinkdb/)
- Python 3.8

## Configuration

**RDM** allows a dynamic configuration based on some environment variables, they aim to speed up some changes and are used in the service, below a list of variables and what their role in **RDM**:

- `ReDB_HOST`: The host address of the Rethink database to which **RDM** is to connect. The default is `rethink`, which is the name of the docker network for the **RDM** service to perform the tests, it is recommended to use `localhost`;
- `ReDB_PORT`: The port on which the Rethink database is operating. The default of RethinkDB is port `28015`, but if your database is configured differently, indicate in this variable;
- `ReDB_DEFAULT_DB`: Defines the default _database_ on which the service should work. The default is `test`, which must be the bank configured for sending status, but if you want to transmit status from another _database_ indicate this variable;
- `ReDB_USER`: The user to authenticate to the RethinkDB database. The default of RethinkDB is `admin`, but if you have different users for the operations just indicate;
- `ReDB_PASS`: The user password for authentication to the RethinkDB database. The default is an empty _string_, if your configuration is different just indicate;
- `ReDB_AUDIT_DB`: Sets the default _database_ for audit files. In this _database_ there should be tables to save the data received from the services for auditing. The default _database_ is called `AUDIT`;
- `ReDB_AUDIT_TABLE`: Defines the table in which the RDM service itself will save the data received by it. The default is the `rethink_data_manager` table (service name). If you want to indicate in another format to save, just configure this variable;
- `WS_HOST`: Indicates at which address the WebSocket server will be served. The default is `0.0.0.0`, which is equivalent to localhost;
- `WS_PORT`: Indicates which port the WebSocket server will be served on. The default is `8765`;

Example of setting an environment variable:

```shell
export ReDB_HOST='0.0.0.0'
```

If the above command is executed on the terminal it will be valid only while the session of that terminal is alive, for a more lasting configuration edit the `.bashrc` or `.profile` of your machine, so the configured environment variables will always be available in the system.
If you want to use the service in the format of a docker container, configure the `.env` file in the project's root folder and do as shown below in the RDM _build_ and _deploy_ section.

## Development

For development, it is enough to have Python 3 and the other project dependencies installed on your machine (which are explained below), in addition to your preferred text editor.

Before installing the environment tools, make sure that you have a [RethinkDB](https://www.rethinkdb.com/) database running for testing. **RDM** still needs _database_ **pytest_schema** to exist, with _tables_ **pytest_empty_table** and **pytest_table** so that tests can be runned.

### Installing VirtualEnvWrapper

We recommend using a virtual environment created by the __virtualenvwrapper__ module. There is a virtual site with English instructions for installation that can be accessed [here](https://virtualenvwrapper.readthedocs.io/en/latest/install.html). But you can also follow these steps below for installing the environment:

```shell
sudo python3 -m pip install -U pip             # Update pip
sudo python3 -m pip install virtualenvwrapper  # Install virtualenvwrapper module
```

**Observation**: If you do not have administrator access on the machine remove `sudo` from the beginning of the command and add the flag `--user` to the end of the command.

Now configure your shell to use **virtualenvwrapper** by adding these two lines to your shell initialization file (e.g. `.bashrc`,` .profile`, etc.)

```shell
export WORKON_HOME=\$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```

If you want to add a specific project location (will automatically go to the project folder when the virtual environment is activated) just add a third line with the following `export`:

```shell
export PROJECT_HOME=/path/to/project
```

Run the shell startup file for the changes to take effect, for example:

```shell
source ~/.bashrc
```

Now create a virtual environment with the following command (entering the name you want for the environment), in this example I will use the name **rethink**:

```shell
mkvirtualenv -p $(which python3) rethink
```

To use it:

```shell
workon rethink
sudo python3 -m pip install pipenv # Or
sudo apt install pipenv # On Debian based distributions
pipenv install # Will install all of the project dependencies
```

**Observaion**: Again, if necessary, add the flag `--user` to make the pipenv package installation for the local user.

## RDM Operations

The RDM service offers some operations from the RethinkDB database, most of which are related to common operations with _CRUD_ (_Create_, _Read_, _Update_ and _Delete_) of objects. Listed below are the operations that _websocket_ offers from the URL of your address:

- `/health`

Operation used to check the health of the RDM service. There is no need to send any data, just a call and the service should return the message:

```text
Server Up and Running!
```

The call URL will depend on the configuration of _host_ and the port of _webscoket_, but the example in local tests would be `localhost:8765/health`.

- `/insert`

Operation used to insert data into the database. The message model for sending and to guarantee the operation is:

```shell
{
    "id": "df03c48c-62fb-4f07-8a4b-7610fbe3adca",
    "type": "rethink-data-call",
    "payload": {
        "database": "database", # schema name
        "table": "table", # table name
        "data": { # JSON object to be inserted
            "key": 1
        }
    },
    "time": "2019-05-18T22:34:52.490439Z"
}
```

Therefore, for insertion, in the `payload` there should be the information of `database`, `table` and `data` (JSON object).

The call URL will depend on the configuration of _host_ and the port of _webscoket_, but the example in local tests would be `localhost:8765/insert`.

- `/get`

Operation to search for a single object in the database. The message model for sending and to guarantee the operation is:

```shell
{
    "id": "929b113d-91ab-41ab-87ca-7bc0e704fc7f",
    "type": "rethink-data-call",
    "payload": {
        "database": "database", # schema name
        "table": "table", # table name
        "identifier": "2a33eda5-040c-40dc-ba1e-dcb8d2f5b140" # object identifier to get
    },
    "time": "2019-05-18T22:40:20.755916Z"
}
```

Therefore, for the selection, in the `payload` there must be the information of the `database`, `table` and the `identifier`. The identifier being the key to the object that you want to retrieve within RethinkDB.

The call URL will depend on the configuration of _host_ and the port of _webscoket_, but the example in local tests would be `localhost:8765/get`.

- `/get_all`

Operation to list all objects in a table in the database. The message model for sending and to guarantee the operation is:

```shell
{
    "id": "a5093f52-bde6-4c74-8989-c36d00e7d7b5",
    "type": "rethink-data-call",
    "payload": {
        "database": "database", # schema name
        "table": "table" # table name
    },
    "time": "2019-05-18T22:42:35.267029Z"
}
```

Therefore, for the listing, in the `payload` there should be the information from the `database` and the `table`.

The calling URL will depend on the configuration of _host_ and the port of _webscoket_, but the example in local tests would be `localhost:8765/get_all`.

- `/filter`

Operation to list all objects in a table in the database with a filter (condition). The message model for sending and to guarantee the operation is:

```shell
{
    "id": "a5093f52-bde6-4c74-8989-c36d00e7d7b5",
    "type": "rethink-data-call",
    "payload": {
        "database": "database", # schema name
        "table": "table", # table name
        "filter": "{'races': 1}" # search filter for objects
    },
    "time": "2019-05-18T22:42:35.267029Z"
}
```

Therefore, for the listing, in the `payload` there should be the information from the `database`, the `table` and the `filter` condition for selection.

The call URL will depend on the configuration of _host_ and the port of _webscoket_, but the example in local tests would be `localhost:8765/filter`.

- `/update`

Operation to update a database object. The message model for sending and to guarantee the operation is:

```shell
{
    "id": "1174969a-c838-49cb-9751-66bb1be22af9",
    "type": "rethink-data-call",
    "payload": {
        "database": "database", # schema name
        "table": "table", # table name
        "identifier": "23af3f1e-ee59-462a-bf41-abbb974ae3ea", # ID of the object you want to update (the IDs generated by RethinkDB for the objects also use the UUID format)
        "data": { # Update declaration (the keys and values that are in the declaration will be updated or added), being a JSON object
            "key": 1
        }
    },
    "time": "2019-05-18T22:34:52.490439Z"
}
```

Therefore, for updating, in the `payload` there must be the information of the `database`, `table`, `identifier` (here must contain the ID of the object you want to update, it can be retrieved by the operation `get` or `get_all`) and `data` (the update declaration must be included here, so the JSON object contained in that key will update the keys and values that exist in the object, if any keys do not exist, they will be included).

The call URL will depend on the configuration of _host_ and the port of _webscoket_, but the example in local tests would be `localhost:8765/update`.

- `/delete`

Operation to delete an object in the database. The message model for sending and to guarantee the operation is:

```shell
{
    "id": "f2da2d37-01c7-4a42-b681-dc4dfa3dc225",
    "type": "rethink-data-call",
    "payload": {
        "database": "database", # schema name
        "table": "table", # table name
        "identifier": "efa67d0b-0d63-4962-b7a7-440ae2ee0848" # ID of the object to be deleted (the IDs generated by RethinkDB for the objects also use the UUID format)
    },
    "time": "2019-05-18T22:53:13.594738Z"
}
```

Therefore, for deletion, in the `payload` there should be the information of `database`, `table` and `identifier` (here must contain the ID of the object you want to delete, it can be recovered by the operation `get` or `get_all`). Remember that this action will delete the object and cannot be undone.

The call URL will depend on the configuration of _host_ and the port of _webscoket_, but the example in local tests would be `localhost:8765/delete`.

- `delete_all`

Operation to delete all objects from a table in the database. The message model for sending and to guarantee the operation is:

```shell
{
    "id": "b991a2c2-c4c9-4e69-a760-aebb173fcafe",
    "type": "rethink-data-call",
    "payload": {
        "database": "database", # schema name
        "table": "table" # table name
    },
    "time": "2019-05-18T22:57:42.552426Z"
}
```

Therefore, for the deletion of all objects, in the `payload` there must be the information from the `database` and `table`. Remember that this action will delete all objects and cannot be undone.

The call URL will depend on the configuration of _host_ and the port of _webscoket_, but the example in local tests would be `localhost:8765/delete_all`.

- `/create_table`

Operation to create a new table in the database schema. The message model for sending and to guarantee the operation is:

```shell
{
    "id": "026b20aa-5fa1-4c28-b506-2ee24096fb74",
    "type": "rethink-data-call",
    "payload": {
        "database": "database", # schema name
        "table": "new_table" # new table name
    },
    "time": "2019-05-18T23:01:41.355693Z"
}
```

Therefore, for the creation of the table, in the `payload` there must be the information from the  `database` and `table` (the names of the tables can only have alphanumeric characters, cannot start in digits and the only accepted character to separate words is the underscore `_`).

The calling URL will depend on the configuration of _host_ and the port of _webscoket_, but the example in local tests would be `localhost:8765/create_table`.

__Observation__: Any error that occurs in the operations the _response_ package must send a message. For more complete information just check the RDM _logs_.

## Local Execution

For local system execution, run the following command in the project root folder (assuming _virtualenv_ is already active):

```shell
python src/main.py
```

This command will upload the RDM server and after a few moments it will be ready for use.

To test communication with a _client_ just run the code on another terminal, also present in the project:

```shell
python3 src/client.py
```

That way it is possible to do tests.

Ensure that RethinkDB is running and accessible, and, if necessary, configure the other variables within `service/service.py`.

## Tests

To run the __RDM__ tests follow the script below:

1.  Enable _virtualenv_ **rethink**;
2.  Ensure that the dependencies are installed, especially:

        pytest
        pytest-asyncio
        pytest-coverage
        flake8

3.  Run the commands below:

```shell
export PYTHONPATH=$(pwd)                   # Set the python path as the project folder
pytest src/                                # Performs the tests
pytest --cov=src src/                      # Performs tests evaluating coverage
pytest --cov=src --cov-report xml src/     # Generate the XML report of coverage
flake8 src/ --ignore=E501,F541             # Run PEP8 linter
unset PYTHONPATH                           # Unset PYTHONPATH variable
```

During the tests the terminal will display a output with the test report (failures, skips and successes) and the system test coverage. For other configurations and supplemental documentation go to [pytest](https://pytest.org/en/latest/) and [coverage](https://pytest-cov.readthedocs.io/en/latest/).

During the lint process the terminal will report a bug report and warnings from the PEP8 style guide, for more configurations and additional documentation go to [flake8](http://flake8.pycqa.org/en/latest/index.html#quickstart) and [PEP8](https://www.python.org/dev/peps/pep-0008/)

## _Build_

Para construir e rodar o container do microsserviço basta rodar os seguintes comandos:

```shell
docker run -it -d --add-host=database:172.17.0.1 --name rethinkdb -v "$PWD:/data" -p 8081:8080 -P rethinkdb:latest
docker build -t rethink-data-manager:latest .
docker run -d --name rethink-data-manager -p 8765:8765 --env-file .env --link=rethinkdb:database rethink-data-manager:latest
```

**OBSERVATION**: The first command will create a running docker instance of RethinkDB
