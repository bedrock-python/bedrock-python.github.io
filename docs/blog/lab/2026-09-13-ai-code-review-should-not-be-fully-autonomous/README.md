# Lab: verify a review finding before publishing it {#lab-review-evidence}

Example for [Why AI review findings need verification](../../posts/2026-09-13-ai-code-review-should-not-be-fully-autonomous.md). A retry creates duplicate reservations when the warehouse commits the first operation but loses its reply.

## Run {#run}

With uv installed, run from the website repository root:

```bash
cd docs/blog/lab/2026-09-13-ai-code-review-should-not-be-fully-autonomous
uv run --no-project --python 3.13 python reproduce.py before
uv run --no-project --python 3.13 python reproduce.py after
uv run --no-project --python 3.13 python test_review.py
```

Run the reproduction commands separately if your shell stops on an unsuccessful command. `before` **intentionally exits with status 1**, prints `calls=2, reservations=2` and fails the one-reservation assertion. `after` exits successfully with `calls=1, reservations=1`. The seven-test suite should pass. It verifies the broken implementation's observed behavior as well as the correction.

Only Python 3.13 and the standard library are used. uv may download Python if it is not cached; the example itself needs no network, Docker, model provider or access token. It posts no comments and does not run mr-review.

## Contract and limits {#contract}

`warehouse.reserve(order_id)` is an application adapter. In this scenario every accepted call creates a new reservation: there is no deduplication by order ID. A timeout may happen before or after the write. `WarehouseStub` deliberately injects those two failure positions and records calls and reservations in memory. It models the control flow; it does not test a real HTTP transport, database or warehouse service.

`reserve_with_retry` makes at most two attempts. After a lost reply, the second attempt can create another reservation even if the caller sees success. `reserve_once` makes one attempt and converts `TimeoutError` to `ReservationOutcomeUnknown`, preserving the order ID and cause. Both success and unrelated errors retain their ordinary behavior.

An unknown outcome is not a failed reservation. The caller needs a status-check or reconciliation process and must not blindly retry this exception at a higher layer. That process, durable idempotency and concurrent calls are outside this small example. A real review must establish the actual receiver's contract before applying the finding.

## Checks {#checks}

The suite covers an ordinary success, a duplicate after a lost reply, the two-attempt limit, the fixed behavior for timeouts before and after the write, successful return values and an unrelated permission error. It does not score AI model quality; the article's findings are illustrative.

## Files {#files}

- `reservation.py`: implementations before and after the review correction.
- `warehouse_stub.py`: controllable outcomes and recorded side effects.
- `reproduce.py`: the same one-reservation assertion for either implementation.
- `test_review.py`: seven executable checks for the finding and correction.
