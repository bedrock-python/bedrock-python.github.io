"""One use case, five domain errors, two transports in one process.

The use case raises `ServiceError` subclasses and knows nothing about HTTP or gRPC. The HTTP
entrypoint renders them as RFC 9457 problem documents; the gRPC entrypoint maps them to status
codes. Neither handler catches anything.
"""

from __future__ import annotations

import contextlib
import sys
from dataclasses import dataclass
from typing import Any

import grpc
from fastapi import APIRouter
from servicewright import AppSpec, ErrorKind, Service, ServiceError, run_sync
from servicewright.adapters.fastapi import FastApiEntrypoint, HttpConfig
from servicewright.adapters.grpc import GrpcConfig, GrpcEntrypoint

HTTP_PORT = int(sys.argv[1])
GRPC_PORT = int(sys.argv[2])
SERVICE = "lab.Orders"


# --- the domain: errors that name what happened, not what the transport should answer ---------


class OrderNotFoundError(ServiceError):
    kind = ErrorKind.NOT_FOUND


class OrderAlreadyPaidError(ServiceError):
    kind = ErrorKind.CONFLICT


class NotYourOrderError(ServiceError):
    kind = ErrorKind.FORBIDDEN


class PaymentProviderDownError(ServiceError):
    kind = ErrorKind.UNAVAILABLE


class LedgerCorruptedError(ServiceError):
    """Real, and none of the caller's business: public=False masks it at every transport."""

    kind = ErrorKind.INTERNAL
    public = False


async def pay_order(case: str) -> dict[str, str]:
    """The use case. It raises; it never formats a response."""
    if case == "missing":
        raise OrderNotFoundError("no order with id 42", params={"order_id": "42"})
    if case == "paid":
        raise OrderAlreadyPaidError("order 42 was paid at 09:12")
    if case == "forbidden":
        raise NotYourOrderError("order 42 belongs to another customer")
    if case == "provider":
        raise PaymentProviderDownError("the payment provider did not answer in 2 s")
    if case == "ledger":
        raise LedgerCorruptedError("ledger row 8891 has a negative balance; dsn=postgres://user:pw@db/ledger")
    if case == "unexpected":
        raise RuntimeError("dividing by the number of retries, which is zero")
    return {"status": "paid"}


# --- the HTTP front ---------------------------------------------------------------------------

router = APIRouter()


@router.post("/orders/{case}/pay")
async def pay(case: str) -> dict[str, str]:
    return await pay_order(case)


# --- the gRPC front ---------------------------------------------------------------------------


class OrdersServicer:
    async def Pay(self, request: bytes, context: grpc.aio.ServicerContext) -> bytes:  # noqa: N802
        result = await pay_order(request.decode())
        return result["status"].encode()


def register_servicer(server: Any, ctx: Any = None) -> None:
    server.add_generic_rpc_handlers(
        (
            grpc.method_handlers_generic_handler(
                SERVICE, {"Pay": grpc.unary_unary_rpc_method_handler(OrdersServicer().Pay)}
            ),
        )
    )


# --- the service ------------------------------------------------------------------------------


@dataclass(frozen=True)
class Settings:
    logging: object | None = None
    metrics: object | None = None
    tracing: object | None = None
    error_tracking: object | None = None

    def get_app_version(self) -> str:
        return "1.0.0"


class Scope:
    async def get(self, dependency_key: Any) -> Any:
        raise KeyError(dependency_key)


class Container:
    @contextlib.asynccontextmanager
    async def app_scope(self):
        yield Scope()

    @contextlib.asynccontextmanager
    async def unit_scope(self, context=None):
        yield Scope()


spec = AppSpec(service_name="errors-lab", create_container=lambda settings: Container())
service = Service(
    spec,
    entrypoints=[
        FastApiEntrypoint(config=HttpConfig(host="127.0.0.1", port=HTTP_PORT), routers=(router,)),
        GrpcEntrypoint(
            config=GrpcConfig(host="127.0.0.1", port=GRPC_PORT),
            servicers=register_servicer,
        ),
    ],
)

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.WARNING)
    run_sync(service, Settings())
