---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - pg-partsmith
  - postgresql
  - partitioning
  - uuid
  - database
---

# UUIDv7 as a PostgreSQL partition key

Range-partitioning a table by time normally costs you the primary key: PostgreSQL requires every unique constraint to contain the partition column, so `PRIMARY KEY (id)` becomes `PRIMARY KEY (id, created_at)`, and every foreign key pointing at the table has to carry the timestamp too. A time-ordered id removes the problem instead of working around it. UUIDv7 puts 48 bits of Unix milliseconds in its leading bits, so the id *is* the time axis, and a table keyed by one can be partitioned on the key it already has.

<!-- more -->

The numbers come from [the post's lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-uuidv7-partition-key), against PostgreSQL 17 in a container. Versions: pg-partsmith 1.5.0, Python 3.13.

## One column in the primary key

```text
    CREATE TABLE events (id UUID PRIMARY KEY, ...) PARTITION BY RANGE (id): accepted
    the same table partitioned by created_at with PRIMARY KEY (id):
      FeatureNotSupportedError: unique constraint on partitioned table must include all
      partitioning columns
```

That is the entire argument in two lines. Partition on a timestamp and the key spreads: composite primary key, composite foreign keys in every referencing table, and application code that has to carry the timestamp everywhere it used to carry an id. Partition on a UUIDv7 and nothing changes above the schema — `WHERE id = $1` still finds one row, and a referencing table still stores one column.

## The bounds are UUIDs

The window boundaries are ordinary UUID literals, computed from the month's instants:

```text
    events__2026_07  FOR VALUES FROM ('019f1af9-b400-7000-8000-000000000000')
                     TO ('019fba9e-d800-7000-8000-000000000000')
    events__2026_08  FOR VALUES FROM ('019fba9e-d800-7000-8000-000000000000')
                     TO ('01a05a43-fc00-7000-8000-000000000000')
    events__2026_09  FOR VALUES FROM ('01a05a43-fc00-7000-8000-000000000000')
                     TO ('01a0f4c2-c400-7000-8000-000000000000')
```

Each bound is the *smallest* UUIDv7 for its instant: the timestamp bits, the version and variant bits, and every random bit zero. Using the minimum on both ends is what makes the windows exactly contiguous — one month's upper bound is the next month's lower bound, so there is no id that falls between two partitions.

Rows route by their own key, with no trigger and no `created_at` to keep in step:

```text
    an id generated this month      -> inserted
    an id generated last month      -> inserted
    an id generated two months ago  -> inserted
    events__2026_07  1 row(s)
    events__2026_08  1 row(s)
    events__2026_09  1 row(s)
```

That last part matters more than it sounds. With a separate timestamp column, the partition key and the id are two facts that can disagree: a backfill that sets `created_at` from an import file, a row whose timestamp is updated later, a default of `now()` that fires at insert rather than at the event. With UUIDv7 there is one fact, decided when the id was minted.

## Pruning happens on the id, not on the timestamp

```text
    WHERE id >= <first uuid7 of last month> AND id < <first uuid7 of this month>:
      1 partition(s): events__2026_08
    WHERE created_at >= <last month> AND created_at < <this month>:
      4 partition(s): events__2026_07, events__2026_08, events__2026_09, events__2026_10
    WHERE id = <one id>:
      1 partition(s): events__2026_07
```

The first line is the win: a time range, expressed as an id range, reads one partition. The third is the everyday case, a lookup by id, which prunes to exactly one partition without anybody thinking about it.

The second line is the tax, and it is the thing to design around. The `created_at` column is still there and still honest, and the planner cannot use it for pruning, because it is not the partition key. Every query written the obvious way — a date range on a timestamp column — scans every partition.

So a table keyed this way needs the conversion to exist somewhere the application actually uses: a helper that turns an instant into the smallest UUIDv7 for it, and queries written as `id >= from_time(a) AND id < from_time(b)`. It is two functions and a habit, and if it is not there, the partitioning quietly does nothing for reads.

## The three ids that do not fit

```text
    an id from a year ago (imported history):        CheckViolationError: no partition of
                                                     relation "events" found for row
    an id from three months ahead (a clock that is wrong): the same
    a uuid4 from a client that did not get the memo:       the same
```

Each of these is the same PostgreSQL error and a different operational story.

**Imported history.** Migrating old rows means minting ids whose timestamps are old, which means partitions for months you were never going to create. The fix is to create them deliberately before the import, and to know that retention will eventually decide they are expired.

**A clock that is wrong.** If ids are generated on the machines that write them, the partition an insert needs is chosen by that machine's clock. A host three months ahead writes into a window `create_ahead` has not built, and its inserts fail. A host slightly ahead — seconds, at a month boundary — writes into the next month's partition, which is why `create_ahead` is never zero.

**A `uuid4` from somewhere.** A random UUID has no timestamp; its leading bits are noise, so it lands wherever those bits point, which is almost always outside every window. This is the one that arrives as a surprise in production, because it usually comes from a client library, a test fixture or a service that was never told the id format matters. Generating ids in one place, server-side, is the defence.

The general shape: **with UUIDv7 as the partition key, id generation is part of the schema contract.** Anything that can mint an id can decide which partition a row wants, and a wrong id is a failed insert rather than a misplaced row. That is the right failure mode, and it is still a failure mode you have to design for.

## Retention has the same edge

```text
    created=0 detached=1 dropped=1 issues=0
    events__2026_08  1 row(s)
    events__2026_09  1 row(s)
    an id for 2026-07, the month retention just retired:
      CheckViolationError: no partition of relation "events" found for row
```

Once retention retires a window, a late row for it has nowhere to go. That is true of any time-partitioned table; it is sharper here because the row's window comes from an id that may have been generated long before the row is written — a queued job, a retried request, a message that sat in a dead-letter topic for a week. Retention older than your longest possible delivery delay is the rule, and the delay to measure is the one from id generation to insert, not from event to insert.

## When to reach for it

**Use it** when a table is naturally append-only and time-ordered, and when you want it partitioned without paying for a composite key: events, audit logs, outbox rows, messages, job runs.

**Do not use it** as a general id scheme without thinking about what the timestamp leaks. A UUIDv7 tells anybody who sees it when the row was created, to the millisecond, and consecutive ids from one machine sort together. For a public identifier of something whose creation time is sensitive, that is a disclosure, and the answer is a separate opaque public id.

And keep the timestamp column anyway. It costs eight bytes, it is what humans and reports read, and it is the thing you compare against when a clock turns out to have been wrong.

## The pieces

The bound computation is a codec in [pg-partsmith](https://bedrock-python.github.io/pg-partsmith/): `TimeBoundaries(granularity=MONTH, codec=UUIDv7BoundaryCodec())` on a `RangePartitioning(key="id")`, and everything else — creating ahead, retention, the plan, ownership — works the way it does for a timestamp axis, because the calendar is the same and only the encoding of the bounds changed. There is a codec for epoch integers too, for a key that is milliseconds rather than a UUID.

Partitioning by time without a composite primary key is a real simplification. It just moves the question to who is allowed to mint an id.
