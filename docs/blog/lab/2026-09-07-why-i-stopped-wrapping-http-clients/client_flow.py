"""The article's HTTP snippets, exercised against local services by the labs."""
# snippet:http_client
from clientwright import (
    AdapterDeps, ClientConfig, RetryConfig, TimeoutConfig, build,
)


def http_client(base_url, *, metrics=None):
    return build(
        'httpx',
        ClientConfig(
            service_name='orders',
            base_url=base_url,
            timeout=TimeoutConfig(total=2, connect=0.3, read=0.5),
            retry=RetryConfig(max_attempts=3, budget_ratio=0.1),
            circuit_breaker=None,
            on_unsupported='strict',
        ),
        AdapterDeps(metrics=metrics),
    )
# /snippet:http_client


# snippet:lifetime
from contextlib import asynccontextmanager


@asynccontextmanager
async def outbound_clients(inventory_url, payments_url):
    async with http_client(inventory_url) as inventory:
        async with http_client(payments_url) as payments:
            yield inventory, payments
# /snippet:lifetime


# snippet:fetch
async def fetch_stock(client, sku):
    response = await client.get(f'/stock/{sku}')
    response.raise_for_status()
    return response.json()['available']
# /snippet:fetch


# snippet:payment
from clientwright.adapters.httpx import IDEMPOTENT_EXTENSION


async def charge(client, order_id, amount_minor):
    response = await client.post(
        '/payments',
        json={'order_id': order_id, 'amount_minor': amount_minor},
        headers={'Idempotency-Key': f'charge:{order_id}'},
        extensions={IDEMPOTENT_EXTENSION: True},
    )
    response.raise_for_status()
    return response.json()['payment_id']
# /snippet:payment


# snippet:backoff
RETRIES = RetryConfig(
    max_attempts=3,
    initial_backoff=0.1,
    max_backoff=1,
    multiplier=2,
    jitter=0.2,
    respect_retry_after=True,
    budget_ratio=0.1,
)
# /snippet:backoff


# snippet:breaker
from clientwright import CircuitBreakerConfig


def shared_http_client():
    return build('httpx', ClientConfig(
        service_name='orders',
        timeout=TimeoutConfig(total=2),
        retry=RETRIES,
        circuit_breaker=CircuitBreakerConfig(
            fail_threshold=3,
            recovery_timeout=10,
            half_open_max_calls=1,
        ),
    ))
# /snippet:breaker


# snippet:metrics
from clientwright.core.testing import RecordingMetrics


async def observe_stock(base_url):
    metrics = RecordingMetrics()
    async with http_client(base_url, metrics=metrics) as client:
        available = await fetch_stock(client, 'sku-42')
    return available, len(metrics.calls), len(metrics.attempts)
# /snippet:metrics
