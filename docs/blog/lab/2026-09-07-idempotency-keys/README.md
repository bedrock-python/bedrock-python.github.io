# Lab: idempotency keys

The script behind the idempotency measurements. Redis 7 runs in a container started by the script.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "idempotency-kit[redis]" "testcontainers[redis]"
.venv/bin/python measure.py
```

`measure.py` charges a card through a coordinator twice with the same key, 50 ms apart, while the
first charge is still in flight, and then reuses the key with a different amount.
