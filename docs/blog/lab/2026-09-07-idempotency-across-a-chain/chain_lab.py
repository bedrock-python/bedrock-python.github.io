"""One retry at the top of a chain, and what reaches the bottom.

Three services in one process — gateway, orders, payments — each calling the next over HTTP, each
with its own retries. Payments records every charge it performs. The lab plays four designs:

1. no idempotency anywhere;
2. every hop mints its own key per attempt, which is what a UUID in the handler looks like;
3. the caller's key travels down the chain and every hop keys on it;
4. no header at all, and every hop keys on a fingerprint of what it was asked to do.

The gateway's first attempt always times out after the charge has happened, which is the case that
makes retries dangerous: the work was done and the answer was lost.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import uuid
from importlib.metadata import version

import httpx
from redis.asyncio import Redis
from testcontainers.redis import RedisContainer

from idempotency_kit import AsyncIdempotencyCoordinator, IdempotencyDomainService, JsonResultAdapter
from idempotency_kit.infra.storage.redis.aio import RedisAsyncIdempotencyRepository

SLOW_FIRST_ATTEMPT = 1.5
CLIENT_TIMEOUT = 0.6
KEY_HEADER = "idempotency-key"


def log(msg: str) -> None:
    print(msg, flush=True)


class Charges:
    """What payments actually did, which is the only number that matters."""

    def __init__(self) -> None:
        self.performed: list[str] = []
        self.attempts = 0

    def reset(self) -> None:
        self.performed.clear()
        self.attempts = 0


def fingerprint(body: dict) -> str:
    return hashlib.blake2b(json.dumps(body, sort_keys=True).encode(), digest_size=16).hexdigest()


async def serve(handler) -> tuple[asyncio.AbstractServer, str]:
    """A minimal HTTP server: read the request, hand the body and headers to the handler."""

    async def connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            head = (await reader.readuntil(b"\r\n\r\n")).decode()
            headers = {}
            for line in head.split("\r\n")[1:]:
                if ": " in line:
                    name, value = line.split(": ", 1)
                    headers[name.lower()] = value
            length = int(headers.get("content-length", "0"))
            body = json.loads(await reader.readexactly(length)) if length else {}
            status, payload = await handler(body, headers)
            encoded = json.dumps(payload).encode()
            writer.write(
                f"HTTP/1.1 {status} X\r\nContent-Length: {len(encoded)}\r\nContent-Type: application/json\r\n\r\n".encode()
                + encoded
            )
            await writer.drain()
        except (asyncio.IncompleteReadError, ConnectionResetError, BrokenPipeError):
            pass
        finally:
            writer.close()

    server = await asyncio.start_server(connection, "127.0.0.1", 0)
    return server, f"http://127.0.0.1:{server.sockets[0].getsockname()[1]}"


async def run_design(
    label: str,
    charges: Charges,
    coordinator: AsyncIdempotencyCoordinator,
    *,
    propagate: bool,
    mint_per_attempt: bool,
    use_fingerprint: bool,
    protected: bool,
) -> None:
    charges.reset()

    async def payments_handler(body: dict, headers: dict) -> tuple[int, dict]:
        charges.attempts += 1

        async def charge() -> dict:
            if charges.attempts == 1:
                await asyncio.sleep(SLOW_FIRST_ATTEMPT)     # the answer is lost; the charge is not
            charges.performed.append(body["order_id"])
            return {"charged": body["order_id"], "charge_id": str(uuid.uuid4())}

        if not protected:
            return 200, await charge()
        key = fingerprint(body) if use_fingerprint else headers.get(KEY_HEADER) or str(uuid.uuid4())
        result = await coordinator.coordinate("payment.charge", key, 300, JsonResultAdapter(), charge)
        return 200, result

    payments_server, payments_url = await serve(payments_handler)

    async def orders_handler(body: dict, headers: dict) -> tuple[int, dict]:
        async def place() -> dict:
            outbound = {}
            if propagate and headers.get(KEY_HEADER):
                outbound[KEY_HEADER] = headers[KEY_HEADER]
            elif mint_per_attempt:
                outbound[KEY_HEADER] = str(uuid.uuid4())    # a fresh key on every attempt
            async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
                for attempt in range(2):                    # orders has its own retry
                    try:
                        response = await client.post(f"{payments_url}/charge", json=body, headers=outbound)
                        return response.json()
                    except httpx.HTTPError:
                        if attempt == 1:
                            raise
            raise RuntimeError("unreachable")

        if not protected:
            return 200, await place()
        key = fingerprint(body) if use_fingerprint else headers.get(KEY_HEADER) or str(uuid.uuid4())
        return 200, await coordinator.coordinate("order.place", key, 300, JsonResultAdapter(), place)

    orders_server, orders_url = await serve(orders_handler)

    # The gateway: one request, one retry after its own timeout.
    body = {"order_id": "order-42", "amount": 100}
    caller_key = str(uuid.uuid4())
    headers = {KEY_HEADER: caller_key} if (propagate or mint_per_attempt) else {}
    outcome = "no answer"
    async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
        for attempt in range(2):
            try:
                response = await client.post(f"{orders_url}/place", json=body, headers=headers)
                outcome = f"answered on attempt {attempt + 1}"
                break
            except httpx.HTTPError:
                if mint_per_attempt:
                    headers = {KEY_HEADER: str(uuid.uuid4())}   # the mistake: a new key per attempt
                continue

    await asyncio.sleep(SLOW_FIRST_ATTEMPT + 0.2)          # let the abandoned attempt finish its work

    # The caller comes back once more, the way a user pressing the button again does.
    late = "not tried"
    charged_before_late = len(charges.performed)
    async with httpx.AsyncClient(timeout=3.0) as client:
        started = asyncio.get_running_loop().time()
        try:
            response = await client.post(f"{orders_url}/place", json=body, headers=headers)
            elapsed = (asyncio.get_running_loop().time() - started) * 1000
            late = f"answered in {elapsed:.0f} ms, charged again: {len(charges.performed) > charged_before_late}"
        except httpx.HTTPError as error:
            late = f"{type(error).__name__}"

    orders_server.close()
    payments_server.close()
    log(f"  {label:<44} charged {len(charges.performed)} time(s); the caller {outcome}; "
        f"a later retry {late}")


async def main() -> None:
    with RedisContainer("redis:7-alpine") as container:
        redis = Redis.from_url(
            f"redis://{container.get_container_host_ip()}:{container.get_exposed_port(6379)}/0"
        )
        coordinator = AsyncIdempotencyCoordinator(
            RedisAsyncIdempotencyRepository(redis, key_prefix="idem:"),
            IdempotencyDomainService(default_ttl_minutes=30),
            in_flight="wait",
        )
        log(f"idempotency-kit {version('idempotency-kit')}, httpx {version('httpx')}")
        log(f"--- one order, a gateway that gives up after {CLIENT_TIMEOUT:.1f} s and retries once")
        charges = Charges()
        await run_design("no idempotency anywhere", charges, coordinator,
                         propagate=False, mint_per_attempt=False, use_fingerprint=False, protected=False)
        await redis.flushall()
        await run_design("a fresh key per attempt, per hop", charges, coordinator,
                         propagate=False, mint_per_attempt=True, use_fingerprint=False, protected=True)
        await redis.flushall()
        await run_design("the caller's key, propagated", charges, coordinator,
                         propagate=True, mint_per_attempt=False, use_fingerprint=False, protected=True)
        await redis.flushall()
        await run_design("no header, a fingerprint per hop", charges, coordinator,
                         propagate=False, mint_per_attempt=False, use_fingerprint=True, protected=True)
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(main())
