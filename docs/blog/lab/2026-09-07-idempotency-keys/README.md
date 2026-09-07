# Lab: idempotency keys

The script behind the idempotency measurements. Redis 7 runs in a container started by the script.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "idempotency-kit[redis]==0.3.0" "testcontainers[redis]"
.venv/bin/python measure.py
```

`measure.py` charges a card through a coordinator twice with the same key, 50 ms apart, while the
first charge is still in flight, under each of the three in-flight modes; then reuses the key with a
different amount, fails an action, and points a coordinator at a Redis that is not there.
