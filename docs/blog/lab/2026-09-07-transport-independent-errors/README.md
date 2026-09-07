# Lab: one domain error, two transports

One service with a FastAPI entrypoint and a gRPC entrypoint over the same use case. The use case
raises `ServiceError` subclasses and a plain `RuntimeError`; the driver calls both transports for
every case and prints what each told the caller.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "servicewright[fastapi,grpc]==0.10.1" "httpx==0.28.1"
.venv/bin/python driver.py
```
