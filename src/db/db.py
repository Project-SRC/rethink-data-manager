from rethinkdb.errors import ReqlDriverError
from rethinkdb import r
import logging

USER = "admin"
PASSWORD = ""


def connect(
    db_host="localhost", db_port=28015, database="test", user=USER, password=PASSWORD
):
    try:
        logging.info(
            f"[INFO] Connecting into RethinkDB "
            f"with options:\n\tHOST: {db_host}"
            f"\n\tPORT: {db_port}\n\tDATABASE: {database}"
        )
        connection = r.connect(
            host=db_host, port=db_port, db=database, user=user, password=password
        )
    except ReqlDriverError as err:
        logging.error(
            f"[ERROR] Error trying to connect with RethinkDB." f" Traceback: {err}"
        )
        return None
    except Exception as err:
        logging.error(
            f"[ERROR] Unknown error trying to connect with "
            f"RethinkDB. Traceback: {err}"
        )
        return None
    else:
        return connection


def close_connection(connection):
    try:
        connection.close()
    except Exception as err:
        logging.error(
            f"[ERROR] Error trying to close RethinkDB " f"connection.\nTraceback: {err}"
        )
        return False
    else:
        return True


def desc_table(database, table, connection):
    try:
        objects = r.db(database).table(table).pluck("id").run(connection)
        if len(objects.items) == 0:
            raise Exception(
                f"Describe Error.\nCouldn't retrieve "
                f"any data from:\ndatabase: "
                f"{database}\ntable: {table}"
            )
        else:
            keys = (
                r.db(database)
                .table(table)
                .get(list(objects.items)[0]["id"])
                .keys()
                .run(connection)
            )
            item = (
                r.db(database)
                .table(table)
                .get(list(objects.items)[0]["id"])
                .run(connection)
            )
            if len(keys) == 0:
                raise Exception(
                    f"Describe Error.\nCouldn't retrieve table "
                    f"keys from:\ndatabase: {database}\ntable: "
                    f"{table}\nobject: {item}"
                )
    except Exception as err:
        logging.error(
            f"[ERROR] Error trying to describe table at db.py/"
            f"desc_table.\nTraceback: {err}"
        )
        return set()
    else:
        logging.info(f"[INFO] Keys retrieved from {table}: {keys}")
        return keys


def insert(database, table, data, connection):
    try:
        result = r.db(database).table(table).insert(data).run(connection)
        if not result["inserted"] > 0:
            raise Exception(f"Insertion Error.\nCouldn't insert object: " f"{data}")
    except Exception as err:
        logging.error(
            f"[ERROR] Error trying to insert data at db.py/insert."
            f"\nTraceback: {err}"
        )
        return {}
    else:
        logging.info(f"[INFO] Object inserted: {data}.\nData: {result}")
        return result


def get_all(database, table, connection):
    try:
        cursor = r.db(database).table(table).run(connection)
        if cursor is None:
            raise Exception(
                f"Select Error.\nCouldn't find any data in:\n\t"
                f"database: {database}\n\ttable: {table}"
            )
        else:
            result = list(cursor.items)
            if result is None or len(result) == 0:
                raise Exception(
                    f"Select Error.\nCouldn't find any data in:"
                    f"\n\tdatabase: {database}\n\ttable: {table}"
                )
    except Exception as err:
        logging.error(
            f"[ERROR] Error trying to get data at db.py/get_all." f"\nTraceback: {err}"
        )
        return {}
    else:
        logging.info(
            f"[INFO] Number of object(s) recovered: {len(result)}." f"\nData: {cursor}"
        )
        return result


def get(database, table, identifier, connection):
    try:
        item = r.db(database).table(table).get(identifier).run(connection)
        if item is None:
            raise Exception(
                f"Select Error.\nCouldn't find any data in:"
                f"\n\tdatabase: {database}\n\t"
                f"table: {table}\n\tid: {identifier}"
            )
    except Exception as err:
        logging.error(
            f"[ERROR] Error trying to get data at db.py/get." f"\nTraceback: {err}"
        )
        return {}
    else:
        logging.info(
            f"[INFO] Number of object(s) recovered: {len(item)}"
            f"\n\tObject recovered: {item}"
        )
        return item


def get_where(database, table, statment, connection):
    try:
        result = r.db(database).table(table).filter(statment).run(connection)
        if result is None:
            raise Exception(
                f"Select Error.\nCouldn't find any data in:"
                f"\n\tdatabase: {database}\n\t"
                f"table: {table}\n\tfilter: {statment}"
            )
    except Exception as err:
        logging.error(
            f"[ERROR] Error trying to get data at db.py/get_where."
            f"\nTraceback: {err}"
        )
        return {}
    else:
        result = result.items
        result = list(result)
        logging.info(
            f"[INFO] Number of object(s) recovered: {len(result)}"
            f"\n\tObject recovered: {result}"
        )
        return result


def update(database, table, identifier, update_statement, connection):
    try:
        item = r.db(database).table(table).get(identifier).run(connection)
        if item is None:
            raise Exception(
                f"Update Error.\nCouldn't find any data in:"
                f"\n\tdatabase: {database}\n\t"
                f"table: {table}\n\t id: {identifier}"
            )
        else:
            result = (
                r.db(database)
                .table(table)
                .get(identifier)
                .update(update_statement, return_changes=True)
                .run(connection)
            )
            if result["replaced"] == 0:
                raise Exception(
                    f"Update Error.\nCouldn't update object in:"
                    f"\n\tdatabase: {database}\n\t"
                    f"table: {table}\n\tid: {identifier}\n\t"
                    f"update statement: {update_statement}"
                )
    except Exception as err:
        logging.error(
            f"[ERROR] Error trying to update data at db.py/update."
            f"\nTraceback: {err}"
        )
        return {"objects_updated": 0}
    else:
        updated = result["replaced"]
        changes = result["changes"]
        logging.info(
            f"[INFO] Number of object(s) updated: {updated}" f"\nChanges: {changes}"
        )
        return {"objects_updated": updated, "changes": changes}


def delete(database, table, identifier, connection):
    try:
        item = r.db(database).table(table).get(identifier).run(connection)
        if item is None:
            raise Exception(
                f"Delete Error.\nCouldn't find any data in:"
                f"\n\tdatabase: {database}\n\t"
                f"table: {table}\n\t id: {identifier}"
            )
        else:
            r.db(database).table(table).get(identifier).delete().run(connection)
    except Exception as err:
        logging.error(
            f"[ERROR] Error trying to delete data at db.py/delete."
            f"\nTraceback: {err}"
        )
        return {"objects_deleted": 0}
    else:
        logging.info(f"[INFO] Number of object(s) deleted: 1.\nData: {item}")
        return {"objects_deleted": 1}


def delete_all(database, table, connection):
    try:
        result = r.db(database).table(table).delete().run(connection)
        if result["deleted"] == 0:
            raise Exception(
                f"Delete Error.\nCouldn't delete data in:"
                f"\n\tdatabase: {database}\n\t"
                f"table: {table}"
            )
    except Exception as err:
        logging.error(
            f"[ERROR] Error trying to delete data at "
            f"db.py/delete_all.\nTraceback: {err}"
        )
        return {"objects_deleted": 0}
    else:
        deleted = result["deleted"]
        logging.info(
            f"[INFO] Number of object(s) deleted: {deleted}." f"\nData: {result}"
        )
        return {"objects_deleted": deleted}


def create_table(database, table, connection):
    if r.db(database).table_list().contains(table).run(connection):
        return {"tables_created": 0}
    else:
        r.db(database).table_create(table).run(connection)
        return {"tables_created": 1}


def create_db(database, connection):
    # TODO REFACTOR TO contains.do(r.branch) BLOCK
    # TODO PyPi package 2.3.0post6 contains error for the mentioned refactor,
    #  wait for new release
    if r.db_list().contains(database).run(connection):
        return {"dbs_created": 0}
    else:
        r.db_create(database).run(connection)
        return {"dbs_created": 1}


def drop_table(database, table, connection):
    try:
        result = r.db(database).table_drop(table).run(connection)
        if result["tables_dropped"] == 0:
            raise Exception(
                f"Drop Error.\n Couldn't drop table in:"
                f"\n\tDatabase: {database}\n\ttable: {table}"
            )
    except Exception as err:
        logging.error(
            f"[ERROR] Error trying to drop table at "
            f"db.py/drop_table.\nTraceback: {err}"
        )
        return {"tables_dropped": 0}
    else:
        dropped = result["tables_dropped"]
        logging.info(f"[INFO] Number of tables dropped: {dropped}." f"\nData: {result}")
        return {"tables_dropped": dropped}


def drop_db(database, connection):
    try:
        result = r.db_drop(database).run(connection)
        if result["dbs_dropped"] == 0:
            raise Exception(
                f"Drop Error.\n Couldn't drop database in:" f"\n\tDatabase: {database}"
            )
    except Exception as err:
        logging.error(
            f"[ERROR] Error trying to drop database at "
            f"db.py/drop_db.\nTraceback: {err}"
        )
        return {"dbs_dropped": 0, "tables_dropped": 0}
    else:
        dbs_dropped = result["dbs_dropped"]
        tables_dropped = result["tables_dropped"]
        logging.info(
            f"[INFO] Number of databases dropped: {dbs_dropped}."
            f"\n[INFO] Number of tables "
            f"dropped: {tables_dropped}.\nData: {result}"
        )
        return {"dbs_dropped": dbs_dropped, "tables_dropped": tables_dropped}
