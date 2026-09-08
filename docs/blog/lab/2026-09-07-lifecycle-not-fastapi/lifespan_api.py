"""The service as most FastAPI codebases write it: the lifecycle lives in the app's lifespan."""

import contextlib
import sys
import time

import uvicorn
from fastapi import FastAPI

T0 = time.perf_counter()


def log(text: str) -> None:
    print(f"{time.perf_counter() - T0:6.2f} s  {text}", flush=True)


class Pool:
    async def use(self, who: str) -> None:
        log(f"{who} used the pool")


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    log("pool opened")                      # startup: the pool, warmup, health registration, ...
    app.state.pool = Pool()
    yield
    log("pool closed")                      # shutdown: ... in whatever order uvicorn gets here


app = FastAPI(lifespan=lifespan)


@app.get("/work")
async def work() -> dict[str, str]:
    await app.state.pool.use("http request")
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(sys.argv[1]), log_level="warning")
