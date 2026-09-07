# Lab: exactly-once effects

One script behind the measurements. PostgreSQL 17 and Kafka run in containers started by the script.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "omni-box[postgres,kafka]" "testcontainers[kafka,postgres]" asyncpg
.venv/bin/python effects_lab.py
```

Four scenes: the two dual-write failure windows (commit then publish, publish then commit), the
outbox relay crashing after the send and republishing on the next cycle, and the inbox consumer
receiving both copies and writing the invoice once.
