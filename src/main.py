from service.service import (
    test_database_connection,
    server,
    ReDB_HOST,
    ReDB_PORT,
    ReDB_USER,
    ReDB_PASS,
)
from websockets.exceptions import ConnectionClosed
import asyncio
import logging


def main():
    logging.basicConfig(
        format="%(asctime)s,%(msecs)-3d - %(name)-2s - "
        "%(levelname)-2s => %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )
    logging.info("[INFO] Starting RDM - Manager Service...")
    try:
        logging.info("[INFO] Testing RethinkDB Connection...")
        if not test_database_connection(ReDB_HOST, ReDB_PORT, ReDB_USER, ReDB_PASS):
            logging.critical(
                "[CRITICAL] RDM couldn't connect with the"
                " database.\n Unable to start service!\n"
            )
            raise Exception(f"No database connection!")
        loop = asyncio.get_event_loop()
        logging.info("[INFO] Starting WebSocket Server")
        loop.run_until_complete(server)
        logging.info("[INFO] WebSocket Server started")
        loop.run_forever()
    except KeyboardInterrupt:
        logging.exception(f"[EXCEPTION] System interrupted by user.")
        logging.info(f"[INFO] Trying to gracefully stop server...")
        loop.stop()
        loop.close()
        logging.info(f"[INFO] Server closed.")
    except Exception as err:
        logging.exception(f"[EXCEPTION] Error in system.\n{str(err)}")
        logging.info(f"[INFO] Trying to gracefully stop server...")
        loop.stop()
        loop.close()
    except ConnectionClosed as err:
        logging.exception(f"[EXCEPTION] Error in system.\n{str(err)}")
        logging.info(f"[INFO] Trying to gracefully stop server...")
        loop.stop()
        loop.close()


if __name__ == "__main__":
    main()
