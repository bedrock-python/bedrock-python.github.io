"""gRPC channels pooled by address, and pooled by everything gRPC baked into them."""

import asyncio

import grpc
import grpc.aio

from grpc_client_kit import ChannelPool, ConnectivityConfig, GrpcClient, GrpcClientConfig, RetryConfig, TimeoutConfig, build_interceptors

SERVICE = "lab.Ledger"


class Ledger:
    def __init__(self) -> None:
        self.attempts = 0

    async def post(self, request: bytes, context: grpc.aio.ServicerContext) -> bytes:
        self.attempts += 1
        await context.abort(grpc.StatusCode.UNAVAILABLE, "replica draining")
        return b""


class Stub:
    def __init__(self, channel: grpc.aio.Channel) -> None:
        self.post = channel.unary_unary(f"/{SERVICE}/Post")


async def serve(ledger: Ledger) -> tuple[grpc.aio.Server, str]:
    server = grpc.aio.server()
    server.add_generic_rpc_handlers((grpc.method_handlers_generic_handler(SERVICE, {"Post": grpc.unary_unary_rpc_method_handler(ledger.post)}),))
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    return server, f"127.0.0.1:{port}"


async def call(stub: Stub, ledger: Ledger) -> str:
    ledger.attempts = 0
    try:
        await stub.post(b"x")
        return "OK"
    except grpc.aio.AioRpcError as error:
        return f"{error.code().name} after {ledger.attempts} attempt(s) at the server"


async def main() -> None:
    ledger = Ledger()
    server, target = await serve(ledger)
    retrying = build_interceptors(timeout=TimeoutConfig(default=2.0), retry=RetryConfig(max_attempts=3, initial_backoff=0.01, jitter=0.0))
    plain = build_interceptors(timeout=TimeoutConfig(default=2.0))

    print("--- two clients, one address: a retrying orders client and a non-retrying audit client ---")
    by_address: dict[str, grpc.aio.Channel] = {}

    def naive_channel(address: str, interceptors) -> grpc.aio.Channel:
        """The pool most codebases write: one channel per address, whoever asked first wins."""
        if address not in by_address:
            from grpc_client_kit import flatten_interceptors
            by_address[address] = grpc.aio.insecure_channel(address, interceptors=flatten_interceptors(interceptors))
        return by_address[address]

    orders_stub = Stub(naive_channel(target, retrying))
    audit_stub = Stub(naive_channel(target, plain))
    print(f"  pool keyed by address:  orders -> {await call(orders_stub, ledger)}")
    print(f"                          audit  -> {await call(audit_stub, ledger)}   (the audit client inherited the orders client's retries)")
    for ch in by_address.values():
        await ch.close()

    async with ChannelPool() as pool:
        orders = GrpcClient(Stub, GrpcClientConfig(target=target, insecure=True), pool, interceptors=retrying)
        audit = GrpcClient(Stub, GrpcClientConfig(target=target, insecure=True), pool, interceptors=plain)
        async with orders as stub:
            print(f"  pool keyed by identity: orders -> {await call(stub, ledger)}")
        async with audit as stub:
            print(f"                          audit  -> {await call(stub, ledger)}   channels in the pool: {len(pool._entries)}")

    print("\n--- the chain rebuilt per request ---")
    async with ChannelPool() as pool:
        for i in range(5):
            chain = build_interceptors(timeout=TimeoutConfig(default=2.0))   # "a fresh chain, just to be safe"
            client = GrpcClient(Stub, GrpcClientConfig(target=target, insecure=True), pool, interceptors=chain)
            async with client as stub:
                await call(stub, ledger)
        print(f"  a chain built per call:  5 calls -> {len(pool._entries)} channels")
    async with ChannelPool() as pool:
        chain = build_interceptors(timeout=TimeoutConfig(default=2.0))
        for i in range(5):
            client = GrpcClient(Stub, GrpcClientConfig(target=target, insecure=True), pool, interceptors=chain)
            async with client as stub:
                await call(stub, ledger)
        print(f"  one chain per target:    5 calls -> {len(pool._entries)} channel(s)")

    print("\n--- same address, different keepalive: a channel argument is part of the identity ---")
    async with ChannelPool() as pool:
        for connectivity in (None, ConnectivityConfig(keepalive_time=10.0)):
            client = GrpcClient(Stub, GrpcClientConfig(target=target, insecure=True, connectivity=connectivity), pool, interceptors=plain)
            async with client as stub:
                await call(stub, ledger)
        print(f"  two connectivity configs -> {len(pool._entries)} channels")
    await server.stop(grace=None)


asyncio.run(main())
