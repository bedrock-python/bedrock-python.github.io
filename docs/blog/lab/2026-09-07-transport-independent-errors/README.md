# Lab: one domain error, two transports {#lab-one-domain-error-two-transports}

Servicewright runs HTTP and gRPC in one process on OS-assigned ports. Both handlers call the same invoice function. The driver sends actual network requests, checks matching success payloads, and verifies seven failures through both transports.

The HTTP response uses `application/problem+json`; gRPC sends the same application code in `x-error-code` trailing metadata. The unpaid order is `PRECONDITION_FAILED`: HTTP 412 and gRPC `FAILED_PRECONDITION`. Private errors and unexpected exceptions become `internal_error`; internal messages, parameters, and private error codes must not appear in the responses.

The driver stops the service through its stop event and asserts that the shared storage closes after both entrypoints finish. Storage is an in-memory fixture. Buyer identity is trusted fixture data; this lab does not implement authentication.

Requires `uv`. Run from `docs/blog/lab/2026-09-07-transport-independent-errors`:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python driver.py
```

Versions are pinned in `requirements.txt`: grpc-server-kit 0.2.0, servicewright 0.13.1, grpcio 1.84.0, FastAPI 0.141.1, Uvicorn 0.53.0, HTTPX 0.28.1 and cryptography 50.0.1.

Keep the sibling `2026-09-07-production-grpc-server` directory: this lab imports its application code, fixtures, and requirements.

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-transport-independent-errors).
