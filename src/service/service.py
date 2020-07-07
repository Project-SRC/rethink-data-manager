from db.db import connect, create_table, close_connection, get_where
from db.db import insert, get_all, get, update
from db.db import delete, delete_all
from dotenv import load_dotenv
from pathlib import Path
from websockets.exceptions import ConnectionClosed
from concurrent.futures._base import CancelledError
import websockets
import logging
import json
import http
import os


# Path operations
op = {
    1: "/insert",
    2: "/get_all",
    3: "/get",
    4: "/update",
    5: "/delete",
    6: "/delete_all",
    7: "/create_table",
    8: "/filter",
}

# Default localhost address
LOCALHOST = "0.0.0.0"  # nosec

# RethinkDB variables
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
ReDB_HOST = os.getenv("ReDB_HOST", LOCALHOST)
ReDB_PORT = os.getenv("ReDB_PORT", 28015)
ReDB_DEFAULT_DB = os.getenv("ReDB_DEFAULT_DB", "test")
ReDB_USER = os.getenv("ReDB_USER", "admin")
ReDB_PASS = os.getenv("ReDB_PASS", "")
ReDB_AUDIT_DB = os.getenv("ReDB_AUDIT_DB", "AUDIT")
ReDB_AUDIT_TABLE = os.getenv("ReDB_AUDIT_TABLE", "rethink_data_manager")

# WebSocket variables
WS_HOST = os.getenv("WS_HOST", LOCALHOST)
WS_PORT = os.getenv("WS_PORT", 8765)

# Other variables
RDM_CALL = "rethink-manager-call"


def health_check(path, request_headers):
    if path == "/health" or path == "/health/":
        logging.info(f"[INFO] HEALTH CHECK PROCESS: {request_headers}")
        return http.HTTPStatus.OK, [], b"Server Up and Running!\n"


def error_msg(path):
    operation = path.lstrip("/")
    msg = (
        f"[ERROR] Some error was faced while trying to execute"
        f" your operation. Verify the Rethink Data Manager (RDM) logs!\n"
        f"params::path = {path}\nparams::operation = {operation}"
    )
    return {"status_code": 500, "response_message": msg}


def success_msg(msg):
    return {"status_code": 200, "response_message": msg}


def test_database_connection(
    host="localhost", port=28015, user=ReDB_USER, password=ReDB_PASS
):
    try:
        connection = connect(host, port, ReDB_DEFAULT_DB, user, password)
        if connection is not None and connection.is_open():
            logging.info(f"[INFO] Connection to database was successful")
        else:
            logging.error(
                f"[ERROR] Couldn't connect to database with:"
                f"\n HOST: {host}\tPORT: {port}"
            )
            raise Exception("Unknown host and unknown port.")
    except Exception as err:
        logging.error(
            f"[ERROR] Error at service.py/test_database_connection."
            f"\nTraceback: {err}"
        )
        return False
    else:
        if connection is not None and connection.is_open():
            logging.info("[INFO] Closing database connection")
            disconnect_database(connection)

        return True


def configure_database(
    host="localhost", port=28015, db=None, user=ReDB_USER, password=ReDB_PASS
):
    connection = connect(host, port, db, user, password)
    if db:
        connection.use(db)

    if connection:
        return connection
    else:
        return False


def disconnect_database(connection):
    if not close_connection(connection):
        logging.error(f"[ERROR] Connection with RethinkDB was not closed!")
        return False
    else:
        logging.info(f"[INFO] Connection with RethinkDB was closed" f" successfully!")
        return True


def save_audit(identifier, request_type, payload, time):
    try:
        connection = configure_database(
            ReDB_HOST, ReDB_PORT, ReDB_AUDIT_DB, ReDB_USER, ReDB_PASS
        )
        audit_data = {
            "identifier": identifier,
            "type": request_type,
            "payload": payload,
            "time": time,
        }
        result = insert(ReDB_AUDIT_DB, ReDB_AUDIT_TABLE, audit_data, connection)
        if result == {}:
            raise Exception(
                f"[ERROR] Error trying to insert data. "
                f"Verify the logs for the full traceback. "
                f"The data was not inserted!"
            )
        else:
            logging.info(
                f"[INFO] Audit data saved into Rethink DB!\n"
                f"Saved payload: {audit_data}\nRethink output"
                f": {result}"
            )
            disconnect_database(connection)
            return True
    except Exception as err:
        if connection:
            disconnect_database(connection)
            raise err
    except KeyboardInterrupt as err:
        disconnect_database(connection)
        raise err
    except ConnectionClosed as err:
        disconnect_database(connection)
        raise err
    except CancelledError as err:
        disconnect_database(connection)
        raise err


async def data_manager(websocket, path):
    logging.info(f"[INFO] Current path: {str(path)}")
    try:
        if path == "/":
            raise Exception(
                f"No operation defined on the current path."
                f"\nReceived path: {str(path)}"
            )
        data = await websocket.recv()
        data = json.loads(data)

        identifier = data["id"]
        request_type = data["type"]
        payload = data["payload"]
        time = data["time"]
        logging.info(f"[INFO] Data received: {data}")

        if request_type != RDM_CALL:
            raise Exception(
                f"Type of service not as expected. Probably a call"
                f"for other service. Verify logs for further infor"
                f"mation!"
            )

        if save_audit(identifier, request_type, payload, time):
            pass
        else:
            logging.error(
                f"[ERROR] Error while trying to save data to audit"
                f" database. Verify Rethink Data Manager logs for "
                f"furhter information!"
            )

        try:
            connection = configure_database(
                ReDB_HOST, ReDB_PORT, ReDB_DEFAULT_DB, ReDB_USER, ReDB_PASS
            )

            if str(path) == op[1]:
                database = payload["database"]
                table = payload["table"]
                payload = payload["data"]
                logging.info(
                    f"[INFO] Inserting data:\n\tDATABASE: "
                    f"{database}\n\tTABLE: {table}\n\tDATA: "
                    f"{payload}"
                )
                result = insert(database, table, payload, connection)
                if result == {}:
                    raise Exception(
                        f"[ERROR] Error trying to insert data. "
                        f"Verify the logs for the full traceback. "
                        f"The data was not inserted!"
                    )
                else:
                    await websocket.send(json.dumps(success_msg(result)))
            elif str(path) == op[2]:
                database = payload["database"]
                table = payload["table"]
                logging.info(
                    f"[INFO] Getting all data:\n\tDATABASE: "
                    f"{database}\n\tTABLE: {table}"
                )
                result = get_all(database, table, connection)
                if result == {}:
                    raise Exception(
                        f"[ERROR] Error trying to getting data. "
                        f"Verify the logs for the full traceback. "
                        f"Neither the table is empty or no table"
                        f" was found!"
                    )
                else:
                    await websocket.send(json.dumps(success_msg(result)))
            elif str(path) == op[3]:
                database = payload["database"]
                table = payload["table"]
                identifier = payload["identifier"]
                logging.info(
                    f"[INFO] Getting objetct data:\n\tDATABASE: "
                    f"{database}\n\tTABLE: {table}\n\tIDENTIFIER: "
                    f"{identifier}"
                )
                result = get(database, table, identifier, connection)
                if result == {}:
                    raise Exception(
                        f"[ERROR] Error trying to getting data. "
                        f"Verify the logs for the full traceback. "
                        f"Neither the object doesn't exists or no"
                        f" table was found!"
                    )
                else:
                    await websocket.send(json.dumps(success_msg(result)))
            elif str(path) == op[4]:
                database = payload["database"]
                table = payload["table"]
                identifier = payload["identifier"]
                statment = payload["data"]
                logging.info(
                    f"[INFO] Updating object:\n\tDATABASE: "
                    f"{database}\n\tTABLE: {table}\n\tIDENTIFIER: "
                    f"{identifier}\n\tUPDATE STATEMENT: {statment}"
                )
                result = update(database, table, identifier, statment, connection)
                if result == {}:
                    raise Exception(
                        f"[ERROR] Error trying to update object. "
                        f"Verify the logs for the full traceback. "
                        f"Neither the object doesn't exists or no"
                        f" table was found!"
                    )
                elif result["objects_updated"] == 0:
                    raise Exception(
                        f"[ERROR] Error trying to update object. "
                        f"Verify the logs for the full traceback."
                    )
                else:
                    await websocket.send(json.dumps(success_msg(result)))
            elif str(path) == op[5]:
                database = payload["database"]
                table = payload["table"]
                identifier = payload["identifier"]
                logging.info(
                    f"[INFO] Deleting object:\n\tDATABASE: "
                    f"{database}\n\tTABLE: {table}\n\tIDENTIFIER: "
                    f"{identifier}"
                )
                result = delete(database, table, identifier, connection)
                if result == {}:
                    raise Exception(
                        f"[ERROR] Error trying to delete object. "
                        f"Verify the logs for the full traceback. "
                        f"Neither the object doesn't exists or no"
                        f" table was found!"
                    )
                elif result["objects_deleted"] == 0:
                    raise Exception(
                        f"[ERROR] Error trying to delete object. "
                        f"Verify the logs for the full traceback."
                    )
                else:
                    await websocket.send(json.dumps(success_msg(result)))
            elif str(path) == op[6]:
                database = payload["database"]
                table = payload["table"]
                logging.info(
                    f"[INFO] Deleting all objects:\n\tDATABASE: "
                    f"{database}\n\tTABLE: {table}"
                )
                result = delete_all(database, table, connection)
                if result == {}:
                    raise Exception(
                        f"[ERROR] Error trying to delete objects. "
                        f"Verify the logs for the full traceback. "
                        f"Neither some error was found or no table"
                        f" was found!"
                    )
                elif result["objects_deleted"] == 0:
                    raise Exception(
                        f"[ERROR] Error trying to delete object. "
                        f"Verify the logs for the full traceback."
                    )
                else:
                    await websocket.send(json.dumps(success_msg(result)))
            elif str(path) == op[7]:
                database = payload["database"]
                table = payload["table"]
                logging.info(
                    f"[INFO] Creating new table:\n\tDATABASE: "
                    f"{database}\n\tTABLE: {table}"
                )
                result = create_table(database, table, connection)
                if result == {}:
                    raise Exception(
                        f"[ERROR] Unknown error while trying to "
                        f"create a new table. Verify the logs"
                        f" for the the full traceback."
                    )
                elif result["tables_created"] == 0:
                    raise Exception(f"[ERROR] This table ({table})" f" already exists!")
                else:
                    await websocket.send(json.dumps(success_msg(result)))
            elif str(path) == op[8]:
                database = payload["database"]
                table = payload["table"]
                statment = payload["filter"]
                statment = json.loads(statment)
                logging.info(
                    f"[INFO] Getting objetct data:\n\tDATABASE: "
                    f"{database}\n\tTABLE: {table}\n\tFILTER: "
                    f"{statment}"
                )
                result = get_where(database, table, statment, connection)
                if result == {}:
                    raise Exception(
                        f"[ERROR] Unknown error while trying to "
                        f"create a new table. Verify the logs"
                        f" for the the full traceback."
                    )
                else:
                    await websocket.send(json.dumps(success_msg(result)))
            else:
                raise Exception(
                    f"Unknown operation on the current path."
                    f"\nReceived path: {str(path)}"
                )
        except Exception as err:
            if connection:
                disconnect_database(connection)
                raise err
        except KeyboardInterrupt as err:
            disconnect_database(connection)
            raise err
        except ConnectionClosed as err:
            disconnect_database(connection)
            raise err
        except CancelledError as err:
            disconnect_database(connection)
            raise err
    except Exception as err:
        logging.error(f"[ERROR] Error at services/data_manager." f"\nTraceback: {err}")
        await websocket.send(json.dumps(error_msg(path)))
    else:
        pass


server = websockets.server.serve(
    data_manager,
    WS_HOST,
    WS_PORT,
    process_request=health_check,
    ping_timeout=60,
    ping_interval=10,
)
