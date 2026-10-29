# Lab: gRPC retries, deadlines and stream restarts {#lab-safe-grpc-retries}

`grpc_flow.py` contains the article's policy and clients. `grpc_origin.py` runs a real `grpc.aio` server with raw-byte methods: `GetStock` reads, `Reserve` records a side effect before failing, and `Export` breaks after two elements.

The driver asserts read retries, exclusion of writes from the allowlist, separate audit behavior, duplicate effects with unrestricted retries, a shared RPC deadline, and an attempt-counting gRPC breaker. It also checks the stream results: `[1, 2]` followed by failure with retries off; `[1, 2, 1, 2, 3]` with explicit restart enabled.

Native gRPC retries are disabled so the interceptor is the only retry layer. The local transport is insecure; TLS and production protobuf schemas are outside this test. The pool and server close through context managers even if an assertion fails. No Docker is needed.

Run from `docs/blog/lab/2026-09-07-safe-grpc-retries` in the repository checkout. Dependencies are pinned in `requirements.txt`.

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python retries_lab.py
```

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-safe-grpc-retries).
