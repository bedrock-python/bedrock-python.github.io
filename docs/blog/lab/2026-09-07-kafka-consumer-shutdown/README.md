# Lab: graceful Kafka consumer shutdown in Kubernetes

Two consumers with the same processing loop, and a driver that plays a rollout against each: start
it, send SIGTERM in the middle of a batch, start a replacement in the same group, and count what
was processed twice and how long the replacement waited for its first message. Kafka runs in a
container the driver starts.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "aiokafka-foundation-kit[models]==0.1.2" "servicewright==0.10.0" "testcontainers[kafka]"
.venv/bin/python driver.py
```

| Script | What it is |
|---|---|
| `consumer_common.py` | settings, the topic, and the 200 ms "work" per message |
| `consumer_naive.py` | a loop with a commit per batch, and SIGTERM handled by exiting immediately |
| `consumer_service.py` | the same loop under servicewright's lifecycle: finish the batch, commit, leave the group |
| `driver.py` | the rollout |
