# Lab: what every production Python microservice reimplements

`service.py` is the hundred-line service from the post: servicewright for the lifecycle,
sqlalchemy-foundation-kit for sessions, clientwright for the outbound client, deadline-budget for
the request deadline. `run_skeleton.py` starts PostgreSQL in a container, a stub warehouse that
reports the deadline header it received, and the service as a subprocess, then calls it, sends
SIGTERM and prints the timeline.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "servicewright[fastapi,postgres]==0.10.0" "sqlalchemy-foundation-kit==0.2.1" \
  "clientwright[httpx,deadline]==0.2.2" "deadline-budget==0.1.3" asyncpg psycopg2-binary "testcontainers[postgres]"
.venv/bin/python run_skeleton.py
```
