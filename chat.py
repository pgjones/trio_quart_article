import json

import trio
from quart import render_template, websocket
from quart_trio import QuartTrio

connections = set()

app = QuartTrio(__name__)


@app.route("/")
async def index():
    return await render_template("index.html")


@app.websocket("/ws")
async def chat():
    try:
        connections.add(websocket._get_current_object())
        async with trio.open_nursery() as nursery:
            nursery.start_soon(heartbeat)
            while True:
                message = await websocket.receive()
                await broadcast(message)
    finally:
        connections.remove(websocket._get_current_object())


async def broadcast(message):
    for connection in connections:
        await connection.send(json.dumps({"type": "message", "value": message}))


async def heartbeat():
    while True:
        await trio.sleep(1)
        await websocket.send(json.dumps({"type": "heartbeat"}))


if __name__ == "__main__":
    app.run()
