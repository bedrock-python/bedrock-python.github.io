"""An instrumented in-memory stand-in for a database, not a database driver."""
import asyncio
from contextlib import asynccontextmanager


class ReportStore:
    def __init__(self, *, duration=0.1, fail_warmup=False):
        self.duration = duration
        self.fail_warmup = fail_warmup
        self.opened = False
        self.active = 0
        self.events = []
        self.started = asyncio.Event()
        self.warming = asyncio.Event()
        self.allow_warmup = asyncio.Event()
        self.allow_warmup.set()

    async def ping(self):
        assert self.opened
        self.warming.set()
        await self.allow_warmup.wait()
        if self.fail_warmup:
            raise ConnectionError('report store unavailable')
        self.events.append('warmup:done')

    async def report(self, source):
        assert self.opened
        self.active += 1
        self.events.append(f'{source}:started')
        self.started.set()
        try:
            await asyncio.sleep(self.duration)
            assert self.opened, 'resource closed before report finished'
            self.events.append(f'{source}:done')
            return {'rows': 42}
        except asyncio.CancelledError:
            self.events.append(f'{source}:cancelled')
            raise
        finally:
            self.active -= 1


@asynccontextmanager
async def open_store(store):
    assert not store.opened
    store.opened = True
    store.events.append('store:open')
    try:
        yield store
    finally:
        assert store.active == 0, 'resource closed while reports still run'
        store.opened = False
        store.events.append('store:close')
