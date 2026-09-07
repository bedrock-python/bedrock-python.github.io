# Lab: retries can make an outage worse

One script behind the retry-storm measurements, against clientwright's in-process origin.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "clientwright[httpx]==0.2.2"
.venv/bin/python storm_lab.py
```

Four scenes: fifty callers against an origin that answers 503 to everything, with no retries, with
three attempts and no budget, and with the default budget; the same fifty with sparse and with dense
transient failures; and ten callers at the top of a three-service chain where every hop retries,
without and with circuit breakers and budgets.
