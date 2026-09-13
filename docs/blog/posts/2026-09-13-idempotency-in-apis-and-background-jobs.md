---
date: 2026-09-13
authors:
  - alex
categories:
  - Design
tags:
  - idempotency-kit
  - redis
  - idempotency
---

# Idempotency in APIs and background jobs {#idempotency-in-apis-and-background-jobs}

<div class="bdr-post__hero" data-bdr-post="2026-09-13-idempotency-in-apis-and-background-jobs" role="img" aria-label="The case that matters is the retry that arrives while the first request is still running" markdown="0"></div>

A client sends a request, loses the response and retries. A worker finishes a job but crashes before acknowledging it. Redelivery is normal in both cases; the risk is repeating the business action.

Idempotency begins by identifying that action. A key represents the intent to perform an operation, rather than a particular network attempt or message delivery.

<!-- more -->

<div id="idempotency-keys-the-part-everyone-gets-wrong" data-search-exclude></div>
<div id="what-the-key-promises" data-search-exclude></div>
<div id="measured-the-request-that-is-still-running" data-search-exclude></div>
<div id="it-is-still-not-a-lock" data-search-exclude></div>
<div id="the-key-is-not-the-request" data-search-exclude></div>
<div id="failures-are-not-cached-and-neither-is-the-store" data-search-exclude></div>
<div id="scope-and-lifetime" data-search-exclude></div>
<div id="the-shape" data-search-exclude></div>

## A result cache does not protect work in progress {#reservation}

“Check the cache, execute, save” admits two concurrent requests: both can observe a missing result. An atomic attempt to reserve the key must precede the action.

A record normally includes scope, key, parameter fingerprint and execution state. The winner performs the work. A duplicate with matching parameters receives the stored result, waits for a bounded time or learns that execution is still in progress. Reusing the key with different parameters should be rejected under an explicit contract.

A fingerprint does not replace authorization. Scope must separate users, tenants and different business operations so that another caller cannot retrieve a stored response.

<!-- diagram:concept -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">THE IDEA, VISUALIZED</span><strong>Reserve the key before the action</strong></figcaption>
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
    accTitle: Reserve the key before the action
    accDescr: The atomic reservation winner executes the action. A duplicate checks its parameters and receives a saved result or an in-progress response.
    A["Key and parameters"]
    B["Atomic reservation"]
    C["Execute action"]
    D["Save result"]
    E["Check fingerprint"]
    F["Return result or status"]
    A --> B
    B -->|"owner"| C --> D
    B -->|"duplicate"| E --> F
```

</div>
<p class="bdr-diagram__caption">The atomic reservation winner executes the action. A duplicate checks its parameters and receives a saved result or an in-progress response.</p>
</figure>
<!-- /diagram:concept -->

<div id="idempotency-across-a-chain-of-microservices" data-search-exclude></div>
<div id="the-shape-of-the-problem" data-search-exclude></div>
<div id="the-mistake-that-looks-like-a-fix" data-search-exclude></div>
<div id="the-key-belongs-to-the-request-not-to-the-attempt" data-search-exclude></div>
<div id="the-line-that-says-the-work-is-not-finished" data-search-exclude></div>
<div id="when-there-is-no-key-to-propagate" data-search-exclude></div>
<div id="what-to-standardise-across-the-chain" data-search-exclude></div>
<div id="the-pieces" data-search-exclude></div>

## Keep identity stable across attempts {#propagation}

In a gateway → orders → payments chain, minting a new key at each hop does not connect a repeated payment to the user's original intent. Create the key at the operation boundary and propagate it, or derive a stable key for a particular child action.

Sending an invoice and charging an order are different actions. They need different key scopes even when both use an order id. For a background job, identify the business action and its version rather than the delivery attempt.

Successful deduplication does not necessarily produce an immediate answer. While the first call is running, the API needs a way to retrieve its outcome: another request with the same key, a status endpoint or an operation identifier.

<div id="idempotency-for-background-jobs-and-kafka-consumers" data-search-exclude></div>
<div id="the-crash-before-the-ack" data-search-exclude></div>
<div id="two-workers-one-job" data-search-exclude></div>
<div id="what-the-key-is-made-of" data-search-exclude></div>
<div id="consumers-the-inbox-and-the-key-are-not-the-same-tool" data-search-exclude></div>
<div id="lifetime" data-search-exclude></div>

## Close the gap between effect and result recording {#effects}

A Redis reservation does not make an external payment atomic with saving its result. The process can complete the payment and crash before marking success. Another worker may acquire the key after the lease expires.

If the effect lives in the same database, the deduplication record and data change can share a transaction. An external provider needs its own stable idempotency key or an outcome reconciliation and recovery process. A local lock alone cannot promise that an email or payment happens once.

Lease duration and renewal must match the work. Expiry does not establish that the previous executor has stopped. This matters especially for long background jobs.

## Define retention and failure behavior {#failure-policy}

| Decision | Consider |
|---|---|
| Result TTL | Maximum retry, replay and queue recovery window |
| Incomplete record | Detecting and recovering interrupted operations |
| Action failure | Whether another attempt is safe and what callers receive |
| Store outage | Whether duplicate effects are acceptable without deduplication |
| Old-key cleanup | What a late retry will do |

Deleting a key on every exception is dangerous when an external effect may already have occurred. Continuing without the store is also dangerous when duplicates are unacceptable. Fail-open is an operation-specific decision.

## Test retries at inconvenient boundaries {#verification}

Exercise concurrent requests, parameter mismatch, lost responses, restart after the effect but before result recording, lease expiry and store failure. Sequentially repeating a completed operation tests only the easy case.

For Kafka, an [inbox](2026-09-13-reliable-events-outbox-inbox-kafka.md) protects transactional consumer effects inside the database. External actions remain a separate boundary. [idempotency-kit](https://bedrock-python.github.io/idempotency-kit/) coordinates keys; the system performing the effect still defines the complete contract.

## Examples and labs {#labs}

The complete setups and reproduction instructions are available separately:

- [Lab: idempotency keys](../lab/2026-09-07-idempotency-keys/README.md)
- [Lab: idempotency across a chain of services](../lab/2026-09-07-idempotency-across-a-chain/README.md)
- [Lab: idempotency for background jobs and consumers](../lab/2026-09-07-idempotency-for-jobs-and-consumers/README.md)
