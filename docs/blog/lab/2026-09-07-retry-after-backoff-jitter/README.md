# Lab: Retry-After, backoff and jitter

One script against clientwright's in-process origin.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "clientwright[httpx]==0.2.2"
.venv/bin/python backoff_lab.py
```

Four scenes: a `503` with a `Retry-After` header, honoured and ignored; fifty callers retrying at once
with and without jitter, and when their retries land; a POST that timed out on read, with and without
being declared idempotent, and how many times the origin received it; and which outcomes and methods
are retried by default.
