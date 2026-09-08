# Lab: safe gRPC retries

One script behind the retry measurements. An in-process `grpc.aio` server exposes a `Charge` method
whose behaviour is chosen by the request (fail before the charge, fail after it, be slow) and counts
every charge it made, plus an `Export` stream that breaks at the third item on its first attempt.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "grpc-client-kit[deadline]==0.1.0"
.venv/bin/python retries_lab.py
```
