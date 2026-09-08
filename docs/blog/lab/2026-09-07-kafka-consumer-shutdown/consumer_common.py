"""What both consumers share: settings, the topic, and how a message is 'processed'."""

import asyncio
import os
import sys
import time

from aiokafka_foundation_kit.contrib.models import BaseKafkaConsumerSettings

TOPIC = os.environ.get("ORDERS_TOPIC", "orders")
T0 = time.perf_counter()


def log(text: str) -> None:
    print(f"{time.perf_counter() - T0:6.2f} s  {text}", flush=True)


def settings() -> BaseKafkaConsumerSettings:
    return BaseKafkaConsumerSettings(bootstrap_servers=os.environ["KAFKA"], group_id=os.environ["GROUP"], auto_offset_reset="earliest")


async def process(message) -> None:
    await asyncio.sleep(0.2)   # the work: an insert, a call, a mail
    log(f"processed {message.value['n']}")
