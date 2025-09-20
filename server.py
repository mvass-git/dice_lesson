import asyncio
import random
import json

import sqlite3

conn = sqlite3.connect("dice.db")
cursor = conn.cursor()

create_table = """
CREATE TABLE IF NOT EXISTS login_data (
id INTEGER PRIMARY KEY AUTOINCREMENT,
login TEXT NOT NULL,
password TEXT NOT NULL
)
"""

cursor.execute(create_table)

async def add_user(login, password):
    query = """
    SELECT login
    FROM login_data
    WHERE login = ?
    """
    cursor.execute(query, (login,))

    rows = cursor.fetchall()
    print(f"sign up attempt with {login} {password}")

    if not rows:
        query = """
        INSERT INTO login_data (login, password) VALUES (?, ?)
        """
        cursor.execute(query, (login, password))
        conn.commit()
        return json.dumps({"respond":"success"})
    else:
        return json.dumps({"respond":"user already exists"})
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
            elif msg.get("cmd").lower() == "add_user":
                login, password = msg.get("login"), msg.get("password")
                respond = await add_user(login, password)
                writer.write(respond.encode())
                await writer.drain()

    except Exception as e:
            print(f"error in client handler {e}")


async def main():
    server = await asyncio.start_server(client_handler, HOST, PORT) #!!!!!!!!!!!!!!!
    print(f"[server] start")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main()) 
