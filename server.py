import asyncio
import random
import json

HOST, PORT = "0.0.0.0", 666
clients = []

async def broadcast(msg):
    for w, _ in clients:
        try:
            msg_json = {"msg": msg}
            w.write(json.dumps(msg_json).encode())
            await w.drain()
        except:
            pass

async def client_handler(reader, writer):
    data = await reader.read(1024)
    data_json = json.loads(data.decode().strip())
    name = data_json.get("name")
    clients.append((writer, name))

    await broadcast(f"{name} connected")

    print(f"[server] connected {name}")

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            msg = json.loads(data.decode().strip())

            if msg.get("cmd").lower() == "roll":
                roll = random.randint(1, 6)
                await broadcast(f"{name} - {roll}")

    except:
        pass


async def main():
    server = await asyncio.start_server(client_handler, HOST, PORT) #!!!!!!!!!!!!!!!
    print(f"[server] start")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main()) 
