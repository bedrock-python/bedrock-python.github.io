# Lab: idempotency across a chain of services

Three services in one process — a gateway, orders and payments — each calling the next over HTTP
with its own retries, and Redis in a container behind the idempotency store. The first attempt
always takes longer than the caller's timeout, so the charge happens and the answer is lost. Four
designs run against that: no idempotency, a fresh key per attempt, the caller's key propagated
down the chain, and no header at all with each hop keying on a fingerprint of its request.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "idempotency-kit[redis]==0.3.0" "httpx==0.28.1" "testcontainers[redis]"
.venv/bin/python chain_lab.py
```
