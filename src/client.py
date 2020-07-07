import asyncio
import datetime
import uuid
import websockets
import json
from websockets import ConnectionClosed


async def hello():
    op = input("Which operation will be used?: ")
    async with websockets.connect(f"ws://127.0.0.1:8765/{op}") as websocket:

        database = input("Get database name: ")
        table = input("Get table name: ")
        payload = input("Get package data: ")
        recv_id = input("Identifier: ")
        statment = input("Filter: ")
        payload = json.loads(payload)

        payload = {
            "database": database,
            "table": table,
            "data": payload,
            "identifier": recv_id,
            "filter": statment,
        }

        identifier = str(uuid.uuid4())

        time = datetime.datetime.utcnow()

        time = str(time.isoformat("T") + "Z")

        type = "rethink-manager-call"
        data = {"id": identifier, "type": type, "payload": payload, "time": time}

        await websocket.send(json.dumps(data))
        print(f"> {data}")

        try:
            while True:
                await websocket.pong(data="PONG")
                message = await asyncio.wait_for(websocket.recv(), timeout=20)
                print(f"< {message}")
                if message is None:
                    break
        except (asyncio.TimeoutError, ConnectionRefusedError) as err:
            print(err)
        except ConnectionClosed as err:
            print(err)
        except RuntimeError as err:
            print(err)
        except Exception as err:
            print(err)
        finally:
            asyncio.get_event_loop().stop()


try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(hello())
except (asyncio.TimeoutError, ConnectionRefusedError) as err:
    print(err)
except ConnectionClosed as err:
    print(err)
except RuntimeError as err:
    print(err)
except Exception as err:
    print(err)
finally:
    asyncio.get_event_loop().stop()
