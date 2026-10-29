# Lab: timeouts are not deadlines

The scripts behind the numbers in [the post](../../posts/2026-09-06-timeouts-are-not-deadlines.md).
Every server runs in-process on loopback; only installing packages needs external network access.
From this directory, run the scripts with the versions pinned in `requirements.txt`:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt 01_read_timeout.py
uv run --no-project --python 3.13 --with-requirements requirements.txt 02_retry_multiplies.py
uv run --no-project --python 3.13 --with-requirements requirements.txt 03_grpc_chain.py
uv run --no-project --python 3.13 --with-requirements requirements.txt 04_deadline_header.py
```

| Script | What it measures |
|---|---|
| `01_read_timeout.py` | httpx `timeout=1.0` against a body that drips for four seconds, against headers that stall, inside `asyncio.timeout`, and under clientwright's `total` |
| `02_retry_multiplies.py` | a hand-rolled three-attempt loop against a server that never answers, and the same attempts under one total |
| `03_grpc_chain.py` | gateway → orders → inventory, billing: the deadline each server saw, with a fresh timeout per call and with the gateway's deadline propagated; plus a 50 s budget against a 5 s configured call |
| `04_deadline_header.py` | the `X-Deadline-Ms` value an HTTP upstream receives on each attempt when the caller carries a request budget |

Timings and header values vary with scheduling and connection setup. The HTTPX adapter in clientwright 0.2.2 raises `HttpxDeadlineExceededError`, a subclass of both `clientwright.DeadlineExceededError` and `httpx.TimeoutException`.

The gRPC lab uses `asyncio.shield()` to model work already accepted by an external payment system. It deliberately continues after handler cancellation; this is not a claim that all database writes behave that way. Propagation prevents starting the simulated charge when too little time remains, but does not undo the earlier stock reservation.
