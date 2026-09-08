"""What a client interceptor actually sees when the RPC is a stream.

One in-process gRPC server with all four RPC kinds, and four client-side interceptors asked the
same questions: how many of the four kinds did the channel register you for, how long did you
measure the call, did you see the failure, was your context still set while the items arrived,
and does the caller still get a call object afterwards.
"""

from __future__ import annotations

import asyncio
import time
from collections import Counter
from contextvars import ContextVar
from importlib.metadata import version
from typing import Any

import grpc
import grpc.aio

from grpc_client_kit.interceptors.base import AsyncAroundClientInterceptor, ClientCall

SERVICE = "lab.Reports"
GET = f"/{SERVICE}/Get"
STREAM = f"/{SERVICE}/Stream"
UPLOAD = f"/{SERVICE}/Upload"
CHAT = f"/{SERVICE}/Chat"

ITEMS = 5
GAP = 0.12
REQUEST_ID: ContextVar[str | None] = ContextVar("request_id", default=None)


def log(msg: str) -> None:
    print(msg, flush=True)


class Reports:
    """The server. `Stream` sends five items with a gap, and fails mid-stream when asked to."""

    async def get(self, request: bytes, context: grpc.aio.ServicerContext) -> bytes:
        await asyncio.sleep(GAP)
        return b"ok"

    async def stream(self, request: bytes, context: grpc.aio.ServicerContext):
        fail_at = int(request) if request else 0
        for i in range(1, ITEMS + 1):
            if i == fail_at:
                await context.abort(grpc.StatusCode.UNAVAILABLE, f"report generator died at item {i}")
            await asyncio.sleep(GAP)
            yield i.to_bytes(1, "big")

    async def upload(self, request_iterator, context: grpc.aio.ServicerContext) -> bytes:
        n = 0
        async for _ in request_iterator:
            n += 1
        return n.to_bytes(1, "big")

    async def chat(self, request_iterator, context: grpc.aio.ServicerContext):
        async for item in request_iterator:
            await asyncio.sleep(GAP)
            yield item


async def serve() -> tuple[grpc.aio.Server, str]:
    server = grpc.aio.server()
    reports = Reports()
    server.add_generic_rpc_handlers(
        (
            grpc.method_handlers_generic_handler(
                SERVICE,
                {
                    "Get": grpc.unary_unary_rpc_method_handler(reports.get),
                    "Stream": grpc.unary_stream_rpc_method_handler(reports.stream),
                    "Upload": grpc.stream_unary_rpc_method_handler(reports.upload),
                    "Chat": grpc.stream_stream_rpc_method_handler(reports.chat),
                },
            ),
        )
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    return server, f"127.0.0.1:{port}"


async def requests(n: int = 3):
    for i in range(n):
        yield i.to_bytes(1, "big")


async def run_all_four(channel: grpc.aio.Channel) -> None:
    """One call of each kind, responses drained."""
    await channel.unary_unary(GET)(b"")
    async for _ in channel.unary_stream(STREAM)(b"0"):
        pass
    await channel.stream_unary(UPLOAD)(requests())
    async for _ in channel.stream_stream(CHAT)(requests()):
        pass


# --- 1. registration ------------------------------------------------------------------------


class EverythingInterceptor(
    grpc.aio.UnaryUnaryClientInterceptor,
    grpc.aio.UnaryStreamClientInterceptor,
    grpc.aio.StreamUnaryClientInterceptor,
    grpc.aio.StreamStreamClientInterceptor,
):
    """The interceptor everyone writes first: one class, all four methods."""

    def __init__(self) -> None:
        self.calls: Counter[str] = Counter()

    async def intercept_unary_unary(self, continuation, details, request):
        self.calls["unary_unary"] += 1
        return await continuation(details, request)

    async def intercept_unary_stream(self, continuation, details, request):
        self.calls["unary_stream"] += 1
        return await continuation(details, request)

    async def intercept_stream_unary(self, continuation, details, request_iterator):
        self.calls["stream_unary"] += 1
        return await continuation(details, request_iterator)

    async def intercept_stream_stream(self, continuation, details, request_iterator):
        self.calls["stream_stream"] += 1
        return await continuation(details, request_iterator)


class OneKindInterceptor:
    """The same four methods, one object per kind."""

    def __init__(self, calls: Counter[str]) -> None:
        self.calls = calls


class UnaryUnaryOnly(OneKindInterceptor, grpc.aio.UnaryUnaryClientInterceptor):
    async def intercept_unary_unary(self, continuation, details, request):
        self.calls["unary_unary"] += 1
        return await continuation(details, request)


class UnaryStreamOnly(OneKindInterceptor, grpc.aio.UnaryStreamClientInterceptor):
    async def intercept_unary_stream(self, continuation, details, request):
        self.calls["unary_stream"] += 1
        return await continuation(details, request)


class StreamUnaryOnly(OneKindInterceptor, grpc.aio.StreamUnaryClientInterceptor):
    async def intercept_stream_unary(self, continuation, details, request_iterator):
        self.calls["stream_unary"] += 1
        return await continuation(details, request_iterator)


class StreamStreamOnly(OneKindInterceptor, grpc.aio.StreamStreamClientInterceptor):
    async def intercept_stream_stream(self, continuation, details, request_iterator):
        self.calls["stream_stream"] += 1
        return await continuation(details, request_iterator)


def registered(channel: grpc.aio.Channel) -> str:
    lists = {
        "unary_unary": "_unary_unary_interceptors",
        "unary_stream": "_unary_stream_interceptors",
        "stream_unary": "_stream_unary_interceptors",
        "stream_stream": "_stream_stream_interceptors",
    }
    return ", ".join(f"{k}={len(getattr(channel, attr, []) or [])}" for k, attr in lists.items())


async def part_registration(target: str) -> None:
    log("--- 1. which of the four kinds the channel registers an interceptor for")
    everything = EverythingInterceptor()
    async with grpc.aio.insecure_channel(target, interceptors=[everything]) as channel:
        log(f"    one object inheriting all four ABCs, channel lists: {registered(channel)}")
        await run_all_four(channel)
    for kind in ("unary_unary", "unary_stream", "stream_unary", "stream_stream"):
        log(f"    {kind:<14} intercept ran {everything.calls[kind]} time(s)")

    calls: Counter[str] = Counter()
    four = [UnaryUnaryOnly(calls), UnaryStreamOnly(calls), StreamUnaryOnly(calls), StreamStreamOnly(calls)]
    async with grpc.aio.insecure_channel(target, interceptors=four) as channel:
        log(f"    four objects, one ABC each, channel lists: {registered(channel)}")
        await run_all_four(channel)
    for kind in ("unary_unary", "unary_stream", "stream_unary", "stream_stream"):
        log(f"    {kind:<14} intercept ran {calls[kind]} time(s)")


# --- 2. the wrapper that works for unary ----------------------------------------------------


class NaiveObservability(grpc.aio.UnaryUnaryClientInterceptor, grpc.aio.UnaryStreamClientInterceptor):
    """Timing, error counting and a request id, written the way a unary interceptor is written."""

    def __init__(self) -> None:
        self.measured_ms = 0.0
        self.errors = 0
        self.id_during_call: str | None = "not read"

    async def intercept_unary_unary(self, continuation, details, request):
        return await self._observe(continuation, details, request)

    async def intercept_unary_stream(self, continuation, details, request):
        return await self._observe(continuation, details, request)

    async def _observe(self, continuation, details, request):
        token = REQUEST_ID.set("req-42")
        started = time.perf_counter()
        try:
            return await continuation(details, request)
        except grpc.aio.AioRpcError:
            self.errors += 1
            raise
        finally:
            self.measured_ms = (time.perf_counter() - started) * 1000
            REQUEST_ID.reset(token)


class StreamAwareObservability(grpc.aio.UnaryStreamClientInterceptor):
    """The same three jobs, done around the whole response stream."""

    def __init__(self) -> None:
        self.measured_ms = 0.0
        self.errors = 0

    async def intercept_unary_stream(self, continuation, details, request):
        started = time.perf_counter()
        call = await continuation(details, request)

        async def wrapped():
            token = REQUEST_ID.set("req-42")
            try:
                async for item in call:
                    yield item
            except grpc.aio.AioRpcError:
                self.errors += 1
                raise
            finally:
                self.measured_ms = (time.perf_counter() - started) * 1000
                REQUEST_ID.reset(token)

        return wrapped()


class KitObservability(AsyncAroundClientInterceptor):
    """The same three jobs as one implementation, for all four kinds."""

    def __init__(self) -> None:
        self.measured_ms: dict[str, float] = {}
        self.errors = 0
        self.kinds: Counter[str] = Counter()

    async def around_call(self, call: ClientCall):
        self.kinds[call.rpc_type.value if hasattr(call.rpc_type, "value") else str(call.rpc_type)] += 1
        token = REQUEST_ID.set("req-42")
        started = time.perf_counter()
        try:
            yield
        except grpc.aio.AioRpcError:
            self.errors += 1
            raise
        finally:
            self.measured_ms[call.method] = (time.perf_counter() - started) * 1000
            REQUEST_ID.reset(token)


async def consume(channel: grpc.aio.Channel, fail_at: int) -> tuple[float, int, str | None, str]:
    """Read the stream to its end; return wall time, items seen, the id seen, and the outcome."""
    started = time.perf_counter()
    seen = 0
    id_seen: str | None = None
    outcome = "ok"
    call = channel.unary_stream(STREAM)(str(fail_at).encode())
    try:
        async for _ in call:
            seen += 1
            if seen == 1:
                id_seen = REQUEST_ID.get()
    except grpc.aio.AioRpcError as error:
        outcome = f"{error.code().name}: {error.details()}"
    return (time.perf_counter() - started) * 1000, seen, id_seen, outcome


async def part_wrapper(target: str) -> None:
    log(f"--- 2. a unary-stream call of {ITEMS} items, {GAP * 1000:.0f} ms apart, that fails at item 3")

    naive = NaiveObservability()
    async with grpc.aio.insecure_channel(target, interceptors=[naive]) as channel:
        wall, seen, id_seen, outcome = await consume(channel, fail_at=0)
        log(f"    unary-style wrapper, healthy stream: it measured {naive.measured_ms:.0f} ms")
        log(f"      the caller waited {wall:.0f} ms for {seen} items; request id during the stream: {id_seen!r}")
        wall, seen, id_seen, outcome = await consume(channel, fail_at=3)
        log(f"    unary-style wrapper, failing stream: it counted {naive.errors} errors, measured {naive.measured_ms:.0f} ms")
        log(f"      the caller waited {wall:.0f} ms, got {seen} items and then {outcome}")

    aware = StreamAwareObservability()
    async with grpc.aio.insecure_channel(target, interceptors=[aware]) as channel:
        wall, seen, id_seen, outcome = await consume(channel, fail_at=0)
        log(f"    stream-aware wrapper, healthy stream: it measured {aware.measured_ms:.0f} ms")
        log(f"      the caller waited {wall:.0f} ms for {seen} items; request id during the stream: {id_seen!r}")
        wall, seen, id_seen, outcome = await consume(channel, fail_at=3)
        log(f"    stream-aware wrapper, failing stream: it counted {aware.errors} errors, measured {aware.measured_ms:.0f} ms")
        log(f"      the caller waited {wall:.0f} ms, got {seen} items and then {outcome}")


# --- 3. what the caller is left holding -----------------------------------------------------


async def call_surface(channel: grpc.aio.Channel, label: str) -> None:
    call = channel.unary_stream(STREAM)(b"0")
    async for _ in call:
        pass
    answers = []
    for name in ("code", "details", "trailing_metadata"):
        member = getattr(call, name, None)
        if member is None:
            answers.append(f"{name}(): AttributeError")
            continue
        try:
            value = await member()
            answers.append(f"{name}()={getattr(value, 'name', value)!r}")
        except Exception as error:  # noqa: BLE001 - the lab reports whatever comes out
            answers.append(f"{name}(): {type(error).__name__}")
    log(f"    {label:<28} {'; '.join(answers)}")


async def part_surface(target: str) -> None:
    log("--- 3. what the caller can still ask the call after the stream ended")
    async with grpc.aio.insecure_channel(target) as channel:
        await call_surface(channel, "no interceptor")
    async with grpc.aio.insecure_channel(target, interceptors=[NaiveObservability()]) as channel:
        await call_surface(channel, "unary-style wrapper")
    async with grpc.aio.insecure_channel(target, interceptors=[StreamAwareObservability()]) as channel:
        await call_surface(channel, "hand-rolled stream wrapper")
    kit = KitObservability()
    from grpc_client_kit import flatten_interceptors

    async with grpc.aio.insecure_channel(target, interceptors=flatten_interceptors([kit])) as channel:
        await call_surface(channel, "the kit's around interceptor")


# --- 4. one implementation, four kinds ------------------------------------------------------


async def part_kit(target: str) -> None:
    from grpc_client_kit import flatten_interceptors

    log("--- 4. one around_call, all four kinds")
    kit = KitObservability()
    chain = flatten_interceptors([kit])
    log(f"    flatten_interceptors([one logical interceptor]) -> {len(chain)} channel entries")
    async with grpc.aio.insecure_channel(target, interceptors=chain) as channel:
        log(f"    channel lists: {registered(channel)}")
        await run_all_four(channel)
        await asyncio.sleep(0.1)  # the teardown of a streaming call outlives the last item
        for kind, n in sorted(kit.kinds.items()):
            log(f"    {kind:<14} around_call ran {n} time(s)")
        for method, ms in sorted(kit.measured_ms.items()):
            log(f"    measured {method:<22} {ms:.0f} ms")

    kit_fail = KitObservability()
    async with grpc.aio.insecure_channel(target, interceptors=flatten_interceptors([kit_fail])) as channel:
        wall, seen, id_seen, outcome = await consume(channel, fail_at=3)
        await asyncio.sleep(0.1)
        log(f"    failing stream: around_call counted {kit_fail.errors} errors, measured "
            f"{kit_fail.measured_ms.get(STREAM, 0):.0f} ms")
        log(f"      the caller waited {wall:.0f} ms, got {seen} items and then {outcome}")
        log(f"      request id during the stream: {id_seen!r}")


async def main() -> None:
    log(f"grpc-client-kit {version('grpc-client-kit')}, grpcio {version('grpcio')}")
    server, target = await serve()
    try:
        await part_registration(target)
        await part_wrapper(target)
        await part_surface(target)
        await part_kit(target)
    finally:
        await server.stop(None)


if __name__ == "__main__":
    asyncio.run(main())
