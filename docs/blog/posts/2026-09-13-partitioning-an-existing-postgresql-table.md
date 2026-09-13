---
date: 2026-09-13
authors:
  - alex
categories:
  - Tutorials
tags:
  - pg-partsmith
  - postgresql
  - partitioning
  - uuid
---

# Partitioning an existing PostgreSQL table {#partitioning-an-existing-postgresql-table}

<div class="bdr-post__hero" data-bdr-post="2026-09-13-partitioning-an-existing-postgresql-table" role="img" aria-label="Adopt the old table as DEFAULT and drain it window by window while writes continue" markdown="0"></div>

Partitioning an existing table changes more than row storage. It affects uniqueness, foreign keys, query plans and writes during the transition. Before creating partitions, choose a key that can satisfy those constraints.

The migration should produce a predictable partition tree, verified data and an explicit application cutover.

<!-- more -->

<div id="uuidv7-as-a-postgresql-partition-key" data-search-exclude></div>
<div id="one-column-in-the-primary-key" data-search-exclude></div>
<div id="the-bounds-are-uuids" data-search-exclude></div>
<div id="pruning-happens-on-the-id-not-on-the-timestamp" data-search-exclude></div>
<div id="the-three-ids-that-do-not-fit" data-search-exclude></div>
<div id="retention-has-the-same-edge" data-search-exclude></div>
<div id="when-to-reach-for-it" data-search-exclude></div>

## Choose the key from queries and constraints {#keys}

Time ranges naturally suggest a timestamp column. A partitioned table's unique constraint generally must include every partition-key column. That can turn `PRIMARY KEY (id)` into a composite key and require changes to incoming foreign keys. See [PostgreSQL's partitioning restrictions](https://www.postgresql.org/docs/current/ddl-partitioning.html).

For suitable new data, another option is partitioning directly on UUIDv7. Bounds are then id values, and the unique key can remain one column. A predicate on a separate `created_at` column does not automatically prune partitions keyed on id: predicates must align with the partition key.

UUIDv7 is useful when its time ordering matches the data and query model. It does not transform existing random UUIDs or eliminate late-arriving records. Validate the choice with real `EXPLAIN` output and retention rules.

<div id="how-to-partition-an-existing-postgresql-table-without-rewriting-your-application" data-search-exclude></div>
<div id="step-1-the-primary-key-has-to-contain-the-partition-column" data-search-exclude></div>
<div id="step-2-the-swap" data-search-exclude></div>
<div id="step-3-the-first-maintenance-tick" data-search-exclude></div>
<div id="step-4-the-drain" data-search-exclude></div>
<div id="step-5-the-foreign-key-comes-back-composite" data-search-exclude></div>
<div id="step-6-the-empty-default-and-the-sequence" data-search-exclude></div>
<div id="the-result" data-search-exclude></div>
<div id="the-order-and-where-the-risk-is" data-search-exclude></div>
<div id="the-pieces" data-search-exclude></div>

## Design cutover separately {#cutover}

An ordinary table cannot simply be declared partitioned without structural work. Create a new parent and a path for moving or attaching existing data. One lab in this blog adopts the old table as DEFAULT and subsequently moves rows into ranges.

Before cutover, inventory incoming foreign keys, sequences, defaults, privileges, indexes, triggers and dependent views. Renaming tables alone does not guarantee that every dependency now references the intended parent.

DDL cutover requires locks. Rehearse with concurrent writes, limit lock waiting and define when to abandon an attempt. “Without changing application queries” does not mean zero interruption or an unchanged schema.

<!-- diagram:concept -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">THE IDEA, VISUALIZED</span><strong>A controlled transition to partitioning</strong></figcaption>
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
    accTitle: A controlled transition to partitioning
    accDescr: Keys and references are designed before cutover. The migration ends by checking rows, constraints and query plans.
    A["Choose partition key"]
    B["Prepare constraints"]
    C["Plan cutover"]
    D["Move data in batches"]
    E["Verify result"]
    A --> B --> C --> D --> E
```

</div>
<p class="bdr-diagram__caption">Keys and references are designed before cutover. The migration ends by checking rows, constraints and query plans.</p>
</figure>
<!-- /diagram:concept -->

## Move data in bounded batches {#movement}

Batch size bounds transaction duration, WAL volume and interference with live traffic. After each batch, identify completed work and how a restart resumes it.

Creating a range alongside DEFAULT needs care: rows belonging to that range may still reside in DEFAULT and prevent the new partition from being added. Movement, validation and attach order must respect the actual tree's constraints. An uncoordinated `INSERT ... SELECT` followed by deletion is not a general substitute when writes continue.

For large tables, compare a maintenance window, controlled copy-and-cutover or a dedicated synchronization approach. The right option depends on acceptable downtime and write intensity.

## Verify more than row counts {#verification}

Reconcile data and duplicates, restore and validate foreign keys, and check the sequence's next value. Verify defaults, permissions and important constraints, then run representative queries with `EXPLAIN`.

Also test writes outside prepared ranges. The application needs either an acceptable DEFAULT path or an expected, observable refusal. Regular [partition maintenance](2026-09-13-postgresql-partition-maintenance.md) follows the migration.

The labs retain transition and UUIDv7 examples. [pg-partsmith](https://bedrock-python.github.io/pg-partsmith/) helps maintain ranges; key selection, cutover design and reference validation remain migration responsibilities.

## Examples and labs {#labs}

The complete setups and reproduction instructions are available separately:

- [Lab: partitioning a live table](../lab/2026-09-07-partition-existing-table/README.md)
- [Lab: UUIDv7 as a PostgreSQL partition key](../lab/2026-09-07-uuidv7-partition-key/README.md)
