# Lab: a documentation contract for a shipping quote {#lab-documentation-contract}

This page is a compact task-specific brief for the [documentation article](../../posts/2026-09-07-documentation-for-ai-coding-agents.md). It describes the API the example uses, its application dependencies and how to verify the result. It is not the library's complete API reference.

## Environment and scope {#scope}

| Item | Contract |
|---|---|
| Package | `deadline-budget==0.1.3` |
| Imports | `from deadline_budget import BudgetContext, DeadlineExceededError` |
| Example runtime | Python 3.13; `asyncio.timeout()` requires Python 3.11+ |
| Library methods | Synchronous; they return values or raise exceptions without `await` |
| Library responsibility | Track remaining time and calculate per-call timeout values |
| Cancellation | The application uses `asyncio.timeout()`; the budget alone cancels nothing |

The application checks stock and then obtains a shipping quote under one 600 ms budget. Each step has a 400 ms cap. No stock means `None`; otherwise return the shipping adapter's result.

`stock` and `shipping` are application-provided async callables, not deadline-budget clients. Both accept `(sku, *, timeout)` with seconds as the timeout unit. `stock` returns an integer count; `shipping` returns a quote. Production adapters must apply the passed timeout and propagate cancellation. The lab supplies controlled in-process substitutes; it does not test an HTTP SDK or a deployed warehouse.

## API used here {#api}

- `BudgetContext.create(total_seconds, call_caps=None, *, min_timeout=0.1, safety_margin=0.0)` returns `BudgetContext` synchronously.
- `ctx.remaining()` returns seconds as a float; it may be negative after expiry.
- `ctx.timeout_for_call(call_name, reserve_for_next=0.0)` returns seconds or raises `DeadlineExceededError` when the budget is already exhausted.
- An unknown `call_name` has no configured cap. Spelling mistakes do not raise a configuration error.
- The default minimum is 100 ms and can exceed the time remaining. This example explicitly uses `min_timeout=0` and a separate operation timeout.

## Working example {#wiring}

```python
import asyncio

from deadline_budget import BudgetContext


async def shipping_quote(sku, *, stock, shipping):
    ctx = BudgetContext.create(
        total_seconds=0.6,
        min_timeout=0,
        call_caps={"stock": 0.4, "shipping": 0.4},
    )
    async with asyncio.timeout(ctx.remaining()):
        available = await stock(sku, timeout=ctx.timeout_for_call("stock"))
        if available <= 0:
            return None
        return await shipping(sku, timeout=ctx.timeout_for_call("shipping"))
```

One context is created per invocation and reused for both steps. `DeadlineExceededError` means a budget calculation refused to start more work. `TimeoutError` can come from the operation timeout or a downstream adapter; this example propagates both error types to its caller. Blocking code and code that suppresses cancellation can overrun the asyncio timeout.

## Run the checks {#run}

With uv installed, run from the website repository root:

```bash
cd docs/blog/lab/2026-09-07-documentation-for-ai-coding-agents
uv run --no-project --python 3.13 --with-requirements requirements.txt python test_contract.py
```

The standard-library test suite checks the pinned version and public defaults, the expected error when awaiting a synchronous method, shared budget arithmetic, a missing cap, no-stock behavior, exhaustion before the next step, and the distinction between calculation and cancellation. It also compares the Python block above with `shipping.py` by syntax tree, so changing only one copy fails the check.

Most timing cases replace only the library module's clock with a manually advanced clock. Asyncio retains its real clock. A separate stalled-call test verifies actual cancellation by the 600 ms operation timeout, with a five-second watchdog. No exact wall-clock duration is asserted.

No Docker, external service or API key is needed. Network access is needed only to download Python or the pinned package if absent from the cache. A failed assertion exits with an error. These tests verify documentation and code; they do not measure an AI model's performance.

## Files and further reading {#files}

- `shipping.py`: the application function shown on this page.
- `test_contract.py`: executable assertions for the code and documentation.
- `requirements.txt`: the package version used by the example.
- [deadline-budget agent guide](https://github.com/bedrock-python/deadline-budget/blob/master/docs/agents.md): the broader library API; match it to the version you install.
- [The deadline article](../../posts/2026-09-06-timeouts-are-not-deadlines.md): request propagation and client integration.
