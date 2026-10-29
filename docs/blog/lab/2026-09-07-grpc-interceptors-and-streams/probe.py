"""Check context isolation and teardown failures against a real gRPC server."""

import asyncio
import logging

import grpc
from grpc_client_kit import flatten_interceptors

from interceptors_lab import next_record
from observers import Observability, RaisingTeardown, REQUEST_ID, TokenScope
from report_service import ITEMS, KINDS, STREAM, invoke, serve


class LogCapture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = asyncio.Queue()

    def emit(self, record):
        self.records.put_nowait(record)


async def context_cases(target):
    for kind in KINDS:
        scope, observer = TokenScope(), Observability()
        token = REQUEST_ID.set("caller-owned")
        try:
            async with grpc.aio.insecure_channel(
                target, interceptors=flatten_interceptors([scope, observer])
            ) as channel:
                await invoke(channel, kind)
                assert (await next_record(observer))["request_id"] == "interceptor-only"
                assert await next_record(scope) == ("interceptor-only", "caller-owned")
                assert REQUEST_ID.get() == "caller-owned"
        finally:
            REQUEST_ID.reset(token)
        assert (
            REQUEST_ID.get() is None
            and scope.finished.empty()
            and observer.finished.empty()
        )
    print(
        "PASS contexts: set/reset in all four kinds; inner observer sees local value; caller stays unchanged",
        flush=True,
    )


async def teardown_cases(target):
    logger = logging.getLogger("grpc_client_kit.interceptors.base")
    capture = LogCapture()
    logger.addHandler(capture)
    previous_propagate = logger.propagate
    logger.propagate = False
    try:
        async with grpc.aio.insecure_channel(
            target, interceptors=flatten_interceptors([RaisingTeardown()])
        ) as channel:
            for kind in KINDS:
                await invoke(channel, kind)
                record = await asyncio.wait_for(capture.records.get(), timeout=5)
                assert "around_call teardown failed" in record.getMessage()
                assert isinstance(record.exc_info[1], RuntimeError)
            seen = []
            try:
                async for row in channel.unary_stream(STREAM)(b"fail", timeout=5):
                    seen.append(row)
            except grpc.aio.AioRpcError as error:
                assert error.code() == grpc.StatusCode.UNAVAILABLE
            else:
                raise AssertionError("The RPC failure was swallowed")
            assert seen == ITEMS[:2]
            record = await asyncio.wait_for(capture.records.get(), timeout=5)
            assert isinstance(record.exc_info[1], RuntimeError)
            assert capture.records.empty()
    finally:
        logger.removeHandler(capture)
        logger.propagate = previous_propagate
    print(
        "PASS teardown failures: four successful RPCs stay successful; UNAVAILABLE stays UNAVAILABLE; five errors logged",
        flush=True,
    )


async def main():
    server, _, target = await serve()
    loop = asyncio.get_running_loop()
    previous_handler = loop.get_exception_handler()
    loop_errors = []
    loop.set_exception_handler(lambda _, context: loop_errors.append(context))
    try:
        async with asyncio.timeout(30):
            await context_cases(target)
            await teardown_cases(target)
    finally:
        await server.stop(None)
        await asyncio.sleep(0)
        loop.set_exception_handler(previous_handler)
    assert not loop_errors, loop_errors
    print(
        "PASS: context and teardown probes; no unhandled event-loop errors", flush=True
    )


if __name__ == "__main__":
    asyncio.run(main())
