# Lab: the transactional inbox

One script. PostgreSQL 17 and Kafka run in containers the script starts.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "omni-box[postgres,kafka]==0.2.0" "testcontainers[kafka,postgres]" asyncpg
.venv/bin/python inbox_lab.py
```

For each ack strategy: one message, a handler that writes an invoice and then fails on its first run,
then a fresh consumer of the same group, and what it receives. The duplicate-delivery scene is in
[the exactly-once lab](../2026-09-07-exactly-once-effects/).
