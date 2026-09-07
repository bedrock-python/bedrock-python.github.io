# Lab: reliability is not retry=3

One in-process origin and forty concurrent callers, through six client configurations: no retries,
`retry=3`, retry under a one-second deadline, retry with a budget, retry with a per-origin circuit
breaker, and two waves through the same client so the breaker has seen the failures. For each: how
many requests the origin received, how many callers were served, how long the slowest waited, and
how long after the origin healed the first caller got through.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "clientwright[httpx]==0.2.2" "httpx==0.28.1"
.venv/bin/python reliability_lab.py
```
