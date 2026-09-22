"""Behavior checks on real HTTP; no private client state and no benchmark claims."""
import asyncio
from dataclasses import replace
import logging
import time

import aiohttp
import httpx
import requests
from clientwright import (
    AdapterDeps, CircuitBreakerConfig, CircuitOpenError, ClientConfig,
    DeadlineExceededError, RetryConfig, TimeoutConfig, UnsupportedCapabilityError,
    build, build_sync, inspect,
)
from clientwright.core.testing import ManualClock, RecordingMetrics
from clientwright.adapters.httpx import IDEMPOTENT_EXTENSION
from client_flow import RETRIES, charge, fetch_stock, observe_stock, outbound_clients, shared_http_client, http_client
from http_origin import HttpOrigin


def config(*, retry=RETRIES, breaker=None, total=3, read=1):
    return ClientConfig(
        service_name='orders', timeout=TimeoutConfig(total=total, read=read),
        retry=retry, circuit_breaker=breaker,
    )


async def wrappers():
    async with HttpOrigin(stock_failures=2) as origin:
        available, calls, attempts = await observe_stock(origin.url)
        assert (available, calls, attempts) == (7, 1, 3)
        assert origin.calls['/stock/sku-42'] == 3
        async with outbound_clients(origin.url, origin.url) as (client, payments):
            assert type(client) is httpx.AsyncClient
            assert await fetch_stock(client, 'sku-7') == 7
            assert await fetch_stock(client, 'sku-7') == 7
        assert client.is_closed and payments.is_closed
        print('PASS HTTPX: native client, repeated use, one call / three attempts, closed')

        async with build('aiohttp', config()) as client:
            assert type(client) is aiohttp.ClientSession
            async with client.get(origin.url + '/stock/sku-aiohttp') as response:
                assert response.status == 200
                assert (await response.json())['available'] == 7
        with build_sync('requests', config()) as client:
            assert type(client) is requests.Session
            response = await asyncio.to_thread(client.get, origin.url + '/stock/sku-requests')
            assert response.status_code == 200
        print('PASS aiohttp / requests: native interfaces and successful retries')

        wants_attempt = replace(config(), timeout=TimeoutConfig(total=2, attempt=0.5))
        with build_sync('requests', wants_attempt) as client:
            report = inspect(client).report
            assert report.dropped, report
        try:
            build_sync('requests', replace(wants_attempt, on_unsupported='strict'))
        except UnsupportedCapabilityError:
            pass
        else:
            raise AssertionError('unsupported attempt timeout silently accepted')
        print('PASS unsupported setting: visible report or strict build failure')

        async with build('httpx', config(retry=replace(RETRIES, budget_ratio=None))) as client:
            for _ in range(3):  # An intentionally duplicated application retry layer.
                response = await client.get(origin.url + '/down')
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError:
                    continue
                break
        assert origin.calls['/down'] == 9
        print('PASS nested retries: three outer calls become nine server requests')


async def deadlines():
    async with HttpOrigin() as origin:
        async with httpx.AsyncClient(timeout=httpx.Timeout(0.3), trust_env=False) as client:
            response = await client.get(origin.url + '/drip')
            assert response.content == b'x' * 10
        metrics = RecordingMetrics()
        async with build('httpx', config(total=0.35, read=0.3), AdapterDeps(metrics=metrics)) as client:
            started = time.monotonic()
            try:
                await client.get(origin.url + '/drip')
            except DeadlineExceededError:
                pass
            else:
                raise AssertionError('body consumption escaped the total deadline')
            assert time.monotonic() - started < 1.5
        assert len(metrics.attempts) == 1
        print('PASS total deadline: regularly arriving body chunks do not extend the whole call')

        metrics = RecordingMetrics()
        async with build('httpx', config(total=0.35, read=0.1), AdapterDeps(metrics=metrics)) as client:
            try:
                await client.get(origin.url + '/slow')
            except httpx.TimeoutException:
                pass
            else:
                raise AssertionError('slow endpoint ignored the deadline')
        assert 1 <= len(metrics.attempts) <= 3
        assert len(metrics.calls) == 1
        print('PASS retries share the total budget; the final error can still be a read timeout')


async def backoff():
    async with HttpOrigin() as origin:
        async with build('httpx', config()) as client:
            assert (await client.get(origin.url + '/retry-after')).status_code == 200
        times = [at for path, at in origin.arrivals if path == '/retry-after']
        assert len(times) == 2 and times[1] - times[0] >= 0.95
        metrics = RecordingMetrics()
        async with build('httpx', config(total=0.3), AdapterDeps(metrics=metrics)) as client:
            response = await client.get(origin.url + '/retry-later')
        assert response.status_code == 503 and origin.calls['/retry-later'] == 1
        assert any(item['reason'] == 'deadline' for item in metrics.retry_skips)
        print('PASS Retry-After: delay respected; retry skipped when it cannot fit the budget')

    async with HttpOrigin() as origin:
        async with http_client(origin.url) as client:
            response = await client.post('/payments', json={'order_id': 'order-42'})
            assert response.status_code == 503
        assert origin.calls['/payments'] == 1 and origin.charges == 1
    async with HttpOrigin() as origin:
        async with http_client(origin.url) as client:
            assert await charge(client, 'order-42', 1500) == 'payment-1'
            assert origin.calls['/payments'] == 2 and origin.charges == 1
            assert await charge(client, 'order-42', 1500) == 'payment-1'
        assert origin.calls['/payments'] == 3 and origin.charges == 1
        print('PASS payment: a plain POST is not retried; a stable server-backed key deduplicates')
    async with HttpOrigin() as origin:
        async with http_client(origin.url) as client:
            response = await client.post('/payments', json={}, extensions={IDEMPOTENT_EXTENSION: True})
            assert response.status_code == 200
        assert origin.charges == 2
        print('PASS counterexample: idempotent=True alone repeats the payment effect')

    async with HttpOrigin() as origin:
        async with build('httpx', config(retry=replace(RETRIES, budget_ratio=None))) as client:
            async def chunks():
                yield b'one-shot body'
            response = await client.post(origin.url + '/down', content=chunks(), extensions={IDEMPOTENT_EXTENSION: True})
            assert response.status_code == 503
            assert (await client.get(origin.url + '/bad-input')).status_code == 400
        assert origin.calls['/down'] == 3 and origin.calls['/bad-input'] == 1
        assert [body for path, body in origin.bodies if path == '/down'] == [b'one-shot body'] * 3
        print('PASS body replay: HTTPX adapter buffers the finite iterator; 400 is not retried')


async def retry_budget():
    for ratio in (None, 0.1):
        async with HttpOrigin() as origin:
            metrics = RecordingMetrics()
            retry = replace(RETRIES, budget_ratio=ratio, initial_backoff=0.01, jitter=0)
            async with build('httpx', config(retry=retry), AdapterDeps(metrics=metrics)) as client:
                # Sequential calls make token refill deterministic, independently of scheduling.
                for _ in range(50):
                    assert (await client.get(origin.url + '/down')).status_code == 503
            seen = origin.calls['/down']
            assert len(metrics.calls) == 50 and len(metrics.attempts) == seen
            if ratio is None:
                assert seen == 150
            else:
                assert 60 <= seen <= 64, seen
                assert any(item['reason'] == 'budget' for item in metrics.retry_skips)
            print(f'PASS retry budget={ratio}: 50 calls, {seen} attempts')


async def breakers():
    async with HttpOrigin() as inventory, HttpOrigin() as payments:
        async with shared_http_client() as client:
            for _ in range(3):
                assert (await client.get(payments.url + '/down')).status_code == 503
            before = payments.calls['/down']
            try:
                await client.get(payments.url + '/down')
            except CircuitOpenError:
                pass
            else:
                raise AssertionError('breaker did not open')
            assert payments.calls['/down'] == before == 9
            assert (await client.get(inventory.url + '/stock/sku-42')).status_code == 200
        print('PASS per origin: failed payments block after three calls / nine attempts; stock still works')

    clock = ManualClock()
    metrics = RecordingMetrics()
    async with HttpOrigin() as origin:
        cfg = config(retry=None, breaker=CircuitBreakerConfig(fail_threshold=2, recovery_timeout=10))
        async with build('httpx', cfg, AdapterDeps(clock=clock, metrics=metrics)) as client:
            for _ in range(3):
                assert (await client.get(origin.url + '/bad-input')).status_code == 400
            for _ in range(2):
                assert (await client.get(origin.url + '/down')).status_code == 503
            try:
                await client.get(origin.url + '/stock/sku-42')
            except CircuitOpenError:
                pass
            else:
                raise AssertionError('open origin accepted traffic')
            clock.advance(11)
            assert (await client.get(origin.url + '/stock/sku-42')).status_code == 200
            assert (await client.get(origin.url + '/stock/sku-42')).status_code == 200
        assert [item['state'] for item in metrics.circuit_states] == ['open', 'half_open', 'closed']
        print('PASS recovery: 400 does not trip; one successful probe closes the circuit (manual clock)')


def run(check):
    logging.basicConfig(level=logging.CRITICAL)
    asyncio.run(check())
