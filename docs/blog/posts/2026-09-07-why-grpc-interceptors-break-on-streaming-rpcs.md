---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - grpc-client-kit
  - grpc
  - interceptors
  - observability
  - asyncio
---

# Why gRPC interceptors break on streaming RPCs

<div class="bdr-post__hero" data-bdr-post="2026-09-07-why-grpc-interceptors-break-on-streaming-rpcs" role="img" aria-label="The wrapper closes before the stream has produced anything" markdown="0"></div>

An interceptor that times a call, counts its errors and binds a request id is twenty lines, and it works. Then somebody adds a server-streaming method and the same twenty lines start lying: the latency histogram reports zero milliseconds for a call that took six hundred, the error counter stays at zero while the stream fails, and the request id is gone by the time the first item arrives. Nothing raises. The dashboards just quietly stop describing reality.

<!-- more -->

The numbers come from [the post's lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-grpc-interceptors-and-streams), an in-process gRPC server with all four RPC kinds. Versions: grpc-client-kit 0.1.2, grpcio 1.83.1, Python 3.13.

## The interceptor that is registered for one kind out of four

Before the measuring problem there is a registration problem, and it is silent.

`grpc.aio` has four client interceptor base classes, one per RPC kind. The obvious thing to write is one class that inherits all four and implements all four methods. Here is what the channel does with it:

```text
    one object inheriting all four ABCs, channel lists: unary_unary=1, unary_stream=0,
                                                        stream_unary=0, stream_stream=0
    unary_unary    intercept ran 1 time(s)
    unary_stream   intercept ran 0 time(s)
    stream_unary   intercept ran 0 time(s)
    stream_stream  intercept ran 0 time(s)
```

The channel sorts interceptors into four lists with an `if`/`elif` chain, so an object that satisfies all four checks lands in the first list only. Your interceptor is registered for unary-unary and nothing else. No error, no warning; the other three methods you wrote are dead code.

Four objects, one base class each, and the same four methods are registered where you expected:

```text
    four objects, one ABC each, channel lists: unary_unary=1, unary_stream=1,
                                               stream_unary=1, stream_stream=1
```

This is worth knowing before anything else, because it means the streaming bugs below are usually *discovered* later than they are introduced: the interceptor was never running on streams in the first place.

## What a unary interceptor measures on a stream

Now the interceptor is registered properly. Here is the shape everyone writes, because it is the shape that is correct for unary calls:

```python
async def intercept_unary_stream(self, continuation, details, request):
    token = REQUEST_ID.set("req-42")
    started = time.perf_counter()
    try:
        return await continuation(details, request)
    except grpc.aio.AioRpcError:
        self.errors += 1
        raise
    finally:
        self.measured_ms = (time.perf_counter() - started) * 1000
        REQUEST_ID.reset(token)
```

Against a five-item stream sent 120 milliseconds apart, and then against the same stream failing at the third item:

```text
    unary-style wrapper, healthy stream: it measured 0 ms
      the caller waited 609 ms for 5 items; request id during the stream: None
    unary-style wrapper, failing stream: it counted 0 errors, measured 0 ms
      the caller waited 245 ms, got 2 items and then UNAVAILABLE: report generator died at item 3
```

Three separate failures in one interceptor, and all of them have the same cause: for a streaming response, `continuation` returns as soon as the *call object* exists. The RPC has not happened yet. It happens later, while the consumer iterates.

- **The duration is zero.** It measured how long gRPC took to construct a call object, and called that the latency of a 609-millisecond RPC. On a dashboard this is worse than no metric: it says the streaming endpoint is the fastest thing in the service.
- **The error is invisible.** The stream failed mid-way, the caller got `UNAVAILABLE`, and the interceptor's `except` never ran, because the exception is raised inside the consumer's `async for`, in a different stack. The error counter says zero while the calls fail.
- **The context is gone.** The `finally` reset the request id before the first item arrived, so every log line the consumer writes while processing the stream has no request id on it. The one place you would most want the correlation, a long-running stream, is the one place it is missing.

## Doing it by hand

The fix, written directly, is to wrap the returned call so that the interceptor's work spans the iteration rather than the setup:

```python
async def intercept_unary_stream(self, continuation, details, request):
    started = time.perf_counter()
    call = await continuation(details, request)

    async def wrapped():
        token = REQUEST_ID.set("req-42")
        try:
            async for item in call:
                yield item
        except grpc.aio.AioRpcError:
            self.errors += 1
            raise
        finally:
            self.measured_ms = (time.perf_counter() - started) * 1000
            REQUEST_ID.reset(token)

    return wrapped()
```

Same lab, same server:

```text
    stream-aware wrapper, healthy stream: it measured 608 ms
      the caller waited 608 ms for 5 items; request id during the stream: 'req-42'
    stream-aware wrapper, failing stream: it counted 1 errors, measured 244 ms
```

608 against 609, one error for one failure, and the request id is visible while the items arrive. That last one works because an async generator runs in its caller's context, so the `set` leaks into the consumer's context on purpose, and the `reset` happens when the generator finishes.

This is the right idea and it is also where the hand-written version starts to accumulate obligations. The wrapper has to handle a consumer that abandons the stream half way, or the `finally` runs at garbage collection time, if ever. It has to not swallow `GeneratorExit`. It has to do something sensible when the underlying call is cancelled. And it has to be written four times, once per RPC kind, with the stream-unary case being different again: there the *request* is the iterator and the outcome arrives after the interceptor has returned.

## The four kinds, one implementation

What I want to write is the thing that reads like the unary version and behaves correctly for all four. That is what a logical interceptor is for: one `around_call` that yields exactly once, where the yield is the whole RPC.

```python
class Observability(AsyncAroundClientInterceptor):
    async def around_call(self, call: ClientCall):
        started = time.perf_counter()
        try:
            yield                       # the whole RPC, response stream included
        except grpc.aio.AioRpcError:
            self.errors += 1
            raise
        finally:
            self.measured[call.method] = (time.perf_counter() - started) * 1000
```

One class, expanded into the four channel entries the `if`/`elif` chain needs:

```text
    flatten_interceptors([one logical interceptor]) -> 4 channel entries
    channel lists: unary_unary=1, unary_stream=1, stream_unary=1, stream_stream=1
    unary_unary    around_call ran 1 time(s)
    unary_stream   around_call ran 1 time(s)
    stream_unary   around_call ran 1 time(s)
    stream_stream  around_call ran 1 time(s)
    measured /lab.Reports/Get       123 ms
    measured /lab.Reports/Stream    608 ms
    measured /lab.Reports/Chat      367 ms
    measured /lab.Reports/Upload      1 ms
```

Every kind runs once, and the streaming durations are the real ones: 608 milliseconds for the five-item stream, not zero. The mid-stream failure reaches the `except` as an ordinary `AioRpcError`:

```text
    failing stream: around_call counted 1 errors, measured 246 ms
```

And the caller still holds a real call afterwards. This is the check people forget when they hand-roll the wrapper, because returning a plain async generator can cost the caller `code()`, `details()` and `trailing_metadata()`:

```text
    no interceptor               code()='OK'; details()=''; trailing_metadata()=Metadata(())
    the kit's around interceptor code()='OK'; details()=''; trailing_metadata()=Metadata(())
```

## The part that only shows up on streams

There is one more asymmetry, and it is the reason this post exists as a design post rather than a tip.

For a unary call, the setup, the RPC and the teardown all happen in one coroutine, in one task, in one context. For a response stream they do not: the teardown runs whenever the stream ends, in whichever task drained it. So an interceptor that acquires something before the yield and releases it after — a `ContextVar` token, an OpenTelemetry context, a semaphore — is doing something subtler than it looks. A `ContextVar` token minted in one context cannot be reset in another; `contextvars` refuses it.

The kit pins one context per call and runs both halves inside it, so the ordinary spelling works on every kind:

```text
--- an around_call that sets a ContextVar before the yield and resets it after
    unary_unary    caller got the response
    unary_stream   caller got the response
    stream_unary   caller got the response
    stream_stream  caller got the response
```

The second guarantee is about what happens when the teardown itself fails, which is not hypothetical: a metrics push, a log write, an exporter that is down.

```text
--- any teardown that raises, per RPC kind
    unary_unary    caller got the response
    unary_stream   caller got the response
    stream_unary   caller got the response
    stream_stream  caller got the response
```

Every kind: the response still arrives, and the teardown's exception is logged rather than delivered. An observability layer must not be able to turn a successful RPC into an error in the caller's hands, and it must not do it for two of four kinds and not the others.

## What to check in your own interceptors

- **How many of the four kinds is it registered for?** One class inheriting all four ABCs is registered for one.
- **Where does the duration stop?** If it stops when `continuation` returns, it measures nothing for a streaming response.
- **Where would a mid-stream failure surface?** Not in the `try` around `continuation`.
- **Does any context you set survive to the consumer?** And can the token be reset where you reset it?
- **What does the caller hold afterwards?** If you wrapped the call in a generator, they may have lost `code()` and `trailing_metadata()`.
- **What happens if the interceptor's own bookkeeping raises?** The caller should never find out.

## The pieces

The `around_call` seam is [grpc-client-kit](https://bedrock-python.github.io/grpc-client-kit/), which also ships the layers most services would otherwise write against it: logging, tracing, metrics, timeouts, retries and a circuit breaker, in a fixed order, expanded into the four channel entries by `flatten_interceptors`. The two guarantees in the last section — a shared context across the yield, and a teardown that cannot change the outcome — landed in 0.1.2, because this lab is what found their absence.

A zero-millisecond histogram on your fastest endpoint is not good news. It is an interceptor measuring the wrong thing.
