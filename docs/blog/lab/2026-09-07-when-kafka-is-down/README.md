# Lab: what happens when Kafka is down for an hour?

One script. PostgreSQL 17 and Kafka run in containers the script starts; "Kafka is down" is the
container paused, so the broker neither answers nor refuses.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "omni-box[postgres,kafka]" "testcontainers[kafka,postgres]" asyncpg
.venv/bin/python kafka_down_lab.py
```

Twenty events go into the outbox, Kafka is paused, the relay runs seven cycles, Kafka comes back,
the relay runs again, and the script prints the outbox statuses and the topic's message count at
each step. The whole run takes about five minutes, most of it the paused cycles.
