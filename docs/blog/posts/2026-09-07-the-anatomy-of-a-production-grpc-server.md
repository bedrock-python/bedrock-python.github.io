---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - grpc-server-kit
  - grpc
  - asyncio
  - tls
  - health-checks
  - graceful-shutdown
---

# The anatomy of a production Python gRPC server

A `grpc.aio` server is six lines. A `grpc.aio` server you can put behind a load balancer, roll out three times a day and hand to an on-call rota is a different object, and the difference is not size, it is a list of decisions that each have an incident behind them. I built the six-line one and asked a client what it got. It handed the caller the database password. It answered nothing when Kubernetes asked whether it was alive. It cancelled a payment mid-flight on every deploy. Below is each part, the failure it prevents, and what a client actually sees with and without it.

<!-- more -->

The numbers come from [the post's lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-production-grpc-server), an in-process server built several ways with a client reporting the status codes it received. Versions: grpc-server-kit 0.1.1, grpcio 1.83.1, Python 3.13.

## The handler that raises

Every handler raises eventually, usually with a message written for a log line. Here is one:

```python
async def place(self, request, context):
    raise RuntimeError(f"could not reach the ledger at {dsn}")
```

Without an interceptor to map it, this is what the caller is told:

```text
UNKNOWN: "Unexpected <class 'RuntimeError'>: could not reach the ledger at postgresql://orders:hunter2@db.internal:5432/orders"
```

The connection string, the internal hostname and the password went over the wire to whoever made the call. gRPC's default for an unhandled exception is to put `repr` of it in the status details, which is a reasonable default for a debugging tool and a data leak in a service. The status is `UNKNOWN`, so the caller's retry policy has no idea whether trying again is safe.

With an interceptor that maps exceptions to statuses, the same handler produces:

```text
INTERNAL: 'Internal server error'
```

and the exception, with its traceback, goes to the server's log where it belongs. The mapping is the part worth thinking about rather than the redaction: a `TimeoutError` from a dependency is `DEADLINE_EXCEEDED` or `UNAVAILABLE` and a caller may retry it, a `ValueError` from parsing is `INVALID_ARGUMENT` and no caller should ever retry it. The default map covers the standard exceptions; a service adds its own domain errors to it.

Deliberate aborts pass through untouched in both cases:

```text
PERMISSION_DENIED: 'not your order'
```

which is the point. `context.abort()` is how a handler says something specific, and nothing should rewrite it.

## Where the reporting interceptor goes

Interceptors are a list, and the list is outermost first. That order is semantics, not style, and the one that catches people is error reporting. Put a Sentry-style interceptor at the top of the list and it wraps the exception handler, so by the time an exception reaches it, it is no longer an exception.

The lab uses a counting stand-in for Sentry and asks it what it saw, for a handler that raised `RuntimeError` and a handler that aborted with `PERMISSION_DENIED`:

```text
    reporter first (outermost)   reported: ['AbortError', 'AbortError']
    reporter after the handler   reported: ['RuntimeError', 'AbortError']
```

From the outer position it never sees a single real exception. Both RPCs reach it as `AbortError`, because the exception handler below it did its job and converted the `RuntimeError` into an abort. Your error tracker fills with `AbortError`, one per failure, all identical, and the bug that caused them is not in any of them.

The second line is the correct position, and it shows the other half of the problem. `AbortError` still arrives, because a deliberate `context.abort()` is also an exception on the way out. A reporter that captures everything reports every permission denial as an error. The rule is to filter aborts out and report what is left.

There is a smaller trap inside this one. `AbortError` is not a `grpc.RpcError`, so the filter people write first does not catch it:

```python
except grpc.RpcError:   # never matches a deliberate abort
```

In the lab both aborts landed in the `except Exception` branch. If you filter on `RpcError`, you filter nothing.

## Message size

gRPC's default receive limit is four mebibytes, and the kit keeps it. A five-mebibyte request gets:

```text
RESOURCE_EXHAUSTED: 'SERVER: Received message larger than max (5242880 vs. 4194304)'
```

That is the right default and the wrong thing to discover in production, because the payload that crosses it is never the one you tested with. Raise it deliberately if your API has a legitimately large message, and know that the limit is per message on both ends: the client has its own send limit, and both have to agree.

The rest of the defaults the kit hands to `grpc.aio.server()` are worth reading once:

```text
    grpc.keepalive_time_ms                     7200000
    grpc.keepalive_timeout_ms                  20000
    grpc.keepalive_permit_without_calls        0
    grpc.http2.max_pings_without_data          2
    grpc.http2.min_recv_ping_interval_without_data_ms 300000
    grpc.max_metadata_size                     8192
    grpc.max_receive_message_length            4194304
    grpc.max_send_message_length               4194304
```

Two hours between keepalive pings is gRPC's own default, and it is the number to change first if your server sits behind a load balancer that drops idle connections after five minutes. The failure it produces is the one that looks like a network fault: a client that has been idle sends a request into a connection the balancer closed, and gets `UNAVAILABLE` on the first call after every quiet period. A keepalive under the balancer's idle timeout keeps the connection provably alive; `min_recv_ping_interval_without_data_ms` is the same argument from the server's side, the rate below which it treats a client's pings as abuse.

## Shutdown

A pod is deleted. Kubernetes sends `SIGTERM` and starts counting to `terminationGracePeriodSeconds`. What the server does in that window decides whether the requests in flight finish or turn into errors on someone else's dashboard.

With a grace period, the server stops accepting new connections and lets the running RPCs finish:

```text
    grace_period=5.0   stop() took 1.61 s, handler finished 1/1, client: the response arrived
```

The stop returned as soon as the last in-flight handler was done, not after the whole five seconds. The grace period is a budget, not a delay.

Without one:

```text
    grace_period=0.0   stop() took 0.00 s, handler finished 0/1, client: UNAVAILABLE: Cancelling all calls
```

The handler never finished. Whatever it was in the middle of, a database write, a charge, a message to another service, stopped where it was, and the caller got `UNAVAILABLE`, which their retry policy will read as "safe to try again". That is a duplicate effect manufactured by a deploy.

One number to be careful with: in gRPC, `stop(None)` means abort immediately, not wait forever. The settings object types the grace period as a non-negative float and defaults it to five seconds, which is the sane reading, but if you drop to the lower-level API and pass `None` because it looks like "no limit", you get the second line above.

The grace period also has to fit inside the pod's termination budget, with room for whatever else the process drains. That arithmetic is [the shutdown post](2026-09-07-graceful-shutdown-is-a-protocol.md); here it is one term in it.

## Health

gRPC has a health checking protocol, `grpc.health.v1.Health`, and Kubernetes can use it directly as a gRPC probe. A server that does not register it answers:

```text
    no enable_health(): Check -> UNIMPLEMENTED: Method not found!
```

A `grpc_health_probe` against that server fails, and a `readinessProbe` reading the failure takes the pod out of rotation, or, worse, if the probe is a TCP one instead, the pod stays in rotation forever, because a socket that accepts is not a service that works. That is the same argument as [the Redis health post](2026-09-07-when-should-redis-fail-open.md): the question is not whether the process is alive, it is whether it can serve.

With checkers registered, the status follows the dependency:

```text
    database up:   Check -> SERVING
    database down: Check -> NOT_SERVING
    ... and the service itself still answers: OK
    database back: Check -> SERVING
```

The third line is the one to think about. While the database was down, the health service reported `NOT_SERVING` and the RPC still worked, because the handler in this lab does not touch the database. Health is a claim about the service's ability to do its job, and a checker set that is too broad takes a pod out of rotation for a dependency half its endpoints do not need. Registering per-service statuses rather than one global one is how that gets separated: `Check` takes a service name, and the empty name is the whole server.

The other side of the same trade is a checker that is too expensive. It runs on a schedule and its results are cached with a TTL, because a probe every second that opens a connection every time is a load generator pointed at the dependency you are trying to protect.

## TLS, and the file permissions

TLS on a gRPC server is a certificate, a key and a decision about clients. The kit refuses to load a private key that anyone but its owner can read:

```text
    a key readable by the group: PermissionError: Sensitive file .../server.key has too permissive
    permissions (0o640). Private keys must be readable only by owner (chmod 600).
```

That is a start-up failure by design, on the theory that a key with group read is a key you should assume is compromised, and the moment to find out is before the process serves traffic.

With the key locked down, the three kinds of client:

```text
    TLS, no client certificate required  plaintext client: UNAVAILABLE, TLS client: OK, mTLS client: OK
    mTLS, client certificate required    plaintext client: UNAVAILABLE, TLS client: UNAVAILABLE, mTLS client: OK
```

The first line is ordinary TLS: anyone who trusts the CA can call, and a plaintext client fails at the handshake. The second is mutual TLS, where the server demands a certificate from the caller too, and a client that has only the CA is refused. That refusal reaches the client as `UNAVAILABLE`, not as anything that says "your certificate is missing", so mTLS rollouts are best done with the server's handshake log open. The failures in the lab's stderr are explicit where the client's status is not:

```text
Handshake failed with error SSL_ERROR_SSL: ... PEER_DID_NOT_RETURN_A_CERTIFICATE
```

If service-to-service authentication is the goal, mTLS is the mechanism that does not depend on anything in the request body being honest. What it does not give you is authorization, which is a separate interceptor reading the peer identity and deciding what that identity may call.

## Reflection, and the rest of the list

Reflection lets `grpcurl` and Postman talk to a server without a copy of its `.proto`. It is a development convenience and an information disclosure, in that order: turning it on in production publishes the shape of every service you run. The kit requires the service names explicitly rather than reflecting whatever is registered, which at least makes it a decision.

That leaves the parts this post has not measured but that belong on the same list. A context interceptor that pulls the request id out of the metadata and binds it to the logging context, so a log line can be traced back to a call. A metrics interceptor, whose method label is the full RPC name, because per-service aggregates hide the one endpoint that is slow. A tracing interceptor, which opens a span but does not read `traceparent` on its own: incoming trace context comes from instrumenting the server, and the two compose. And `max_concurrent_rpcs`, which is the only thing standing between a traffic spike and an out-of-memory kill, since a server with no limit accepts every request and queues them in memory.

## The order

The list, outermost first, ends up:

```python
interceptors = [
    AsyncMetricsInterceptor(metrics, service_name="orders"),
    AsyncContextInterceptor(header_configs),
    AsyncRequestLoggerInterceptor(),
    AsyncTracingInterceptor("orders"),
    AsyncExceptionHandlerInterceptor(),
    AsyncSentryInterceptor(),
]
```

Metrics outermost, because it should time everything including the layers below it. Context next, because the layers under it log and trace with those values bound. The exception handler near the bottom, because everything above it should see statuses rather than exceptions. The reporter below the handler, for the reason the second section measured.

And interceptors are handed to `grpc.aio.server()` at construction. There is no adding one to a running server, which is the mechanical reason this list is a decision you make once, at build time, rather than something a plugin can extend later.

## The pieces

All of the above is [grpc-server-kit](https://bedrock-python.github.io/grpc-server-kit/): the settings object that validates before anything binds, the credential loader that checks the key's permissions, the six interceptors in that order, the health service with its checkers and cache, and a lifecycle that installs the signal handlers and drains with the grace period. It compiles no protobufs and has no client side; the generated `add_*Servicer_to_server` functions and the stubs stay yours.

The six-line server is fine. It is just answering a different question than the one production asks.
