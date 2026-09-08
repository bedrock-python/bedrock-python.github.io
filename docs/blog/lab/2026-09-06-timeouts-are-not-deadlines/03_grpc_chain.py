"""Gateway -> Orders -> (Inventory, then Billing). What each hop sees, and who keeps working after the caller left."""
import asyncio
import time
import grpc
import grpc.aio
from deadline_budget import BudgetContext
from grpc_client_kit import (
    ChannelPool,
    DeadlineBudgetConfig,
    GrpcClient,
    GrpcClientConfig,
    TimeoutConfig,
    build_interceptors,
    use_budget,
)
GATEWAY_TIMEOUT = 2.0   # what the gateway gives Orders
CONFIGURED = 5.0        # what Orders' client is configured with, per call
LEAF_WORK = 1.5         # how long Inventory and Billing each take
T0 = 0.0
log: list[str] = []
def stamp(who: str, text: str) -> None:
    log.append(f"  {time.perf_counter() - T0:5.2f} s  {who:<10} {text}")
def show(seconds):
    return "none" if seconds is None else f"{seconds:.2f} s"
class Leaf:
    def __init__(self, name: str) -> None:
        self.name = name
    async def handle(self, request: bytes, context: grpc.aio.ServicerContext) -> bytes:
        left = context.time_remaining()
        stamp(self.name, f"deadline seen {show(left)}")
        if left is not None and left < LEAF_WORK:
            stamp(self.name, f"refuses: {LEAF_WORK} s of work does not fit in {left:.2f} s")
            await context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "cannot finish in time")
        work = asyncio.ensure_future(self.commit(request))
        try:
            await asyncio.shield(work)  # a commit or a card charge: once started, it completes
        except asyncio.CancelledError:
            stamp(self.name, f"caller gone, but the {request.decode()} is already running")
            raise
        return b"ok"
    async def commit(self, request: bytes) -> None:
        await asyncio.sleep(LEAF_WORK)
        stamp(self.name, f"{request.decode()} completed")
class Stub:
    def __init__(self, channel: grpc.aio.Channel) -> None:
        self.call = channel.unary_unary("/lab.Leaf/Do")
class Orders:
    def __init__(self, pool: ChannelPool, inventory: str, billing: str, propagate: bool) -> None:
        chain = build_interceptors(
            timeout=TimeoutConfig(default=CONFIGURED),
            deadline_budget=DeadlineBudgetConfig() if propagate else None,
        )
        self.inventory = GrpcClient(Stub, GrpcClientConfig(target=inventory, insecure=True), pool, interceptors=chain)
        self.billing = GrpcClient(Stub, GrpcClientConfig(target=billing, insecure=True), pool, interceptors=chain)
        self.propagate = propagate
    async def handle(self, request: bytes, context: grpc.aio.ServicerContext) -> bytes:
        left = context.time_remaining()
        stamp("orders", f"deadline seen {show(left)}")
        budget = BudgetContext.create(total_seconds=left) if (self.propagate and left) else None
        try:
            with use_budget(budget):
                async with self.inventory as inventory:
                    await inventory.call(b"reserve")
                async with self.billing as billing:
                    await billing.call(b"charge")
        except grpc.aio.AioRpcError as error:
            stamp("orders", error.code().name)
            await context.abort(error.code(), "downstream failed")
        except asyncio.CancelledError:
            stamp("orders", "cancelled")
            raise
        return b"ok"
async def serve(service: str, handler) -> tuple[grpc.aio.Server, str]:
    server = grpc.aio.server()
    server.add_generic_rpc_handlers((grpc.method_handlers_generic_handler(service, {"Do": grpc.unary_unary_rpc_method_handler(handler)}),))
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    return server, f"127.0.0.1:{port}"
async def scenario(propagate: bool) -> None:
    global T0
    log.clear()
    inv_server, inv_target = await serve("lab.Leaf", Leaf("inventory").handle)
    bil_server, bil_target = await serve("lab.Leaf", Leaf("billing").handle)
    async with ChannelPool() as pool:
        orders = Orders(pool, inv_target, bil_target, propagate)
        ord_server, ord_target = await serve("lab.Orders", orders.handle)
        channel = grpc.aio.insecure_channel(ord_target)
        submit = channel.unary_unary("/lab.Orders/Do")
        T0 = time.perf_counter()
        stamp("gateway", f"calls orders, timeout {GATEWAY_TIMEOUT} s")
        try:
            await submit(b"order", timeout=GATEWAY_TIMEOUT)
            stamp("gateway", "OK")
        except grpc.aio.AioRpcError as error:
            stamp("gateway", error.code().name)
        await asyncio.sleep(3.5)  # let anything still running finish, so it shows in the log
        await channel.close()
        await ord_server.stop(grace=None)
    await inv_server.stop(grace=None)
    await bil_server.stop(grace=None)
    print("\n".join(log))
async def wide_budget() -> None:
    """A request with far more time left than the call is configured for does not extend the call."""
    log.clear()
    server, target = await serve("lab.Leaf", Leaf("billing").handle)
    async with ChannelPool() as pool:
        chain = build_interceptors(timeout=TimeoutConfig(default=CONFIGURED), deadline_budget=DeadlineBudgetConfig())
        client = GrpcClient(Stub, GrpcClientConfig(target=target, insecure=True), pool, interceptors=chain)
        global T0
        T0 = time.perf_counter()
        with use_budget(BudgetContext.create(total_seconds=50.0)):
            async with client as stub:
                await stub.call(b"charge")
    await server.stop(grace=None)
    print("\n".join(log))
async def main() -> None:
    print(f"--- fresh {CONFIGURED:.0f}s timeout per call ---")
    await scenario(propagate=False)
    print(f"\n--- the gateway's deadline propagated ---")
    await scenario(propagate=True)
    print(f"\n--- a 50s request budget against a {CONFIGURED:.0f}s configured timeout ---")
    await wide_budget()
asyncio.run(main())
