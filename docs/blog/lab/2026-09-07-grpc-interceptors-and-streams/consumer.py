"""Caller-owned context and explicit cancellation on early exit."""

import asyncio

import grpc
from grpc_client_kit import flatten_interceptors

from observers import REQUEST_ID, Observability
from report_service import STREAM


async def download(target):
    observer = Observability()
    async with grpc.aio.insecure_channel(
        target, interceptors=flatten_interceptors([observer])
    ) as channel:
        call = channel.unary_stream(STREAM)(b"ok", timeout=5)
        rows = [row async for row in call]
        record = await asyncio.wait_for(observer.finished.get(), timeout=5)
        assert await call.code() == grpc.StatusCode.OK
        assert dict(await call.trailing_metadata()) == {"report-id": "r-42"}
        return rows, record


async def first_row(channel, request=b"hold"):
    token = REQUEST_ID.set("req-42")
    call = None
    try:
        call = channel.unary_stream(STREAM)(request, timeout=5)
        async for row in call:
            assert REQUEST_ID.get() == "req-42"
            return row
    finally:
        if call is not None:
            call.cancel()
        REQUEST_ID.reset(token)
