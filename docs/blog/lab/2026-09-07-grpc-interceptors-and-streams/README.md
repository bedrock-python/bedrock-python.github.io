# Lab: gRPC client interceptors and streaming RPCs

One in-process gRPC server with all four RPC kinds, and client interceptors asked the same
questions: which kinds the channel registered them for, how long they measured the call, whether
they saw a mid-stream failure, whether their context was still set while items arrived, and what
the caller is left holding afterwards.

- `interceptors_lab.py` — the four interceptors side by side.
- `probe.py` — what happens to an `around_call` that carries a `ContextVar` token across the
  yield, per RPC kind.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "grpc-client-kit==0.1.1"
.venv/bin/python interceptors_lab.py
.venv/bin/python probe.py
```
