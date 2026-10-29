"""Observe channel identity via public get_channel() and actual RPC behavior."""
import asyncio
import logging
from pathlib import Path
import sys
import grpc

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '2026-09-07-safe-grpc-retries'))
from grpc_client_kit import ChannelPool, TimeoutConfig, build_interceptors
from grpc_flow import OPTIONS, grpc_clients, inventory_chain
from grpc_origin import grpc_origin
from retries_lab import expect_unavailable


async def main():
    async with grpc_origin() as (inventory, target):
        async with grpc_clients(target) as (orders, audit):
            async with orders as stub:
                await expect_unavailable(stub.get_stock(b'down'))
            assert inventory.attempts[('stock', b'down')] == 3
            async with audit as stub:
                await expect_unavailable(stub.get_stock(b'down'))
            assert inventory.attempts[('stock', b'down')] == 4
            assert orders.interceptors_for(target)[0] is orders.interceptors_for(target)[0]
            print('PASS same target: orders makes three attempts, audit makes one')

        async with ChannelPool() as pool:
            chain = inventory_chain()
            plain = build_interceptors(timeout=TimeoutConfig(default=1))
            first = await pool.get_channel(target, insecure=True, options=OPTIONS, interceptors=chain)
            again = await pool.get_channel(target, insecure=True, options=OPTIONS, interceptors=chain)
            audit = await pool.get_channel(target, insecure=True, options=OPTIONS, interceptors=plain)
            changed = await pool.get_channel(target, insecure=True, options=OPTIONS + [('grpc.keepalive_time_ms', 30000)], interceptors=chain)
            assert first is again and first is not audit and first is not changed
            new_chain = await pool.get_channel(target, insecure=True, options=OPTIONS, interceptors=inventory_chain())
            assert first is not new_chain
            await asyncio.wait_for(first.channel_ready(), timeout=3)
            print('PASS public channel identity: reuse stable chain; separate chains and options')
        for channel in (first, audit, changed, new_chain):
            assert channel.get_state() == grpc.ChannelConnectivity.SHUTDOWN
        print('PASS pool owns shutdown: all acquired channels are closed')


if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    asyncio.run(main())
