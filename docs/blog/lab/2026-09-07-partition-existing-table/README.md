# Lab: partitioning an existing table in a maintenance window {#lab-partitioning-a-live-table}

Rehearse moving an analytics service's `events` table to monthly partitions. The updated example uses a **maintenance window**: application reads and writes stay paused during the transition. Diagnostic queries observe intermediate states deliberately. It does not promise transparent operation under live traffic.

Docker and `uv` are required. Run from this directory:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python migrate_lab.py
uv run --no-project --python 3.13 --with-requirements requirements.txt python batch_boundary_lab.py
```

`migrate_lab.py` creates 615 historical events across July–September 2026, one application event and twenty notes. It keeps the full original rows for comparison after the migration. Each `PASS` follows assertions against PostgreSQL.

| Check | Expected result |
|---|---|
| Partition by `created_at` with the old `PRIMARY KEY (id)` | SQLSTATE `0A000` |
| Drop the primary key while a foreign key references it | SQLSTATE `2BP01` |
| Try cutover while another transaction holds a read lock | SQLSTATE `55P03`; rollback preserves the table, foreign key and rows |
| Create a July partition while DEFAULT still holds July rows | SQLSTATE `23514` |
| Move one batch of 100 rows | Parent sees 516 rows; the unattached July table holds 100; their combined rows match the original 616 |
| Recreate the toolkit and resume | All months are attached and all saved rows are visible through the parent |
| Read the old view before rebinding | Zero rows counted after legacy data has moved |
| Restore the composite foreign key after the move | Missing timestamp fails with `23502`; an invalid pair fails with `23503` |
| Restore grants, view and sequence ownership, remove empty DEFAULT | The application's original event INSERT works and the sequence advances |
| Compare keys and query plans | Duplicate pair rejected; same id with another timestamp allowed; July query scans one partition |
| Insert outside prepared ranges with no DEFAULT | SQLSTATE `23514` |

`batch_boundary_lab.py` covers the batch boundary: when the batch budget ends right after a batch empties a month, the month's table stays unattached and the parent shows none of its rows. `plan()` reports it as `unattached_rows`, and the next `partition_data` call attaches it (pg-partsmith 1.5.1 could leave such a month hidden while reporting `complete=True`; 1.7.0 fixed that). The test compares all 100 original rows through the parent afterwards.

`migration_flow.py` contains the article's functions; `schema.sql` is the starting schema, including the reporting view and application role. Application event SQL stays the same, but note writers must now provide both `event_id` and `event_created_at`. Application pause/drain is a prerequisite for these database steps, not an HTTP maintenance-mode implementation supplied by the lab.

Python dependencies are pinned: pg-partsmith 1.8.0, SQLAlchemy 2.0.54, asyncpg 0.31.0, pydantic 2.13.5 and testcontainers 4.15.0. The container uses `postgres:17-alpine` and is removed on exit. Fixed dates and small data make this a correctness check, not a benchmark for production lock durations. No automatic retention cycle runs during migration.

[Read the article](../../posts/2026-10-17-partitioning-an-existing-postgresql-table.md).
