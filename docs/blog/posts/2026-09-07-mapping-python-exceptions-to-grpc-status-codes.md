---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - grpc-server-kit
  - grpc
  - errors
  - security
  - api-design
---

# Mapping Python exceptions to gRPC status codes without leaking internals

<div class="bdr-post__hero" data-bdr-post="2026-09-07-mapping-python-exceptions-to-grpc-status-codes" role="img" aria-label="Many exception types collapse into few status codes, with the internals filtered out" markdown="0"></div>

gRPC has sixteen status codes and your service has a hundred exception types, so somebody has to write the map. Done badly, it produces two failures at once: callers cannot tell a retryable failure from a permanent one, and the exception message goes over the wire to whoever called. I sent eleven exceptions through four configurations of one server and read what the client got back. Two of the eleven contained a database password.

<!-- more -->

The numbers come from [the post's lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-python-exceptions-to-grpc-status-codes). Versions: grpc-server-kit 0.1.1, grpcio 1.83.1, Python 3.13.

## What happens with no map at all

```text
    ValueError        UNKNOWN  "Unexpected <class 'ValueError'>: amount must be positive"
    PermissionError   UNKNOWN  "Unexpected <class 'PermissionError'>: token lacks scope orders:write"
    ConnectionError   UNKNOWN  "Unexpected <class 'ConnectionError'>: could not connect to
                               postgresql://orders:hunter2@db.internal:5432/orders"
    RuntimeError      UNKNOWN  "Unexpected <class 'RuntimeError'>: ledger write failed against
                               postgresql://orders:hunter2@db.internal:5432/orders"
```

Every failure is `UNKNOWN`, and every exception message is public.

The `UNKNOWN` part is the operational problem: a caller cannot distinguish "your request was invalid" from "our database is down", so its retry policy has nothing to work with. Retry everything and a bad request becomes a storm; retry nothing and a transient failure becomes a user-visible error.

The message part is the security problem, and it is not a hypothetical. Two of these exceptions carry a connection string, because that is what a driver puts in its error, and nobody wrote them intending them to be public. gRPC's default is to serialise the exception's `repr` into the status details, which is a fine default for a debugging tool and the wrong one for a server.

## The default map

```text
    ValueError           INVALID_ARGUMENT     'Invalid request data'
    PermissionError      PERMISSION_DENIED    'Permission denied'
    FileNotFoundError    NOT_FOUND            'Resource not found'
    TimeoutError         DEADLINE_EXCEEDED    'Deadline exceeded'
    NotImplementedError  UNIMPLEMENTED        'Method is not implemented'
    KeyError             INTERNAL             'Internal server error'
    ConnectionError      INTERNAL             'Internal server error'
    RuntimeError         INTERNAL             'Internal server error'
```

Five standard exceptions map to the status codes they obviously mean; everything else becomes `INTERNAL`, and every message is replaced with a safe string keyed on the status. The passwords are gone.

The `INTERNAL` default is the important half. **Anything the map does not know about is a bug in your service, and a bug is `INTERNAL` with no detail.** That is the correct default in both directions: the caller learns "this is not your fault, and retrying identically will probably fail the same way", and the message stays in the log where you can read it with a traceback.

## The map is a client contract, not a formatting decision

Adding this service's own errors is what makes the map worth having:

```text
    OrderNotFound     NOT_FOUND            'Resource not found'
    OrderAlreadyPaid  FAILED_PRECONDITION  'Failed precondition'
    RateLimited       RESOURCE_EXHAUSTED   'Resource exhausted'
    ConnectionError   UNAVAILABLE          'Service unavailable'
```

Each line is a statement about what the caller should do, and the code is the machine-readable half of it:

| Status | What the caller should do |
|---|---|
| `INVALID_ARGUMENT` | fix the request; never retry it unchanged |
| `NOT_FOUND` | the thing is not there; retrying will not create it |
| `FAILED_PRECONDITION` | the state is wrong; retry only after changing it |
| `PERMISSION_DENIED` / `UNAUTHENTICATED` | get a better token; do not retry with this one |
| `RESOURCE_EXHAUSTED` | back off, then retry — you are being rate limited |
| `UNAVAILABLE` | retry with backoff; a different replica may answer |
| `DEADLINE_EXCEEDED` | the call ran out of time; the work may or may not have happened |
| `ABORTED` | a concurrency conflict; retry at a higher level |
| `INTERNAL` | our bug; retrying identically is unlikely to help |

Two of these deserve care.

**`ConnectionError` as `UNAVAILABLE` is a choice with consequences.** It tells every client to retry, which is right when your database blipped and wrong when it has been down for an hour and the retries are what is keeping it down. It is the right code, and it is also the reason the client side needs a budget and a breaker rather than a bare retry count.

**`DEADLINE_EXCEEDED` does not say whether the work happened.** A write that times out may have been committed. That is why this code, more than any other, is the one that needs an idempotency key on the other side, and why "retry on `DEADLINE_EXCEEDED`" is only safe for operations that can be repeated.

The one to avoid is `ALREADY_EXISTS` for anything that is not a duplicate. It looks like a natural fit for "this order was already paid", and the client library that treats `ALREADY_EXISTS` as success — because it usually means "your create already worked" — will silently swallow it.

## Details: the two-tier rule

Safe messages per status are honest and useless: `Failed precondition` tells a caller nothing about *which* precondition. The fix is not to loosen the rule, it is to split the population:

```text
    ValueError        INVALID_ARGUMENT     'Request processing failed'
    ConnectionError   UNAVAILABLE          'Request processing failed'
    RuntimeError      INTERNAL             'Request processing failed'
    OrderNotFound     NOT_FOUND            'OrderNotFound: order 42'
    OrderAlreadyPaid  FAILED_PRECONDITION  'OrderAlreadyPaid: order 42 was paid at 09:12'
    RateLimited       RESOURCE_EXHAUSTED   'RateLimited: 100 requests per minute'
```

Domain errors your service defined carry their message, because you wrote that message for a caller and it contains nothing but domain facts. Everything else — including standard exceptions your code raised — gets a generic string, because their messages are written by libraries, drivers and the standard library, and none of those authors were thinking about your API's audience.

That is the rule worth writing down: **a message is publishable only if the type that carries it was defined by your service.** It is mechanical, it is checkable in review, and it fails safe when somebody adds an exception type and forgets to think about it.

For anything richer than a sentence, use gRPC's `error_details` rather than stuffing structure into the details string: a machine-readable payload in the trailing metadata is what a client can branch on, and it keeps the human string human.

<!-- diagram:concept -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">THE IDEA, VISUALIZED</span><strong>Choose the status and the public message separately</strong></figcaption>
<div class="bdr-diagram__viewport" markdown="1" data-search-exclude>

```mermaid
---
config:
  theme: default
  look: classic
  flowchart:
    useMaxWidth: false
    wrappingWidth: 150
    padding: 12
    nodeSpacing: 24
    rankSpacing: 32
---
flowchart TD
    accTitle: Choose the status and the public message separately
    accDescr: Domain errors can return a deliberate client-facing explanation. Unexpected internal exceptions need a generic response and detailed server-side reporting.
 E["Python exception"] --> M["Map to gRPC status"]
 E --> P{"Known public domain error?"}
 P -->|"Yes"| D["Safe domain details"]
 P -->|"No"| G["Generic details"]
 E -.-> L["Server-side logs and tracing"]
 M --> R["gRPC response"]
 D --> R
 G --> R
```

</div>
<p class="bdr-diagram__caption">Domain errors can return a deliberate client-facing explanation. Unexpected internal exceptions need a generic response and detailed server-side reporting.</p>
</figure>
<!-- /diagram:concept -->

## What belongs where

- **The map lives in the transport layer**, not in handlers. A handler that catches its own exception to choose a status has moved API design into business logic, and the next handler will choose differently.
- **The domain does not import `grpc`.** It raises `OrderNotFound`, which is also what an HTTP entrypoint over the same use case needs — the two-transport version of this is [the transport-independent errors post](2026-09-07-transport-independent-errors.md).
- **Deliberate aborts pass through untouched.** A handler that calls `context.abort` has already chosen its status, and the mapping layer must not rewrite it — nor should the error reporter treat it as a bug, which is [the interceptor ordering trap](2026-09-07-the-anatomy-of-a-production-grpc-server.md).
- **The log gets everything.** Type, message, traceback, correlation id. The whole point of a generic message on the wire is that the specific one is somewhere else.

## The pieces

The map, the safe messages and the detail factory are [grpc-server-kit](https://bedrock-python.github.io/grpc-server-kit/): an interceptor that takes your map merged into its defaults, replaces details with a safe string unless you say otherwise, logs the real exception with its traceback, and leaves deliberate aborts alone. The five standard exceptions it maps out of the box are a starting point; the map that matters is the one with your domain errors in it.

Eleven exceptions, two passwords, one map.
