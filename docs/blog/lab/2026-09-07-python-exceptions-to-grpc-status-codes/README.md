# Lab: Python exceptions to gRPC status codes {#lab-python-exceptions-to-grpc-status-codes}

The same internal `ValueError` is sent through three real gRPC server configurations: bare (`UNKNOWN` with internal text), the kit defaults (`INVALID_ARGUMENT` with safe details), and the explicit application mapping (`INTERNAL`, `internal_error`).

Further assertions cover seven application/internal failures, a successful invoice response, a deliberate `context.abort()`, the status recorded in metrics, and the errors captured for reporting. Expected application refusals are not reported as server incidents. A negative check moves the reporter outside the exception mapper and verifies that it misses the original exception.

Storage, metrics, and the error reporter are local fixtures; no database or external reporting service is used. A fake private marker detects leaked response details. Expected exception logs are suppressed so that the assertion results remain readable.

Requires `uv`. Run from `docs/blog/lab/2026-09-07-python-exceptions-to-grpc-status-codes`:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python mapping_lab.py
```

Versions are pinned in `requirements.txt`: grpc-server-kit 0.2.0, servicewright 0.13.1, grpcio 1.84.0, FastAPI 0.141.1, Uvicorn 0.53.0, HTTPX 0.28.1 and cryptography 50.0.1.

Keep the sibling `2026-09-07-production-grpc-server` directory: this lab imports its application code, fixtures, and requirements.

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-python-exceptions-to-grpc-status-codes).
