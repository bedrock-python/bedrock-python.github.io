"""Assert retry safety, shared deadlines, breaker accounting and stream restarts."""
import asyncio
import logging
import time

import grpc
from grpc_client_kit import (
    ChannelPool, CircuitBreakerConfig, CircuitBreakerOpenError, GrpcClient, GrpcClientConfig,
    RetryConfig, TimeoutConfig, build_interceptors,
)
from grpc_flow import EXPORT, GET_STOCK, OPTIONS, InventoryStub, grpc_clients
from grpc_origin import grpc_origin


async def expect_unavailable(call):
    try:
        await call
    except grpc.aio.AioRpcError as error:
        assert error.code() == grpc.StatusCode.UNAVAILABLE
    else:
        raise AssertionError('expected UNAVAILABLE')


async def main():
    async with grpc_origin() as (inventory, target):
        async with grpc_clients(target) as (orders, audit):
            async with orders as stub:
                assert await stub.get_stock(b'flaky') == b'7'
                await expect_unavailable(stub.reserve(b'order-42'))
            assert inventory.attempts[('stock', b'flaky')] == 3
            assert inventory.attempts[('reserve', b'order-42')] == inventory.reservations == 1
            print('PASS allowlist: stock retried three times; Reserve fails once after one effect')
            async with audit as stub:
                await expect_unavailable(stub.get_stock(b'down'))
            assert inventory.attempts[('stock', b'down')] == 1
            print('PASS audit: same target, separate chain, no inherited retries')

    async with grpc_origin() as (inventory, target), ChannelPool() as pool:
        unsafe = build_interceptors(retry=RetryConfig(max_attempts=3, initial_backoff=0.01))
        client = GrpcClient(InventoryStub, GrpcClientConfig(target=target, insecure=True, options=OPTIONS), pool, interceptors=unsafe)
        async with client as stub:
            await expect_unavailable(stub.reserve(b'order-42'))
        assert inventory.reservations == 3
        print('PASS counterexample: default UNAVAILABLE retry repeats a write three times')

    async with grpc_origin() as (inventory, target), ChannelPool() as pool:
        chain = build_interceptors(
            timeout=TimeoutConfig(default=0.3),
            retry=RetryConfig(max_attempts=3, initial_backoff=0.02, jitter=0, idempotent_methods={GET_STOCK}),
        )
        client = GrpcClient(InventoryStub, GrpcClientConfig(target=target, insecure=True, options=OPTIONS), pool, interceptors=chain)
        started = time.monotonic()
        async with client as stub:
            try:
                await stub.get_stock(b'slow')
            except grpc.aio.AioRpcError as error:
                assert error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
            else:
                raise AssertionError('deadline did not end the call')
        assert inventory.attempts[('stock', b'slow')] == 2
        assert time.monotonic() - started < 1.5
        print('PASS deadline: the second attempt gets remaining time, not another 300 ms')

    async with grpc_origin() as (inventory, target), ChannelPool() as pool:
        chain = build_interceptors(
            timeout=TimeoutConfig(default=1),
            retry=RetryConfig(max_attempts=3, initial_backoff=0.01, idempotent_methods={GET_STOCK}),
            circuit_breaker=CircuitBreakerConfig(fail_threshold=2),
        )
        client = GrpcClient(InventoryStub, GrpcClientConfig(target=target, insecure=True, options=OPTIONS), pool, interceptors=chain)
        async with client as stub:
            try:
                await stub.get_stock(b'down')
            except CircuitBreakerOpenError:
                pass
            else:
                raise AssertionError('third attempt reached an open circuit')
        assert inventory.attempts[('stock', b'down')] == 2
        print('PASS gRPC breaker: two failed attempts block attempt three within the first call')

    for restart in (False, True):
        async with grpc_origin() as (inventory, target), ChannelPool() as pool:
            chain = build_interceptors(
                timeout=TimeoutConfig(default=1),
                retry=RetryConfig(max_attempts=2, initial_backoff=0.01, retry_streaming=restart, idempotent_methods={EXPORT}),
            )
            client = GrpcClient(InventoryStub, GrpcClientConfig(target=target, insecure=True, options=OPTIONS), pool, interceptors=chain)
            received = []
            status = grpc.StatusCode.OK
            async with client as stub:
                try:
                    async for item in stub.export(b'export-42'):
                        received.append(int(item))
                except grpc.aio.AioRpcError as error:
                    status = error.code()
            assert received == ([1, 2, 1, 2, 3] if restart else [1, 2])
            assert status == (grpc.StatusCode.OK if restart else grpc.StatusCode.UNAVAILABLE)
            assert inventory.attempts[('export', b'export-42')] == (2 if restart else 1)
            print(f'PASS stream restart={restart}: received {received}, final status {status.name}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    asyncio.run(main())
