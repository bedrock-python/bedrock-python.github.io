---
date: 2026-09-13
authors:
  - alex
categories:
  - Design
tags:
  - omni-box
  - kafka
  - outbox
  - inbox
  - postgresql
---

# Reliable event delivery with Outbox, Inbox and Kafka {#reliable-events-outbox-inbox-kafka}

<div class="bdr-post__hero" data-bdr-post="2026-09-13-reliable-events-outbox-inbox-kafka" role="img" aria-label="Two systems, two commits, no shared transaction: close each window one at a time" markdown="0"></div>

A service saves an order in PostgreSQL and needs to publish it through Kafka. The process can fail between commit and publication. Reversing the order creates the opposite risk: the event exists, but the database transaction rolls back.

Outbox and Inbox make these boundaries explicit. They retain redelivery as an expected part of processing.

<!-- more -->

<div id="the-transactional-outbox-pattern-in-python-omni-box" data-search-exclude></div>
<div id="the-dual-write-problem" data-search-exclude></div>
<div id="the-outbox-pattern" data-search-exclude></div>
<div id="using-omni-box" data-search-exclude></div>
<div id="the-inbox-side" data-search-exclude></div>
<div id="why-a-library" data-search-exclude></div>

## Record intent with the business data {#outbox}

Write an outbox row, including a stable event id and payload, in the order transaction. The transaction has one outcome: both records exist or neither does. An outbox repository must not independently commit the caller's transaction.

A separate relay selects pending rows, publishes them and records the outcome. If it crashes after Kafka acknowledges but before the database update, publication repeats. The event id therefore survives retries, and consumers need to recognize duplicates.

Parallel relays need a work-claiming protocol. Claims, ownership expiry, recovery and completion must agree; selecting the first N rows alone is insufficient.

<!-- diagram:concept -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">THE IDEA, VISUALIZED</span><strong>Atomicity on each side of delivery</strong></figcaption>
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
    accTitle: Atomicity on each side of delivery
    accDescr: The producer commits its data with the outbox. The consumer commits its effect with the inbox; delivery between them may repeat.
    A["Data and outbox in one transaction"]
    B["Relay"]
    C["Kafka"]
    D["Inbox and effect in one transaction"]
    E["Acknowledge processing"]
    A --> B --> C --> D --> E
```

</div>
<p class="bdr-diagram__caption">The producer commits its data with the outbox. The consumer commits its effect with the inbox; delivery between them may repeat.</p>
</figure>
<!-- /diagram:concept -->

<div id="transactional-inbox-the-other-half-of-the-outbox-pattern" data-search-exclude></div>
<div id="the-consumers-two-problems" data-search-exclude></div>
<div id="the-inbox-row" data-search-exclude></div>
<div id="measured-the-handler-fails-halfway" data-search-exclude></div>
<div id="what-the-inbox-does-not-do" data-search-exclude></div>
<div id="the-pair" data-search-exclude></div>

## Commit processing with its effect {#inbox}

The consumer begins a transaction, attempts to record the message id in an inbox, applies the business change and commits both. A unique constraint distinguishes new delivery from completed processing.

Broker acknowledgement follows commit. A crash between them causes redelivery, which finds the inbox row and does not repeat the transactional effect. A handler failure before commit rolls back both the effect and its marker.

Identity must include the logical recipient: independent handlers of one event need not share a deduplication record. Inbox retention must cover possible replay, not just ordinary delivery delays.

<div id="exactly-once-is-a-lie-exactly-once-effects-are-not" data-search-exclude></div>
<div id="messages-versus-effects" data-search-exclude></div>
<div id="every-window-measured" data-search-exclude></div>
<div id="the-outbox-closes-the-producer-side" data-search-exclude></div>
<div id="the-inbox-closes-the-consumer-side" data-search-exclude></div>
<div id="the-http-edge" data-search-exclude></div>
<div id="the-whole-path" data-search-exclude></div>
<div id="why-the-library-must-not-own-the-transaction" data-search-exclude></div>
<div id="what-it-looks-like" data-search-exclude></div>

## Name the guarantee's boundary {#boundaries}

An inbox protects changes included in its transaction. PostgreSQL rollback cannot undo a sent email or external payment. Those actions need their own [idempotency contract](2026-09-13-idempotency-in-apis-and-background-jobs.md).

Kafka supports transactional scenarios within its ecosystem, but those guarantees do not automatically extend to an arbitrary external database. See [Kafka's delivery semantics](https://kafka.apache.org/41/design/design/#message-delivery-semantics).

A useful system property is specific: repeating this event id does not create a second invoice row in this database. “Everything is exactly-once” hides conditions that must be checked during failure.

<div id="what-happens-when-kafka-is-down-for-an-hour" data-search-exclude></div>
<div id="publishing-from-the-request-path" data-search-exclude></div>
<div id="the-outbox-during-the-outage" data-search-exclude></div>
<div id="what-an-hour-actually-costs-you" data-search-exclude></div>
<div id="what-it-does-not-solve" data-search-exclude></div>
<div id="the-pieces" data-search-exclude></div>

## A broker outage creates a backlog {#outage}

While Kafka is unavailable, the application may continue committing business data and outbox rows if the product contract permits it and database capacity allows. The event is durable but not delivered. The UI must not represent an unfinished external process as complete.

Backlog size grows approximately with arrival rate multiplied by outage duration. Recovery requires relay throughput above the rate of new work. Bound retries and monitor oldest-event age, queue size and messages that cannot be processed.

Ordering also needs a decision. Multiple relays and repeated publication can change observed order. Entities that depend on ordering need suitable partition keys and a verified version or sequence protocol.

## Test every interruption point {#verification}

Exercise failure before commit, after commit before publication, after publication before marking completion, and after the consumer effect before acknowledgement. Include long outages, backlog recovery and replay after inbox cleanup.

[omni-box](https://bedrock-python.github.io/omni-box/) provides outbox and inbox components. Integration begins with application transaction boundaries: where intent is stored, where an effect commits and exactly what an acknowledgement means.

## Examples and labs {#labs}

The complete setups and reproduction instructions are available separately:

- [Lab: exactly-once effects](../lab/2026-09-07-exactly-once-effects/README.md)
- [Lab: the transactional inbox](../lab/2026-09-07-transactional-inbox/README.md)
- [Lab: what happens when Kafka is down for an hour?](../lab/2026-09-07-when-kafka-is-down/README.md)
