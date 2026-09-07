"""Run each consumer, SIGTERM it mid-batch, start a replacement, and count what was processed twice and how long the handover took."""

import asyncio
import os
import re
import signal
import subprocess
import sys
import time
import uuid

from aiokafka import AIOKafkaProducer
from testcontainers.kafka import KafkaContainer

MESSAGES = 30


async def seed(bootstrap: str, topic: str) -> None:
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap)
    await producer.start()
    for n in range(MESSAGES):
        await producer.send_and_wait(topic, value=('{"n": %d}' % n).encode())
    await producer.stop()


def run_instance(script: str, env: dict, until: str, sigterm_after_processed: int | None) -> tuple[list[str], float | None, int | None, float]:
    proc = subprocess.Popen([sys.executable, script], env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    lines, processed, sent_at, started = [], 0, None, time.perf_counter()
    first_message_at = None
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        line = proc.stdout.readline()
        if not line:
            break
        lines.append(line.rstrip())
        if "processed" in line:
            processed += 1
            first_message_at = first_message_at or time.perf_counter() - started
        if sigterm_after_processed and processed == sigterm_after_processed and sent_at is None:
            sent_at = time.perf_counter()
            os.kill(proc.pid, signal.SIGTERM)
        if sigterm_after_processed is None and processed >= int(until):
            break
    if proc.poll() is None:
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
    exit_after = (time.perf_counter() - sent_at) if sent_at else None
    return lines, exit_after, proc.returncode, first_message_at


async def main(bootstrap: str) -> None:
    for script in ("consumer_naive.py", "consumer_service.py"):
        group = f"billing-{uuid.uuid4().hex[:6]}"
        topic = f"orders-{group}"
        await seed(bootstrap, topic)
        env = {**os.environ, "KAFKA": bootstrap, "GROUP": group}
        # the topic name is shared through the env too: both consumers read TOPIC from the module, so patch it
        env["ORDERS_TOPIC"] = topic
        lines1, exit_after, code, _ = run_instance(script, env, until="", sigterm_after_processed=8)
        seen1 = [int(m.group(1)) for l in lines1 for m in [re.search(r"processed (\d+)", l)] if m]
        lines2, _, _, first_at = run_instance(script, env, until=str(MESSAGES - len(set(seen1))), sigterm_after_processed=None)
        seen2 = [int(m.group(1)) for l in lines2 for m in [re.search(r"processed (\d+)", l)] if m]
        dupes = sorted(set(seen1) & set(seen2))
        print(f"--- {script} ---")
        for l in lines1[-6:]:
            print("   " + l)
        print(f"   first instance: processed {len(seen1)} messages, SIGTERM after 8, exited with {code} {exit_after:.2f} s after the signal")
        print(f"   second instance: first message {first_at:.2f} s after start, processed {len(seen2)}; processed twice: {dupes}\n")


with KafkaContainer() as kafka:
    asyncio.run(main(kafka.get_bootstrap_server()))
