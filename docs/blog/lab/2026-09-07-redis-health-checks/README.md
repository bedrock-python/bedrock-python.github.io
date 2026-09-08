# Lab: Redis health checks, PING is not the whole story

One script starting three Redis 7 containers on one network: a healthy primary, a primary at
`maxmemory 1mb` with `noeviction`, and a replica of the first. Each is asked the kit's health check
(PING) and a write-then-read probe; then the primary is paused.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "redis-client-kit[settings]==0.2.0" "testcontainers[redis]"
.venv/bin/python health_lab.py
```
