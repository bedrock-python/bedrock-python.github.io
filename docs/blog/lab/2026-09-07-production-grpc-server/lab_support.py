"""Local fixtures and bounded calls; no database or external monitoring service is used."""
import asyncio
from contextlib import asynccontextmanager, nullcontext
import json

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc

from grpc_flow import METHOD, SERVICE
from invoice_domain import InvoiceStoreUnavailable, PrivateLedgerError

PRIVATE_MARKER = "private-ledger-location"


class InvoiceStore:
    def __init__(self, *, blocked=False):
        self.up = True
        self.active = 0
        self.reads = 0
        self.closed = False
        self.started = asyncio.Event()
        self.cleaned = asyncio.Event()
        self.release = asyncio.Event()
        self.ping_release = asyncio.Event()
        self.ping_release.set()
        if not blocked:
            self.release.set()

    @asynccontextmanager
    async def read(self, order_id):
        self.reads += 1
        self.active += 1
        self.started.set()
        try:
            await self.release.wait()
            if order_id == "offline":
                raise InvoiceStoreUnavailable("Invoice storage is unavailable")
            if order_id == "private":
                raise PrivateLedgerError(PRIVATE_MARKER, params={"row": "private-row"})
            if order_id == "bug":
                raise RuntimeError(PRIVATE_MARKER)
            if order_id == "value-bug":
                raise ValueError(PRIVATE_MARKER)
            if order_id == "missing":
                yield None
            else:
                yield {
                    "buyer_id": "someone-else" if order_id == "foreign" else "buyer-7",
                    "paid": order_id != "unpaid",
                    "invoice_id": "inv-42", "amount": 1999,
                }
        finally:
            self.active -= 1
            self.cleaned.set()

    async def ping(self):
        await self.ping_release.wait()
        return self.up

    async def close(self):
        assert self.active == 0, "A shared resource closed before its RPCs finished"
        self.closed = True


class Metrics:
    def __init__(self):
        self.rows = []

    def record_request(self, **values):
        self.rows.append(values)


class Reporter:
    def __init__(self):
        self.errors = []

    def isolate(self):
        return nullcontext()

    def set_tags(self, **tags):
        pass

    def add_breadcrumb(self, **values):
        pass

    def capture_exception(self, error):
        self.errors.append(type(error).__name__)


async def call(channel, order_id="ready", *, timeout=2):
    data = order_id.encode() if isinstance(order_id, str) else order_id
    return await channel.unary_unary(METHOD)(data, timeout=timeout)


async def expect_error(awaitable, code, details=None):
    try:
        await awaitable
    except grpc.aio.AioRpcError as error:
        assert error.code() == code, (error.code(), error.details())
        if details is not None:
            assert error.details() == details, error.details()
        return error
    raise AssertionError(f"Expected {code.name}")


async def health(channel, service=SERVICE):
    reply = await health_pb2_grpc.HealthStub(channel).Check(
        health_pb2.HealthCheckRequest(service=service), timeout=2,
    )
    return health_pb2.HealthCheckResponse.ServingStatus.Name(reply.status)


async def wait_until(predicate):
    async with asyncio.timeout(5):
        while not predicate():
            await asyncio.sleep(0.01)


def result(data):
    return json.loads(data)
