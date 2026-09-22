"""A real local gRPC server with deterministic faults and in-memory effect counters."""
import asyncio
from collections import Counter
from contextlib import asynccontextmanager

import grpc
from grpc_flow import SERVICE


class Inventory:
    def __init__(self):
        self.attempts = Counter()
        self.reservations = 0

    async def get_stock(self, request, context):
        self.attempts[('stock', request)] += 1
        count = self.attempts[('stock', request)]
        if request == b'slow':
            await asyncio.sleep(0.18)
            await context.abort(grpc.StatusCode.UNAVAILABLE, 'still busy')
        if request == b'down' or (request == b'flaky' and count < 3):
            await context.abort(grpc.StatusCode.UNAVAILABLE, 'inventory restarting')
        return b'7'

    async def reserve(self, request, context):
        self.attempts[('reserve', request)] += 1
        self.reservations += 1
        await context.abort(grpc.StatusCode.UNAVAILABLE, 'reply failed after reserving stock')

    async def export(self, request, context):
        self.attempts[('export', request)] += 1
        count = self.attempts[('export', request)]
        for item in (1, 2, 3):
            if item == 3 and count == 1:
                await context.abort(grpc.StatusCode.UNAVAILABLE, 'stream interrupted')
            yield str(item).encode()


@asynccontextmanager
async def grpc_origin():
    inventory = Inventory()
    server = grpc.aio.server()
    server.add_generic_rpc_handlers((grpc.method_handlers_generic_handler(SERVICE, {
        'GetStock': grpc.unary_unary_rpc_method_handler(inventory.get_stock),
        'Reserve': grpc.unary_unary_rpc_method_handler(inventory.reserve),
        'Export': grpc.unary_stream_rpc_method_handler(inventory.export),
    }),))
    port = server.add_insecure_port('127.0.0.1:0')
    await server.start()
    try:
        yield inventory, f'127.0.0.1:{port}'
    finally:
        await server.stop(grace=0)
