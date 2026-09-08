"""What happens to an around_call that keeps a ContextVar token across the yield, per RPC kind."""

from __future__ import annotations

import asyncio
import time
from contextvars import ContextVar
from importlib.metadata import version

import grpc
import grpc.aio

from grpc_client_kit import flatten_interceptors
from grpc_client_kit.interceptors.base import AsyncAroundClientInterceptor, ClientCall

SERVICE = "lab.Reports"
GET = f"/{SERVICE}/Get"
STREAM = f"/{SERVICE}/Stream"
UPLOAD = f"/{SERVICE}/Upload"
CHAT = f"/{SERVICE}/Chat"
REQUEST_ID: ContextVar[str | None] = ContextVar("request_id", default=None)

loop_errors: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)


class Reports:
    async def get(self, request, context):
        return b"ok"

    async def stream(self, request, context):
        fail_at = int(request) if request else 0
        for i in range(1, 4):
            if i == fail_at:
                await context.abort(grpc.StatusCode.UNAVAILABLE, f"died at item {i}")
            await asyncio.sleep(0.02)
            yield i.to_bytes(1, "big")

    async def upload(self, request_iterator, context):
        n = 0
        async for _ in request_iterator:
            n += 1
        return n.to_bytes(1, "big")

    async def chat(self, request_iterator, context):
        async for item in request_iterator:
            yield item


async def serve():
    server = grpc.aio.server()
    r = Reports()
    server.add_generic_rpc_handlers(
        (
            grpc.method_handlers_generic_handler(
                SERVICE,
                {
                    "Get": grpc.unary_unary_rpc_method_handler(r.get),
                    "Stream": grpc.unary_stream_rpc_method_handler(r.stream),
                    "Upload": grpc.stream_unary_rpc_method_handler(r.upload),
                    "Chat": grpc.stream_stream_rpc_method_handler(r.chat),
                },
            ),
        )
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    return server, f"127.0.0.1:{port}"


async def requests(n: int = 2):
    for i in range(n):
        yield i.to_bytes(1, "big")


class TokenAcrossYield(AsyncAroundClientInterceptor):
    """The obvious way to put a request id on every outgoing call."""

    def __init__(self) -> None:
        self.teardowns = 0

    async def around_call(self, call: ClientCall):
        token = REQUEST_ID.set("req-42")
        try:
            yield
        finally:
            self.teardowns += 1
            REQUEST_ID.reset(token)


class RaisingTeardown(AsyncAroundClientInterceptor):
    """Any teardown that fails, for whatever reason of its own."""

    async def around_call(self, call: ClientCall):
        try:
            yield
        finally:
            raise RuntimeError("the teardown itself failed")


async def probe(target: str, interceptor, kind: str, fail_at: int = 0) -> str:
    chain = flatten_interceptors([interceptor])
    async with grpc.aio.insecure_channel(target, interceptors=chain) as channel:
        try:
            if kind == "unary_unary":
                await channel.unary_unary(GET)(b"")
            elif kind == "unary_stream":
                async for _ in channel.unary_stream(STREAM)(str(fail_at).encode()):
                    pass
            elif kind == "stream_unary":
                await channel.stream_unary(UPLOAD)(requests())
            else:
                async for _ in channel.stream_stream(CHAT)(requests()):
                    pass
        except grpc.aio.AioRpcError as error:
            return f"caller got {error.code().name}: {error.details()}"
        except Exception as error:  # noqa: BLE001 - the probe reports whatever comes out
            return f"caller got {type(error).__name__}: {error}"
        await asyncio.sleep(0.2)  # let a teardown that runs elsewhere finish
        return "caller got the response"


async def main() -> None:
    asyncio.get_running_loop().set_exception_handler(
        lambda loop, ctx: loop_errors.append(f"{ctx.get('message')}: {ctx.get('exception')!r}")
    )
    log(f"grpc-client-kit {version('grpc-client-kit')}, grpcio {version('grpcio')}")
    server, target = await serve()
    try:
        log("--- an around_call that sets a ContextVar before the yield and resets it after")
        for kind in ("unary_unary", "unary_stream", "stream_unary", "stream_stream"):
            loop_errors.clear()
            outcome = await probe(target, TokenAcrossYield(), kind)
            log(f"    {kind:<14} {outcome}")
            for e in loop_errors:
                log(f"        loop exception handler: {e}")

        log("--- the same interceptor on a stream the server fails mid-way")
        loop_errors.clear()
        outcome = await probe(target, TokenAcrossYield(), "unary_stream", fail_at=2)
        log(f"    unary_stream   {outcome}")
        for e in loop_errors:
            log(f"        loop exception handler: {e}")

        log("--- any teardown that raises, per RPC kind")
        for kind in ("unary_unary", "unary_stream", "stream_unary", "stream_stream"):
            loop_errors.clear()
            outcome = await probe(target, RaisingTeardown(), kind)
            log(f"    {kind:<14} {outcome}")
            for e in loop_errors:
                log(f"        loop exception handler: {e}")
    finally:
        await server.stop(None)


if __name__ == "__main__":
    asyncio.run(main())
