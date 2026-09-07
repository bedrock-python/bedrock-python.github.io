"""The worker for the same service. There is no FastAPI here, so there is no lifespan: the plumbing is written again."""

import asyncio
import signal
import time

T0 = time.perf_counter()


def log(text: str) -> None:
    print(f"{time.perf_counter() - T0:6.2f} s  {text}", flush=True)


class Pool:  # copied from the API, or imported and wired by hand
    async def use(self, who: str) -> None:
        log(f"{who} used the pool")


async def main() -> None:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, stop.set)     # the API got this from uvicorn
    log("pool opened")                                    # the API got this from the lifespan
    pool = Pool()
    try:
        while not stop.is_set():
            await pool.use("worker loop")
            try:
                await asyncio.wait_for(stop.wait(), timeout=0.4)
            except TimeoutError:
                pass
        log("worker loop saw the stop event")
    finally:
        log("pool closed")                                # and this


asyncio.run(main())
