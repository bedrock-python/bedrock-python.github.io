# Lab: gRPC channels should not be pooled by address alone

One script with an in-process `grpc.aio` server that counts the attempts it receives.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "grpc-client-kit==0.1.0"
.venv/bin/python identity_lab.py
```

Three scenes: two clients with different interceptor chains sharing one address, under a pool
keyed by address and under one keyed by identity; a chain rebuilt per request and the channels it
mints; and two keepalive configurations for the same address. The channel count reads the pool's
private entry table, which is what the lab is measuring.
