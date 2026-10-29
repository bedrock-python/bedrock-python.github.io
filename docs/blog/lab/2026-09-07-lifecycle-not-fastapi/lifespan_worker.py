"""The worker duplicates the application's resource and warmup wiring."""
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '2026-09-07-one-lifecycle'))
from report_store import ReportStore, open_store


async def worker(store, stop):
    async with open_store(store):
        await store.ping()
        while not stop.is_set():
            async with asyncio.timeout(1):
                await store.report('worker')
            try:
                await asyncio.wait_for(stop.wait(), timeout=0.5)
            except TimeoutError:
                pass


async def demo():
    stop = asyncio.Event()
    store = ReportStore()
    task = asyncio.create_task(worker(store, stop))
    try:
        await asyncio.wait_for(store.started.wait(), timeout=2)
    finally:
        stop.set()
        await asyncio.wait_for(task, timeout=3)
    print(store.events)


if __name__ == '__main__':
    asyncio.run(demo())
