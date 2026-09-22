# Lab: who creates the Kafka topic

Topic provisioning from [the article](../../posts/2026-09-13-kafka-in-python-services.md).
Docker must be running. Run from this directory in a repository checkout:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt topics_lab.py
```

The script imports the article code and helpers from the
[client lab](../2026-09-07-aiokafka-checklist/README.md); keep that sibling directory.
Its requirements pin aiokafka-foundation-kit 0.1.3, aiokafka 0.14.0 and testcontainers 4.15.0.
It creates and removes a `confluentinc/cp-kafka:7.6.0` broker in KRaft mode.
Broker-side automatic topic creation is disabled.

Assertions verify:

- `producer_lifecycle(topics=[...])` alone does not create the topic;
- adding `auto_create_topics=True` creates the requested topic;
- three concurrent calls to the article's provisioner all succeed with one three-partition topic;
- requesting six partitions on a later call leaves the existing three unchanged;
- asking one broker for three replicas raises `InvalidReplicationFactorError`;
- a valid topic before the rejected one remains created, while the following topic is not attempted.

The check waits for broker metadata after concurrent creation: acknowledgement of
`CreateTopics` can precede another client's view of the topic. It asserts the eventual
partition and replica counts rather than assuming an immediate metadata refresh.

`PASS` lines follow assertions against the real admin API. No library internals
are replaced. These checks cover creation, not reconciliation of partitions, retention,
permissions or replication on an existing production topic.
