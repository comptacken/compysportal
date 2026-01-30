import asyncio
import websockets
import json
import os

clients = []

async def broadcast(message, exclude_ws=None):
    if isinstance(message, dict):
        message = json.dumps(message)

    for client in clients[:]:
        try:
            if client["ws"] != exclude_ws:
                await client["ws"].send(message)
        except:
            clients.remove(client)

async def handler(websocket):
    nickname = "Unknown"
    client = {"ws": websocket, "name": nickname}

    try:
        # handshake
        raw = await asyncio.wait_for(websocket.recv(), timeout=5)
        data = json.loads(raw)
        nickname = data.get("name", "Guest")
    except:
        nickname = "Guest"

    client["name"] = nickname
    clients.append(client)

    await broadcast({"name": "System", "msg": f"✨ {nickname} joined the chat"})

    try:
        async for message in websocket:
            data = json.loads(message)
            msg = data.get("msg", "").strip()
            if not msg:
                continue

            await broadcast({"name": nickname, "msg": msg}, websocket)

    finally:
        if client in clients:
            clients.remove(client)
            await broadcast({"name": "System", "msg": f"❌ {nickname} left the chat"})

async def main():
    port = int(os.environ.get("PORT", 8765))
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"🚀 Server running on port {port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
