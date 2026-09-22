# Lab: Kafka consumer shutdown and replay {#lab-graceful-kafka-consumer-shutdown-in-kubernetes}

Shutdown scenarios from [the article](../../posts/2026-09-13-kafka-in-python-services.md).
Docker must be running. From this directory in a repository checkout, run:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt driver.py
```

Requirements include the [client lab's](../2026-09-07-aiokafka-checklist/README.md)
aiokafka-foundation-kit 0.1.3, aiokafka 0.14.0 and testcontainers 4.15.0,
plus servicewright 0.13.1. Keep that sibling directory: it contains `kafka_flow.py`
and the container helpers. The driver creates and removes a single
`confluentinc/cp-kafka:7.6.0` broker in KRaft mode.

| File | Role |
| --- | --- |
| `consumer_common.py` | Imports shared code and supplies minimal servicewright settings and container |
| `consumer_naive.py` | Runs the batch loop that the driver cancels halfway through |
| `consumer_service.py` | Connects the article's bounded loop to `DaemonEntrypoint` |
| `driver.py` | Produces ten records and checks all three interruption scenarios |

After the second handler effect, the driver cancels the task, sets a stop event,
or sets the event while blocking further work until the drain budget expires.
Synchronization uses events rather than guessing when a batch is in flight.

| Scenario | Completed effects | Committed offset | Replacement's first offset |
| --- | --- | --- | --- |
| Cancel current processing | 0, 1 | None | 0 |
| Set stop and finish the accepted batch | 0–4 | 5 | 5 |
| Set stop, exhaust the drain budget | 0, 1 | None | 0 |

Assertions read the actual group offset and start a new consumer in the same group.
The two service cases run through `Service.run(..., stop=event)`. A `TimeoutError`
from budget expiry must propagate; the test does not accept a silently successful exit.
The timeout is implemented in `run_tracking()`: `DaemonEntrypoint.drain()` alone does
not limit time spent in its arbitrary daemon function.

This is an event/task-cancellation test, not a SIGTERM, hard-kill or Kubernetes rollout test.
It works on Windows as well as Unix. The effect is an in-memory tracking view;
durable database effects and replication need separate tests.

`consumer_service.py` can also run as a process with `KAFKA` set to a bootstrap address
and optional `GROUP` (default `tracking`), after provisioning `delivery.status`.
Its `run_sync()` path enables servicewright's normal signal handling; the driver uses
the explicit stop-event path to make the assertions reproducible.
