# Lab: idempotency for background jobs and consumers

One script against Redis 7 in a container the script starts.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "idempotency-kit[redis]==0.3.0" "testcontainers[redis]"
.venv/bin/python jobs_lab.py
```

Three scenes: a worker that crashes after its effect and before acknowledging the job, with and
without an idempotency key; two workers holding the same job at once under the two in-flight modes;
and what happens when the key is the delivery's identity, the effect's identity, or contains a
character the key may not contain.
