"""One application use case, two real transports, one servicewright lifecycle."""
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-09-07-production-grpc-server"))
from grpc_flow import SERVICE, register_invoice_service
from invoice_domain import get_invoice


@dataclass(frozen=True)
class Settings:
    logging: object | None = None
    metrics: object | None = None
    tracing: object | None = None
    error_tracking: object | None = None

    def get_app_version(self):
        return "1.0.0"


class Scope:
    async def get(self, key):
        raise KeyError(key)


class Container:
    def __init__(self, store):
        self.store = store

    @asynccontextmanager
    async def app_scope(self):
        try:
            yield Scope()
        finally:
            await self.store.close()

    @asynccontextmanager
    async def unit_scope(self, context=None):
        yield Scope()


# snippet:entrypoints
from fastapi import APIRouter
from servicewright import AppSpec, Service
from servicewright.adapters.fastapi import FastApiEntrypoint, HttpConfig
from servicewright.adapters.grpc import GrpcConfig, GrpcEntrypoint


def build_service(store):
    router = APIRouter()

    @router.get("/orders/{order_id}/invoice")
    async def invoice(order_id: str):
        return await get_invoice(store, order_id, buyer_id="buyer-7")

    http = FastApiEntrypoint(
        config=HttpConfig(host="127.0.0.1", port=0), routers=(router,),
    )
    grpc_entry = GrpcEntrypoint(
        config=GrpcConfig(host="127.0.0.1", port=0, grace_period=1),
        servicers=lambda server, ctx: register_invoice_service(server, store),
    )
    spec = AppSpec(
        service_name="invoices", create_container=lambda settings: Container(store),
    )
    return Service(spec, entrypoints=[http, grpc_entry]), http, grpc_entry
# /snippet:entrypoints
