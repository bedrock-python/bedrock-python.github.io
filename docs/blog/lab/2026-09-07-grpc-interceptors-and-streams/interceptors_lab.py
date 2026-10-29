"""Assert registration, stream outcomes, cancellation and the boundary of RPC timing."""

import asyncio
from collections import Counter
from importlib.metadata import version
from time import perf_counter

import grpc
from grpc_client_kit import flatten_interceptors

from consumer import download, first_row
from observers import (
    EverythingInterceptor,
    IterationTimer,
    Observability,
    REQUEST_ID,
    SetupTimer,
)
from report_service import ITEMS, KINDS, STREAM, UPLOAD, invoke, serve


async def next_record(observer):
    return await asyncio.wait_for(observer.finished.get(), timeout=5)


async def registration(target):
    wrong = EverythingInterceptor()
    async with grpc.aio.insecure_channel(target, interceptors=[wrong]) as channel:
        for kind in KINDS:
            await invoke(channel, kind)
    assert wrong.calls == Counter(unary_unary=1), wrong.calls
    observer = Observability()
    chain = flatten_interceptors([observer])
    assert len(chain) == 4
    records = []
    async with grpc.aio.insecure_channel(target, interceptors=chain) as channel:
        for kind in KINDS:
            await invoke(channel, kind)
            records.append(await next_record(observer))
    assert Counter(record["kind"] for record in records) == Counter(KINDS)
    assert all(record["outcome"] == "OK" for record in records)
    assert observer.finished.empty()
    print(
        "PASS registration: multiple inheritance=1 kind; flattened logical interceptor=4 kinds",
        flush=True,
    )


async def measure(target, interceptor, request):
    async with grpc.aio.insecure_channel(
        target, interceptors=flatten_interceptors([interceptor])
    ) as channel:
        await channel.channel_ready()
        call = channel.unary_stream(STREAM)(request, timeout=5)
        started = perf_counter()
        seen = []
        outcome = "OK"
        try:
            async for row in call:
                if not seen:
                    if isinstance(interceptor, SetupTimer):
                        assert (
                            interceptor.entered == 1 and interceptor.finished.is_set()
                        )
                    elif isinstance(interceptor, IterationTimer):
                        assert not interceptor.finished.is_set()
                seen.append(row)
        except grpc.aio.AioRpcError as error:
            outcome = error.code().name
            assert error.details() == "report generator failed at row 3"
        wall = perf_counter() - started
        expected = "UNAVAILABLE" if request == b"fail" else "OK"
        assert outcome == expected and (await call.code()).name == expected
        assert await call.details() == ("report generator failed at row 3" if request == b"fail" else "")
        assert seen == (ITEMS[:2] if request == b"fail" else ITEMS)
        assert dict(await call.trailing_metadata()) == {"report-id": "r-42"}
        if isinstance(interceptor, Observability):
            record = await next_record(interceptor)
            assert record["outcome"] == expected
            assert interceptor.finished.empty()
            measured = record["seconds"]
        else:
            assert interceptor.finished.is_set()
            assert interceptor.errors == (
                int(request == b"fail")
                if isinstance(interceptor, IterationTimer)
                else 0
            )
            measured = interceptor.seconds
        assert measured is not None and measured >= 0
        print(
            f"  {type(interceptor).__name__:<16} {expected:<11} rows={len(seen)} measured={measured * 1000:.1f}ms consumer={wall * 1000:.1f}ms",
            flush=True,
        )


async def cancel_early(target, reports):
    observer = Observability()
    async with grpc.aio.insecure_channel(
        target, interceptors=flatten_interceptors([observer])
    ) as channel:
        assert await first_row(channel) == ITEMS[0]
        record = await next_record(observer)
        assert record["outcome"] == "CANCELLED" and record["request_id"] == "req-42"
        await asyncio.wait_for(reports.hold_closed.wait(), timeout=5)
        assert REQUEST_ID.get() is None and observer.finished.empty()
    print(
        "PASS early exit: explicit cancel, server stops, one CANCELLED record, caller context restored",
        flush=True,
    )


async def break_is_not_cancel(target, reports):
    reports.holding.clear()
    reports.hold_closed.clear()
    observer = Observability()
    async with grpc.aio.insecure_channel(
        target, interceptors=flatten_interceptors([observer])
    ) as channel:
        call = channel.unary_stream(STREAM)(b"hold", timeout=5)
        try:
            async for row in call:
                assert row == ITEMS[0]
                break
            await asyncio.wait_for(reports.holding.wait(), timeout=5)
            assert not call.done() and observer.finished.empty()
        finally:
            call.cancel()
        assert (await next_record(observer))["outcome"] == "CANCELLED"
        assert await call.code() == grpc.StatusCode.CANCELLED
        await asyncio.wait_for(reports.hold_closed.wait(), timeout=5)
        assert observer.finished.empty()
    print(
        "PASS break alone leaves RPC active; cancel closes it without waiting for garbage collection",
        flush=True,
    )


async def rpc_is_not_consumer_time(target):
    observer = Observability()
    async with grpc.aio.insecure_channel(
        target, interceptors=flatten_interceptors([observer])
    ) as channel:
        call = channel.unary_stream(STREAM)(b"fast", timeout=5)
        iterator = call.__aiter__()
        rows = [await anext(iterator) for _ in ITEMS]
        # The consumer has the final row but has not resumed the iterator for EOF.
        assert await call.code() == grpc.StatusCode.OK
        assert (await next_record(observer))["outcome"] == "OK"
        assert rows == ITEMS
        assert [row async for row in iterator] == []
        assert observer.finished.empty()
    print(
        "PASS timing boundary: RPC finalized before the consumer resumed past the final row",
        flush=True,
    )


async def write_style(target):
    observer = Observability()
    async with grpc.aio.insecure_channel(
        target, interceptors=flatten_interceptors([observer])
    ) as channel:
        call = channel.stream_unary(UPLOAD)(timeout=5)
        for row in ITEMS[:3]:
            await call.write(row)
        await call.done_writing()
        assert await call == bytes([3])
        assert (await next_record(observer))["outcome"] == "OK"
        assert observer.finished.empty()
    print(
        "PASS stream-unary write()/done_writing(): no interceptor deadlock", flush=True
    )


async def main():
    print(
        f"grpc-client-kit {version('grpc-client-kit')}, grpcio {version('grpcio')}",
        flush=True,
    )
    server, reports, target = await serve()
    loop = asyncio.get_running_loop()
    previous_handler = loop.get_exception_handler()
    loop_errors = []
    loop.set_exception_handler(lambda _, context: loop_errors.append(context))
    try:
        async with asyncio.timeout(45):
            await registration(target)
            rows, record = await download(target)
            assert rows == ITEMS and record["outcome"] == "OK"
            for observer_type in (SetupTimer, IterationTimer, Observability):
                for request in (b"ok", b"fail"):
                    await measure(target, observer_type(), request)
            print(
                "PASS measurements: observers really ran; rows, late errors and trailing metadata verified",
                flush=True,
            )
            await cancel_early(target, reports)
            await break_is_not_cancel(target, reports)
            await rpc_is_not_consumer_time(target)
            await write_style(target)
    finally:
        await server.stop(None)
        await asyncio.sleep(0)
        loop.set_exception_handler(previous_handler)
    assert not loop_errors, loop_errors
    print("PASS: all stream scenarios; no unhandled event-loop errors", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
