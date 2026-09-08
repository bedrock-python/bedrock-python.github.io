# Lab: the anatomy of a production gRPC server

One in-process `grpc.aio` server, built six ways, and a client that reports what it got: what an
unhandled handler exception tells the caller, what a reporting interceptor sees from either side
of the exception handler, what a payload over the size limit gets, what a shutdown does to a
request that is still running, what the health service says while a dependency is down, and what
TLS and mTLS refuse. The certificates are generated with `openssl` into a temporary directory.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "grpc-server-kit[health,settings]==0.1.1"
.venv/bin/python server_lab.py
```
