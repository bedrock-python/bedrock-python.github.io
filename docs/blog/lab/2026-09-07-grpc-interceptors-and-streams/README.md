# Lab: gRPC client interceptors and streaming RPCs {#lab-grpc-client-interceptors-and-streaming-rpcs}

An export worker calls a real local reporting service. The lab checks registration, streaming outcomes, context and cleanup. Companion to [Why gRPC interceptors break on streaming RPCs](../../posts/2026-09-07-why-grpc-interceptors-break-on-streaming-rpcs.md).

## Run {#run}

Install uv, then run from the website repository root. uv downloads Python or dependencies if needed; the RPCs use only loopback, with an automatically selected port.

```bash
cd docs/blog/lab/2026-09-07-grpc-interceptors-and-streams
uv run --no-project --python 3.13 --with-requirements requirements.txt python interceptors_lab.py
uv run --no-project --python 3.13 --with-requirements requirements.txt python probe.py
```

Pinned versions: `grpc-client-kit==0.4.0`, `grpcio==1.84.0`; Python 3.13. Byte messages and generic handlers keep protobuf generation out of this example. This is a client-interceptor experiment, not a benchmark or a deployment configuration.

## Assertions {#assertions}

| Scenario | What must hold |
|---|---|
| One native object inheriting four bases | Only unary-unary runs in this grpcio version |
| One logical interceptor, four adapters | Each RPC shape produces one successful observation |
| Timer around continuation | It really runs, finishes before the first row and misses the later network failure |
| Timer around iteration | Counts the mid-stream error; retains status, details and trailing metadata |
| Library observer | Five rows on success; two rows then `UNAVAILABLE` on failure |
| Early exit | Explicit cancellation stops the server handler and produces one `CANCELLED` record |
| `break` without cancellation | The held RPC remains active until explicitly cancelled |
| Fast stream | The observer can finish before the consumer resumes past the final row |
| Streaming request with `write()` | `done_writing()` allows a final response without an interceptor deadlock |
| Context scope | Token reset succeeds for all four shapes; the caller's context stays unchanged |
| Teardown raises `RuntimeError` | Four successes and one `UNAVAILABLE` keep their outcomes; five failures are logged |

Both scripts fail on a violated assertion or an unhandled asyncio error. Completion is synchronized through queues and events with timeouts, not arbitrary sleeps. Server delays simulate row production; printed elapsed times vary between runs and are not exact assertions.

## Files {#files}

- `report_service.py`: four RPC handlers, failure and cancellation fixtures, server lifecycle.
- `observers.py`: native and logical interceptors copied into the article.
- `consumer.py`: full download and caller-owned context with cancellation on early exit.
- `interceptors_lab.py`: the streaming scenarios and call-interface checks.
- `probe.py`: context isolation and teardown-error logging.
- `requirements.txt`: exact library versions.

The small observation queues are test collectors. Application processing can outlive the RPC; measure the full export separately. A context value set inside an interceptor does not automatically become the caller's value or a gRPC metadata field.
