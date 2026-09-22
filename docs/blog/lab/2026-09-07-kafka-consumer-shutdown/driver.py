"""Cancel, drain, or exhaust the drain budget; verify where a replacement starts."""

import asyncio
from contextlib import suppress

from aiokafka_foundation_kit import consumer_lifecycle

from consumer_common import Settings, committed_offset, fetch_count, flow, infrastructure, seed
from consumer_naive import consume
from consumer_service import build_service


async def scenario(bootstrap, mode):
    group = f"tracking-{mode}"
    stop, second_effect, block = asyncio.Event(), asyncio.Event(), asyncio.Event()
    processed = []
    view = flow.TrackingView()

    async def process(message):
        await view.process(message)
        processed.append(message.offset)
        if len(processed) == 2:
            second_effect.set()
            if mode != "cancel":
                stop.set()
            if mode != "drain":
                await block.wait()
        await asyncio.sleep(0.01)

    if mode == "cancel":
        work = consume(bootstrap, process, stop, group)
    else:
        work = build_service(
            bootstrap, process, group=group, grace=0.05 if mode == "timeout" else 12,
        ).run(Settings(), stop=stop)
    task = asyncio.create_task(work)
    try:
        async with asyncio.timeout(30):
            await second_effect.wait()
            if mode == "cancel":
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
            elif mode == "timeout":
                try:
                    await task
                except TimeoutError:
                    pass
                else:
                    raise AssertionError("A blocked handler must exhaust the drain budget")
            else:
                await task
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    expected = list(range(5)) if mode == "drain" else [0, 1]
    assert processed == expected, (mode, processed)
    saved = await committed_offset(bootstrap, group)
    assert saved == (5 if mode == "drain" else None), (mode, saved)
    async with consumer_lifecycle(flow.tracking_settings(bootstrap, group),
                                  topics=(flow.TOPIC,)) as replacement:
        record, = await fetch_count(replacement, 1)
    first = 5 if mode == "drain" else 0
    assert record.offset == first, (mode, record.offset)
    print(f"PASS {mode}: processed={processed}, committed={saved}, replacement starts={first}", flush=True)


async def main(bootstrap):
    await flow.provision_delivery_topic(bootstrap, partitions=1)
    await seed(bootstrap, count=10)
    for mode in ("cancel", "drain", "timeout"):
        await scenario(bootstrap, mode)


if __name__ == "__main__":
    with infrastructure() as (bootstrap, _):
        asyncio.run(main(bootstrap))
