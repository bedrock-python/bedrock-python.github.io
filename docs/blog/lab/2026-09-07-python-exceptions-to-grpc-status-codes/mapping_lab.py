"""What a gRPC caller is told for each kind of Python exception, and what it costs to get it wrong.

One server, three configurations: no exception handling, the kit's default map, and a map with the
service's own domain errors added. Ten exceptions go through each, and the lab prints the status
code and the details string the client received — the two things a caller can act on.
"""

from __future__ import annotations

import asyncio
from importlib.metadata import version

import grpc
import grpc.aio

from grpc_server_kit import GrpcApp, GrpcServerConfig
from grpc_server_kit.aio.interceptors import (
    GRPC_DEFAULT_ERROR_STATUS_MAP,
    AsyncExceptionHandlerInterceptor,
)

SERVICE = "lab.Orders"
METHOD = f"/{SERVICE}/Do"
DSN = "postgresql://orders:hunter2@db.internal:5432/orders"


class OrderNotFound(Exception):
    """A domain error: the caller asked for something that is not there."""


class OrderAlreadyPaid(Exception):
    """A domain error: the state does not allow this."""


class RateLimited(Exception):
    """A domain error: come back later."""


CASES: dict[str, Exception] = {
    "ValueError": ValueError("amount must be positive"),
    "PermissionError": PermissionError("token lacks scope orders:write"),
    "FileNotFoundError": FileNotFoundError("no such invoice"),
    "TimeoutError": TimeoutError("the ledger did not answer in 2 s"),
    "NotImplementedError": NotImplementedError("refunds are not supported yet"),
    "KeyError": KeyError("order_id"),
    "ConnectionError": ConnectionError(f"could not connect to {DSN}"),
    "RuntimeError": RuntimeError(f"ledger write failed against {DSN}"),
    "OrderNotFound": OrderNotFound("order 42"),
    "OrderAlreadyPaid": OrderAlreadyPaid("order 42 was paid at 09:12"),
    "RateLimited": RateLimited("100 requests per minute"),
}


def log(msg: str) -> None:
    print(msg, flush=True)


async def handler(request: bytes, context: grpc.aio.ServicerContext) -> bytes:
    case = request.decode()
    if case in CASES:
        raise CASES[case]
    return b"ok"


def register(server) -> None:
    server.add_generic_rpc_handlers(
        (
            grpc.method_handlers_generic_handler(
                SERVICE, {"Do": grpc.unary_unary_rpc_method_handler(handler)}
            ),
        )
    )


async def call(target: str, case: str) -> tuple[str, str]:
    async with grpc.aio.insecure_channel(target) as channel:
        try:
            await channel.unary_unary(METHOD)(case.encode(), timeout=5)
            return "OK", ""
        except grpc.aio.AioRpcError as error:
            return error.code().name, (error.details() or "")


async def run(label: str, interceptors: list) -> None:
    log(f"--- {label}")
    app = GrpcApp(GrpcServerConfig(host="127.0.0.1", port=0), interceptors=list(interceptors))
    app.register(register)
    async with app:
        target = f"127.0.0.1:{app.bound_port}"
        for case in CASES:
            code, details = await call(target, case)
            leak = "  <- leaks the password" if "hunter2" in details else ""
            log(f"    {case:<20} {code:<20} {details[:72]!r}{leak}")


async def main() -> None:
    log(f"grpc-server-kit {version('grpc-server-kit')}, grpcio {version('grpcio')}")
    log(f"the kit's default map: "
        f"{ {exc.__name__: code.name for exc, code in GRPC_DEFAULT_ERROR_STATUS_MAP.items()} }")
    log("")

    await run("no exception handling at all", [])
    log("")
    await run("the default map", [AsyncExceptionHandlerInterceptor()])
    log("")
    await run(
        "the default map plus this service's domain errors",
        [
            AsyncExceptionHandlerInterceptor(
                error_status_map={
                    OrderNotFound: grpc.StatusCode.NOT_FOUND,
                    OrderAlreadyPaid: grpc.StatusCode.FAILED_PRECONDITION,
                    RateLimited: grpc.StatusCode.RESOURCE_EXHAUSTED,
                    ConnectionError: grpc.StatusCode.UNAVAILABLE,
                }
            )
        ],
    )
    log("")
    log("--- the same, with details the caller can act on for the domain errors only")

    def detail_factory(exc: Exception, status: grpc.StatusCode) -> str:
        if isinstance(exc, OrderNotFound | OrderAlreadyPaid | RateLimited):
            return f"{type(exc).__name__}: {exc}"
        return "Request processing failed"

    await run(
        "a detail factory that trusts domain errors only",
        [
            AsyncExceptionHandlerInterceptor(
                error_status_map={
                    OrderNotFound: grpc.StatusCode.NOT_FOUND,
                    OrderAlreadyPaid: grpc.StatusCode.FAILED_PRECONDITION,
                    RateLimited: grpc.StatusCode.RESOURCE_EXHAUSTED,
                    ConnectionError: grpc.StatusCode.UNAVAILABLE,
                },
                detail_factory=detail_factory,
            )
        ],
    )


if __name__ == "__main__":
    asyncio.run(main())
