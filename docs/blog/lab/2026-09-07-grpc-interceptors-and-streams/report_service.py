"""A real local gRPC service; bytes keep protobuf generation out of this experiment."""

import asyncio

import grpc
import grpc.aio

SERVICE = "lab.Reports"
GET, STREAM, UPLOAD, CHAT = (
    f"/{SERVICE}/{name}" for name in ("Get", "Stream", "Upload", "Chat")
)
KINDS = ("unary_unary", "unary_stream", "stream_unary", "stream_stream")
GAP = 0.03
ITEMS = [bytes([number]) for number in range(1, 6)]


async def report_rows(request, context):
    for number, row in enumerate(ITEMS, start=1):
        if request == b"fail" and number == 3:
            await context.abort(
                grpc.StatusCode.UNAVAILABLE, "report generator failed at row 3"
            )
        if request != b"fast":
            await asyncio.sleep(GAP)
        yield row


class Reports:
    def __init__(self):
        self.holding = asyncio.Event()
        self.hold_closed = asyncio.Event()

    async def get(self, request, context):
        await asyncio.sleep(GAP)
        return b"ready"

    async def stream(self, request, context):
        context.set_trailing_metadata((("report-id", "r-42"),))
        if request == b"hold":
            try:
                yield ITEMS[0]
                self.holding.set()
                await asyncio.Event().wait()
            finally:
                self.hold_closed.set()
            return
        async for row in report_rows(request, context):
            yield row

    async def upload(self, request_iterator, context):
        rows = [row async for row in request_iterator]
        return bytes([len(rows)])

    async def chat(self, request_iterator, context):
        async for row in request_iterator:
            await asyncio.sleep(GAP)
            yield row


async def serve():
    reports = Reports()
    server = grpc.aio.server()
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
    assert port > 0
    await server.start()
    return server, reports, f"127.0.0.1:{port}"


async def requests():
    for row in ITEMS[:3]:
        yield row


async def invoke(channel, kind):
    if kind == "unary_unary":
        call = channel.unary_unary(GET)(b"", timeout=5)
        assert await call == b"ready"
    elif kind == "unary_stream":
        call = channel.unary_stream(STREAM)(b"ok", timeout=5)
        assert [row async for row in call] == ITEMS
    elif kind == "stream_unary":
        call = channel.stream_unary(UPLOAD)(requests(), timeout=5)
        assert await call == b"\x03"
    else:
        call = channel.stream_stream(CHAT)(requests(), timeout=5)
        assert [row async for row in call] == ITEMS[:3]
    assert await call.code() == grpc.StatusCode.OK
    return call
