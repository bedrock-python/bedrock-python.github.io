---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - aiokafka-foundation-kit
  - kafka
  - topics
  - operations
  - deployment
---

# Should your application create Kafka topics on startup?

<div class="bdr-post__hero" data-bdr-post="2026-09-07-should-your-application-create-kafka-topics-on-startup" role="img" aria-label="Three candidates can create the topic, and one of them makes a wrong one quietly" markdown="0"></div>

Somebody has to create the topic. The three candidates are the broker, doing it automatically the first time anyone mentions a name; the application, doing it at startup; and a person, doing it through whatever process owns the cluster. Each of the three has a failure that shows up weeks later, and the one everybody meets first is a topic with one partition and a typo in its name, quietly created by a producer, receiving all the traffic nobody is reading.

<!-- more -->

The numbers come from [the post's lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-topics-on-startup), against Kafka in a container with broker-side auto-creation on, which is the default in most development setups. Versions: aiokafka-foundation-kit 0.1.3, aiokafka 0.14.0, Python 3.13.

## What the broker does for you

```text
--- 1. nobody created it: a producer writes to a topic that does not exist
    send to ordrs.events-b4f0e5: accepted; the topic now exists with 1 partition(s)
--- 2. a consumer subscribes to a topic that does not exist
    subscribe to orders.events-46631c: no error; the topic now exists with 1 partition(s)
```

Both of those are convenience in development and a trap in production.

The producer wrote to `ordrs.events` — a typo — and got no error at all. The topic exists now, with the broker's default partition count, and every message goes into it. The consumer of `orders.events` is healthy, has no lag, and receives nothing. There is no error anywhere in the system, because from Kafka's point of view nothing went wrong: two topics exist and one of them has a subscriber.

The consumer case is the mirror image and slightly worse. Subscribing to a name that does not exist creates it, so a typo on the consumer side produces an empty topic that will never receive anything, and a consumer that waits forever without complaining.

And both created the topic with **one partition**, which is the cluster default and almost never what a real topic wants. Partition count is the parallelism limit for the consumer group: with one partition, exactly one member of the group can process at a time, no matter how many pods you run.

That is the case for turning broker-side auto-creation off in production, and it is a cluster-level decision made once. With it off, the two cases above become errors, which is what you want: a typo should fail loudly at the first send.

## What the application does

```text
--- 3. the application creates its topics at startup
    ensure_topics_async(num_partitions=6): exists with 6 partition(s)
```

Now the shape is a decision in the codebase, next to the code that produces to it, in the same review, released with the same deploy. That is the strongest argument for application-side creation: the topic and the code that uses it change together, and a new service does not need a ticket to somebody else's queue before it can run.

The costs come next.

## The shape is decided once, forever

```text
--- 4. the next deploy asks for a different shape
    ensure_topics_async(num_partitions=12) on the same topic: exists with 6 partition(s)
```

The second call did not fail and did not change anything. Creation is idempotent in the sense that matters for startup — an existing topic is fine, the service starts — but it is not a reconciliation loop. The declaration in your code now says twelve and the cluster says six, and nothing will ever tell you.

That is the right behaviour for a library. Adding partitions to a live topic changes which partition a key hashes to, which breaks per-key ordering for every key that moves, and no library should do that as a side effect of a deploy. But it means the number in your code is documentation after the first deploy, not configuration. If it matters, check it: a startup check that compares the declared partition count with the real one and logs loudly on a mismatch costs one admin call and turns a silent drift into a line in the log.

## Three replicas start at the same time

```text
--- 5. three replicas start at the same moment
    replica 1: started
    replica 2: started
    replica 3: started
    the topic exists with 3 partition(s)
```

A rollout starts every pod at once, and every pod runs the same creation code. One of them creates the topic; the others get "topic already exists" and treat it as success. This has to be explicitly true in the implementation — an unhandled `TopicAlreadyExistsError` would crash two pods out of three on every cold start of a new topic — and it is the reason creation must never be "check, then create", which is a race with itself.

## A shape the cluster cannot give you

```text
--- 6. a shape the cluster cannot honour
    replication_factor=3 on a one-broker cluster: InvalidReplicationFactorError:
    Replication factor: 3 larger than available brokers: 1
    the topic does not exist
```

The service does not start. That is correct — a topic with a replication factor of one in a cluster that is supposed to give you three is a data-loss configuration you would rather not discover during an incident — and it is also the failure mode that makes application-side creation feel dangerous: a wrong number in a config file becomes a service that will not boot.

The mitigation is the same as for any startup-time validation: it fails in the first environment the deploy touches, not in production, provided the environments have the same broker count. When they do not, and they often do not, the replication factor belongs in per-environment settings rather than in code.

## So, should it?

**Yes, when** the service owns the topic, the topics are per-service rather than shared contracts between teams, and the environments are similar enough that a shape valid in one is valid in all. The convenience is real: a new topic is a code change, and a fresh environment is one deploy away from working.

**No, when** the topic is a contract between teams, the cluster is managed by somebody with capacity plans and quotas, or the partition count is a decision with cost implications you are not the one making. In that case the application should *check* rather than create: assert at startup that its topics exist with the shape it expects, and refuse to start when they do not. That is the same failure mode as creation with a bad shape, minus the authority to write to somebody else's cluster.

**Either way**, turn broker-side auto-creation off in production, keep the declaration in code even if a person applies it, and check the shape at startup rather than assuming it. The check is what catches the topic somebody created by hand last year with one partition.

## The pieces

The creation above is [aiokafka-foundation-kit](https://bedrock-python.github.io/aiokafka-foundation-kit/): a `TopicConfig` per topic, `ensure_topics_async` that creates each one and treats an existing topic as success, and a producer lifecycle that can run it before the producer starts — behind two separate arguments, so that "I have topics" and "create them" stay different statements. It never reshapes an existing topic, for the reason in the fourth section.

The typo'd topic with one partition is not a hypothetical. It is the most common Kafka incident I have seen, and it takes a cluster setting to make it impossible.
