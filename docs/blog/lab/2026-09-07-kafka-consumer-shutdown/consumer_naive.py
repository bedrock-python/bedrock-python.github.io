"""The consumer most codebases run: a loop, a batch, a commit at the end of the batch, and SIGTERM handled by dying."""

import asyncio
import os
import signal

from aiokafka_foundation_kit import consumer_lifecycle

from consumer_common import TOPIC, log, process, settings

signal.signal(signal.SIGTERM, lambda *_: (log("SIGTERM: exiting now"), os._exit(143)))


async def main() -> None:
    async with consumer_lifecycle(settings(), topics=(TOPIC,)) as consumer:
        log("consuming")
        while True:
            batches = await consumer.getmany(timeout_ms=500, max_records=5)
            for records in batches.values():
                for message in records:
                    await process(message)
            if batches:
                await consumer.commit()
                log("committed")


asyncio.run(main())
