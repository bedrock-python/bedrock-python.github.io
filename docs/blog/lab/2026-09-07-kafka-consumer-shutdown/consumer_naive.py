"""The batch loop without a stop-and-drain owner; the driver cancels it mid-batch."""

from aiokafka_foundation_kit import consumer_lifecycle

from consumer_common import flow


async def consume(bootstrap, process, stop, group):
    async with consumer_lifecycle(flow.tracking_settings(bootstrap, group),
                                  topics=(flow.TOPIC,)) as consumer:
        await flow.consume_batches(consumer, process, stop)
