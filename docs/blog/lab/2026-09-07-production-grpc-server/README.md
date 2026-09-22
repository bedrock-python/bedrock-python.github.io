# Lab: the anatomy of a production gRPC server {#lab-the-anatomy-of-a-production-grpc-server}

Real localhost gRPC calls verify message and concurrency limits, health transitions and timeouts, explicit cancellation, client deadlines, graceful and forced shutdown, TLS and mTLS. Storage is an in-memory fixture; metrics and error reports are recorded in lists. No database, Sentry account, or Docker is needed.

The concurrency check distinguishes waiting for a stream on one HTTP/2 connection from a server-wide refusal on a separate connection. Both prevent another storage read. Health reports `NOT_SERVING` without blocking a direct business RPC. Deadline expiry returns `DEADLINE_EXCEEDED` to the client and records `CANCELLED` at the cancelled server handler.

Shutdown assertions verify that the shared store closes after handler cleanup, both when the request finishes within the grace period and when it is cancelled at the limit. TLS checks create one-day certificates in a temporary directory using `cryptography`; no external `openssl` executable is required. Failed handshakes deliberately print gRPC diagnostics.

Invalid PEM input is rejected. The Unix permission-bit assertion runs only on Unix; Windows skips that assertion because the library delegates file access protection to Windows ACLs. TLS and mTLS handshakes run on both platforms.

Requires `uv`. Run from `docs/blog/lab/2026-09-07-production-grpc-server`:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python server_lab.py
```

Versions are pinned in `requirements.txt`: grpc-server-kit 0.2.0, servicewright 0.13.1, grpcio 1.84.0, FastAPI 0.141.1, Uvicorn 0.53.0, HTTPX 0.28.1 and cryptography 50.0.1.

Article snippets come from `invoice_domain.py` and `grpc_flow.py`. `lab_support.py` provides fixtures; `tls_support.py` generates certificates. The method uses bytes through a generic handler, so no protobuf code generation is required.

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-production-grpc-server).
