"""Run the skeleton against a real PostgreSQL and a stub warehouse, and watch what it does."""

import asyncio
import os
import signal
import socket
import subprocess
import sys
import time

import httpx
from testcontainers.postgres import PostgresContainer


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def warehouse(reader, writer) -> None:
    """A downstream service that reports the deadline header it received."""
    head = (await reader.readuntil(b"\r\n\r\n")).decode()
    deadline = next((l.split(":", 1)[1].strip() for l in head.split("\r\n") if l.lower().startswith("x-deadline-ms")), "none")
    body = f'{{"in_stock": 3, "deadline_ms_seen": {deadline}}}'.encode()
    writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body)
    await writer.drain()
    writer.close()


async def main(database_url: str) -> None:
    stub = await asyncio.start_server(warehouse, "127.0.0.1", 0)
    warehouse_url = f"http://127.0.0.1:{stub.sockets[0].getsockname()[1]}"
    port = free_port()
    env = {**os.environ, "DATABASE_URL": database_url, "WAREHOUSE_URL": warehouse_url, "PORT": str(port)}
    t0 = time.perf_counter()
    proc = subprocess.Popen([sys.executable, "service.py"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = lambda text: print(f"  {time.perf_counter() - t0:5.2f} s  {text}")
    async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{port}", timeout=5.0) as client:
        for _ in range(300):
            try:
                r = await client.get("/system/health/readyz")
                if r.status_code == 200:
                    break
            except httpx.TransportError:
                pass
            await asyncio.sleep(0.05)
        log(f"readyz -> {r.status_code} {r.json()}")
        r = await client.get("/orders/1", headers={"X-Deadline-Ms": "800"})
        log(f"GET /orders/1 with X-Deadline-Ms: 800 -> {r.status_code} {r.json()}")
        r = await client.get("/orders/2")
        log(f"GET /orders/2 without a deadline       -> {r.status_code} {r.json()}")
        log("SIGTERM")
        os.kill(proc.pid, signal.SIGTERM)
        await asyncio.sleep(0.2)
        r = await client.get("/system/health/readyz")
        log(f"readyz during the drain delay -> {r.status_code}")
        r = await client.get("/orders/1")
        log(f"GET /orders/1 during the drain delay -> {r.status_code}")
    while proc.poll() is None and time.perf_counter() - t0 < 30:
        await asyncio.sleep(0.05)
    log(f"process exited with {proc.returncode}")
    stub.close()


with PostgresContainer("postgres:17-alpine") as pg:
    url = pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    import sqlalchemy
    engine = sqlalchemy.create_engine(pg.get_connection_url())
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("CREATE TABLE orders (id int primary key); INSERT INTO orders VALUES (1)"))
    engine.dispose()
    asyncio.run(main(url))
