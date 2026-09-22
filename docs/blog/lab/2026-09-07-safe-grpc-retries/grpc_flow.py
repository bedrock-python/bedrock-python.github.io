"""A read-only retry allowlist and application-scoped gRPC channels."""
SERVICE = 'shop.Inventory'
GET_STOCK = f'/{SERVICE}/GetStock'
RESERVE = f'/{SERVICE}/Reserve'
EXPORT = f'/{SERVICE}/Export'
OPTIONS = [('grpc.enable_retries', 0)]


class InventoryStub:
    """Raw-byte stub for the lab; production services normally generate this from protobuf."""
    def __init__(self, channel):
        self.get_stock = channel.unary_unary(GET_STOCK)
        self.reserve = channel.unary_unary(RESERVE)
        self.export = channel.unary_stream(EXPORT)


# snippet:grpc_policy
import grpc
from grpc_client_kit import (
    RetryConfig as GrpcRetry,
    TimeoutConfig as GrpcTimeout,
    build_interceptors,
)


def inventory_chain():
    return build_interceptors(
        timeout=GrpcTimeout(default=1),
        retry=GrpcRetry(
            max_attempts=3,
            initial_backoff=0.05,
            retryable_codes={grpc.StatusCode.UNAVAILABLE},
            idempotent_methods={'/shop.Inventory/GetStock'},
            retry_streaming=False,
        ),
    )
# /snippet:grpc_policy


# snippet:grpc_clients
from contextlib import asynccontextmanager
from grpc_client_kit import ChannelPool, GrpcClient, GrpcClientConfig


@asynccontextmanager
async def grpc_clients(target):
    config = GrpcClientConfig(
        target=target,
        insecure=True,  # Local lab; configure credentials for a TLS deployment.
        options=[('grpc.enable_retries', 0)],
    )
    async with ChannelPool() as pool:
        orders = GrpcClient(
            InventoryStub, config, pool,
            interceptor_factory=lambda target: inventory_chain(),
        )
        audit = GrpcClient(
            InventoryStub, config, pool,
            interceptor_factory=lambda target: build_interceptors(
                timeout=GrpcTimeout(default=1), retry=None,
            ),
        )
        yield orders, audit
# /snippet:grpc_clients
