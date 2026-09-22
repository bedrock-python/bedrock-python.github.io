"""The article's gRPC assembly. Raw bytes keep the lab independent of generated stubs."""
import json

from invoice_domain import (
    InvoiceAccessDenied, InvoiceNotReady, InvoiceStoreUnavailable,
    OrderNotFound, get_invoice,
)

# snippet:exception_handler
import grpc
from grpc_server_kit.aio.interceptors import AsyncExceptionHandlerInterceptor


SERVICE = "orders.Invoices"

ERROR_STATUS = {
    OrderNotFound: grpc.StatusCode.NOT_FOUND,
    InvoiceNotReady: grpc.StatusCode.FAILED_PRECONDITION,
    InvoiceAccessDenied: grpc.StatusCode.PERMISSION_DENIED,
    InvoiceStoreUnavailable: grpc.StatusCode.UNAVAILABLE,
}


def public_details(error, status):
    if isinstance(error, tuple(ERROR_STATUS)) and error.public:
        return error.code
    return "internal_error"


def exception_handler():
    return AsyncExceptionHandlerInterceptor(
        error_status_map=ERROR_STATUS,
        detail_factory=public_details,
        merge_defaults=False,
    )
# /snippet:exception_handler


METHOD = f"/{SERVICE}/GetInvoice"


def register_invoice_service(server, store, buyer_id="buyer-7"):
    # buyer_id is a trusted lab identity. Real handlers obtain it from verified auth context.
    async def get(request, context):
        result = await get_invoice(store, request.decode(), buyer_id)
        return json.dumps(result).encode()

    server.add_generic_rpc_handlers((grpc.method_handlers_generic_handler(
        SERVICE, {"GetInvoice": grpc.unary_unary_rpc_method_handler(get)},
    ),))


# snippet:config
from grpc_server_kit import GrpcApp, GrpcServerConfig


def server_config():
    return GrpcServerConfig(
        host="127.0.0.1", port=0,
        max_receive_message_length=64 * 1024,
        max_send_message_length=64 * 1024,
        max_concurrent_rpcs=32,
        grace_period=1.0,
    )
# /snippet:config

# snippet:assembly
from grpc_server_kit.aio.interceptors import (
    AsyncMetricsInterceptor, AsyncSentryInterceptor,
)
from grpc_server_kit.aio.interceptors.exception_handler import find_mapped_status


def build_app(store, metrics, reporter, *, config=None):
    app = GrpcApp(config or server_config(), interceptors=[
        AsyncMetricsInterceptor(metrics, service_name=SERVICE),
        exception_handler(),
        AsyncSentryInterceptor(reporter, capture_filter=lambda error:
            find_mapped_status(type(error), ERROR_STATUS) in {
                grpc.StatusCode.INTERNAL, grpc.StatusCode.UNAVAILABLE,
            }),
    ])
    app.register(lambda server: register_invoice_service(server, store))
    return app
# /snippet:assembly

# snippet:health
class InvoiceStoreHealth:
    name = "invoice-store"

    def __init__(self, store):
        self.store = store

    async def check(self) -> bool:
        return await self.store.ping()


def enable_readiness(app, store):
    app.enable_health(
        checkers=[InvoiceStoreHealth(store)],
        service_names=[SERVICE],
        cache_ttl=0,
        check_timeout=0.2,
    )
# /snippet:health

# snippet:lifecycle
async def serve_invoices(app, store, stop):
    try:
        async with app:
            await stop.wait()
    finally:
        await store.close()
# /snippet:lifecycle

# snippet:tls
from dataclasses import replace


def tls_config(cert_file, key_file, ca_file=None):
    return replace(
        server_config(),
        ssl_enabled=True,
        ssl_cert_file=str(cert_file),
        ssl_key_file=str(key_file),
        ssl_ca_file=str(ca_file) if ca_file else None,
        ssl_client_auth=ca_file is not None,
    )
# /snippet:tls
