"""Local fault-injecting HTTP services. Payment deduplication is in-memory and sequential only."""
import asyncio
from collections import Counter
import time

from aiohttp import web


class HttpOrigin:
    def __init__(self, *, stock_failures=0):
        self.stock_failures = stock_failures
        self.calls = Counter()
        self.arrivals = []
        self.bodies = []
        self.charges = 0
        self.payments = {}
        self.runner = None

    async def handle(self, request):
        body = await request.read()
        path = request.path
        self.calls[path] += 1
        self.arrivals.append((path, time.monotonic()))
        self.bodies.append((path, body))
        attempt = self.calls[path]
        if path.startswith('/stock/'):
            if attempt <= self.stock_failures:
                return web.json_response({'error': 'restarting'}, status=503)
            return web.json_response({'sku': path.rsplit('/', 1)[1], 'available': 7})
        if path == '/down':
            return web.Response(status=503)
        if path == '/bad-input':
            return web.Response(status=400)
        if path == '/retry-after' and attempt == 1:
            return web.Response(status=503, headers={'Retry-After': '1'})
        if path == '/retry-later':
            return web.Response(status=503, headers={'Retry-After': '60'})
        if path == '/slow':
            await asyncio.sleep(0.6)
        if path == '/drip':
            response = web.StreamResponse(headers={'Content-Length': '10'})
            await response.prepare(request)
            try:
                for _ in range(10):
                    await asyncio.sleep(0.08)
                    await response.write(b'x')
                await response.write_eof()
            except ConnectionResetError:
                pass  # The total deadline can close this response before the last byte.
            return response
        if path == '/payments':
            key = request.headers.get('Idempotency-Key')
            if key and key in self.payments:
                saved_body, result = self.payments[key]
                if saved_body != body:
                    return web.Response(status=409)
                return web.json_response(result)
            self.charges += 1
            result = {'payment_id': f'payment-{self.charges}'}
            if key:
                self.payments[key] = (body, result)
            # The first response fails AFTER the effect, with or without a key.
            if attempt == 1:
                return web.Response(status=503)
            return web.json_response(result)
        return web.json_response({'ok': True})

    async def __aenter__(self):
        app = web.Application()
        app.router.add_route('*', '/{tail:.*}', self.handle)
        self.runner = web.AppRunner(app, handle_signals=False, shutdown_timeout=2)
        await self.runner.setup()
        try:
            await web.TCPSite(self.runner, '127.0.0.1', 0, backlog=128).start()
        except BaseException:
            await self.runner.cleanup()
            raise
        self.url = f'http://127.0.0.1:{self.runner.addresses[0][1]}'
        return self

    async def __aexit__(self, *exc):
        await self.runner.cleanup()
