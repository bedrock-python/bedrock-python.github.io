# Lab: Kafka clients, commits and redelivery {#lab-the-production-checklist-for-aiokafka}

Runnable examples from [the article](../../posts/2026-09-13-kafka-in-python-services.md).
Docker must be running. From this directory in a repository checkout, run:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt checklist_lab.py
```

`requirements.txt` pins aiokafka-foundation-kit 0.1.3, aiokafka 0.14.0 and
testcontainers 4.15.0. The script creates and removes its own
`confluentinc/cp-kafka:7.6.0` container in KRaft mode. Automatic broker-side topic
creation is disabled.

`kafka_flow.py` contains the article's eight Kafka snippets, including its handler,
consumer loop and shutdown wrapper. The ninth snippet, the servicewright adapter,
is in the [shutdown lab](../2026-09-07-kafka-consumer-shutdown/README.md).
`lab_support.py` provides the shared container and bounded reads.

Assertions verify:

- the published `ensure_topics_async()` creates a three-partition topic without patches;
- dictionaries arrive as JSON values, keys remain bytes, and one key stays in one partition;
- after five fetched records, position lag is zero while committed lag is still five;
- a handler failure after two effects leaves the batch uncommitted and all five records replay;
- the sample tracking view ignores repeated or older revisions;
- completing offsets 0–4 and manually committing 5 makes the replacement start at 5;
- periodic auto-commit can save 5 after five records are fetched but only two are processed;
- the library's connection probe returns true for the running broker.

The tracking view is an in-memory diagnostic effect, not durable application storage.
Replay checks create new consumers in the same group. The auto-commit case waits for
the real periodic commit while the consumer is open; it does not label a clean close a crash.
The connection check makes no claim about topic permissions or handler progress.

The focused public-API topic check can also run separately:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt topic_probe.py
```

Every `PASS` line follows assertions. This single-broker lab does not test replicated
durability or a live rebalance. Continue with [topic ownership](../2026-09-07-topics-on-startup/README.md)
and [shutdown](../2026-09-07-kafka-consumer-shutdown/README.md).
