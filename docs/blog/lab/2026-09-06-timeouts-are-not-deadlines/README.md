# Lab: timeouts are not deadlines

The scripts behind the numbers in [the post](../../posts/2026-09-06-timeouts-are-not-deadlines.md).
Every server runs in-process on loopback; nothing here needs a network.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "deadline-budget==0.1.2" "clientwright[httpx,deadline]==0.2.0" "grpc-client-kit[deadline]==0.1.0"
.venv/bin/python 01_read_timeout.py
.venv/bin/python 02_retry_multiplies.py
.venv/bin/python 03_grpc_chain.py
.venv/bin/python 04_deadline_header.py
```

| Script | What it measures |
|---|---|
| `01_read_timeout.py` | httpx `timeout=1.0` against a body that drips for four seconds, against headers that stall, inside `asyncio.timeout`, and under clientwright's `total` |
| `02_retry_multiplies.py` | a hand-rolled three-attempt loop against a server that never answers, and the same attempts under one total |
| `03_grpc_chain.py` | gateway → orders → inventory, billing: the deadline each server saw, with a fresh timeout per call and with the gateway's deadline propagated; plus a 50 s budget against a 5 s configured call |
| `04_deadline_header.py` | the `X-Deadline-Ms` value an HTTP upstream receives on each attempt when the caller carries a request budget |
