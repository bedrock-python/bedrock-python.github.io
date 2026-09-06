# Lab: graceful shutdown is a protocol

The scripts behind the shutdown measurements: two servers with the same two routes, and a driver
that plays Kubernetes against them.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "servicewright[fastapi]" httpx
.venv/bin/python driver.py server_plain.py
.venv/bin/python driver.py server_servicewright.py
```

| Script | What it is |
|---|---|
| `routes.py` | `/work` (20 ms) and `/slow` (2 s), shared by both servers |
| `server_plain.py` | FastAPI under `uvicorn.run`, uvicorn's own SIGTERM handling |
| `server_servicewright.py` | the same routes under servicewright's lifecycle |
| `driver.py` | starts a server, waits for readiness, starts one slow request, sends SIGTERM, keeps sending one request every 20 ms for `LAG` seconds (the endpoint propagation lag), polls readiness, and counts what came back |
