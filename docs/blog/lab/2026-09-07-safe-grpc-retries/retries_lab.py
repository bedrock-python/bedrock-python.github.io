"""Which gRPC status codes are safe to retry, measured against a server that counts what it did."""

import asyncio
import time
from dataclasses import dataclass, field

import grpc
import grpc.aio

from grpc_client_kit import (
    ChannelPool,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    GrpcClient,
    GrpcClientConfig,
    RetryConfig,
    TimeoutConfig,
    build_interceptors,
)

SERVICE = "lab.Payments"
CHARGE = f"/{SERVICE}/Charge"
EXPORT = f"/{SERVICE}/Export"


@dataclass
class Payments:
    """One handler, several behaviours chosen by the request. `charges` is the side effect."""

    charges: int = 0
    attempts: int = 0
    items_sent: list[int] = field(default_factory=list)

    def reset(self) -> None:
        self.charges = 0
        self.attempts = 0
        self.items_sent.clear()

    async def charge(self, request: bytes, context: grpc.aio.ServicerContext) -> bytes:
        self.attempts += 1
        mode = request.decode()
        if mode == "unavailable-before-work" and self.attempts == 1:
            await context.abort(grpc.StatusCode.UNAVAILABLE, "draining, try another replica")
        if mode == "slow-then-unavailable":
            await asyncio.sleep(1.5)
            await context.abort(grpc.StatusCode.UNAVAILABLE, "overloaded")
        self.charges += 1  # the card is charged here
        if mode == "internal-after-write":
            await context.abort(grpc.StatusCode.INTERNAL, "ledger write failed after the charge")
        if mode == "unavailable-after-write":
            await context.abort(grpc.StatusCode.UNAVAILABLE, "replica shut down after the charge")
        return b"ok"

    async def export(self, request: bytes, context: grpc.aio.ServicerContext):
        self.attempts += 1
        for i in range(1, 6):
            if i == 3 and self.attempts == 1:
                await context.abort(grpc.StatusCode.UNAVAILABLE, "stream broke")
            self.items_sent.append(i)
            yield i.to_bytes(1, "big")


class Stub:
    def __init__(self, channel: grpc.aio.Channel) -> None:
        self.charge = channel.unary_unary(CHARGE)
        self.export = channel.unary_stream(EXPORT)


async def serve(payments: Payments) -> tuple[grpc.aio.Server, str]:
    server = grpc.aio.server()
    server.add_generic_rpc_handlers((grpc.method_handlers_generic_handler(SERVICE, {
        "Charge": grpc.unary_unary_rpc_method_handler(payments.charge),
        "Export": grpc.unary_stream_rpc_method_handler(payments.export),
    }),))
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    return server, f"127.0.0.1:{port}"


async def call(pool, target, payments, mode, *, retry, timeout=TimeoutConfig(default=5.0), breaker=None, label):
    payments.reset()
    chain = build_interceptors(timeout=timeout, retry=retry, circuit_breaker=breaker)
    client = GrpcClient(Stub, GrpcClientConfig(target=target, insecure=True), pool, interceptors=chain)
    started = time.perf_counter()
    try:
        async with client as stub:
            await stub.charge(mode.encode())
        result = "OK"
    except CircuitBreakerOpenError:
        result = "CircuitBreakerOpenError"
    except grpc.aio.AioRpcError as error:
        result = error.code().name
    took = time.perf_counter() - started
    print(f"  {label:<52} -> {result:<24} attempts={payments.attempts} charges={payments.charges}  {took:.2f}s")


async def main() -> None:
    payments = Payments()
    server, target = await serve(payments)
    default = RetryConfig(max_attempts=3, initial_backoff=0.05, jitter=0.0)
    async with ChannelPool() as pool:
        print("--- the codes: what the default policy retries ---")
        await call(pool, target, payments, "unavailable-before-work", retry=default,
                   label="UNAVAILABLE before the handler ran")
        await call(pool, target, payments, "internal-after-write", retry=default,
                   label="INTERNAL after the charge, default policy")
        await call(pool, target, payments, "internal-after-write",
                   retry=RetryConfig(max_attempts=3, initial_backoff=0.05, jitter=0.0,
                                     retryable_codes={grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.INTERNAL}),
                   label="INTERNAL after the charge, INTERNAL made retryable")
        await call(pool, target, payments, "unavailable-after-write", retry=default,
                   label="UNAVAILABLE after the charge, default policy")
        await call(pool, target, payments, "unavailable-after-write",
                   retry=RetryConfig(max_attempts=3, initial_backoff=0.05, jitter=0.0, idempotent_methods={EXPORT}),
                   label="UNAVAILABLE after the charge, Charge not in idempotent_methods")

        print("\n--- the deadline: three attempts do not triple it ---")
        await call(pool, target, payments, "slow-then-unavailable",
                   retry=RetryConfig(max_attempts=3, initial_backoff=0.1, jitter=0.0), timeout=TimeoutConfig(default=2.0),
                   label="1.5 s then UNAVAILABLE, timeout 2.0 s, 3 attempts allowed")

        print("\n--- the breaker counts attempts, not calls ---")
        await call(pool, target, payments, "unavailable-after-write", retry=default,
                   breaker=CircuitBreakerConfig(fail_threshold=2, recovery_timeout=60.0),
                   label="fail_threshold=2 under max_attempts=3, first call")
        await call(pool, target, payments, "unavailable-before-work", retry=default,
                   breaker=CircuitBreakerConfig(fail_threshold=2, recovery_timeout=60.0),
                   label="fail_threshold=2 under max_attempts=3, first call, recoverable")

        print("\n--- streams ---")
        for label, retry in (
            ("unary-stream breaks at item 3, default policy", default),
            ("same, retry_streaming=True and Export in idempotent_methods",
             RetryConfig(max_attempts=3, initial_backoff=0.05, jitter=0.0, retry_streaming=True, idempotent_methods={EXPORT})),
        ):
            payments.reset()
            chain = build_interceptors(timeout=TimeoutConfig(default=5.0), retry=retry)
            client = GrpcClient(Stub, GrpcClientConfig(target=target, insecure=True), pool, interceptors=chain)
            received: list[int] = []
            try:
                async with client as stub:
                    async for item in stub.export(b"x"):
                        received.append(int.from_bytes(item, "big"))
                result = "OK"
            except grpc.aio.AioRpcError as error:
                result = error.code().name
            print(f"  {label:<62} -> {result:<12} client received {received}  server attempts={payments.attempts}")
    await server.stop(grace=None)


asyncio.run(main())
