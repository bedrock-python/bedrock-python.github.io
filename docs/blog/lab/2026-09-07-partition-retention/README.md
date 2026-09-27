# Lab: partition retention and a verified archive {#lab-partition-retention-is-not-drop-table}

Run the analytics-service example from the [partition maintenance article](../../posts/2026-09-13-postgresql-partition-maintenance.md) against a disposable PostgreSQL 17 database. Python 3.13 and pg-partsmith 1.5.1 are used; `requirements.txt` pins the Python dependencies.

With a planning date of September 15, 2026, the policy keeps July–September, prepares October and November, and waits seven days after detachment before deletion. A receipt references a May event. The fixture also includes a two-month partition with a misleading monthly name and an unmarked standalone table.

From this directory, with Docker running and `uv` installed:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python retention_lab.py
```

The script asserts:

- Planning leaves the catalog unchanged; JSON round-tripping preserves the plan, and a changed policy is refused before DDL.
- October and November are created. April and June detach but their rows survive. October inserts work; late April inserts fail without a DEFAULT partition.
- `Unreferenced()` keeps May attached. Without it, PostgreSQL refuses the detach; `success=True` still comes with an issue and the receipt survives.
- A second toolkit on a separate engine cannot maintain a table whose advisory lock is held. It can acquire the lock after release.
- The seven-day grace threshold is respected. A failing archive hook or an incorrect existing archive prevents deletion.
- A successful retry drops April and June only after writing and rereading their JSON files. All four rows are restored into a temporary table and compared with the originals.
- Deleting the receipt makes manually created May eligible. The two-month partition and unmarked standalone table remain intact.

`maintenance_flow.py` contains the exact policy, planning, archive, and scheduler snippets used in both article languages. `lab_support.py` provides the disposable database and shared assertions. `retention_lab.py` is the executable scenario.

The lab advances the **planning argument** `now` to test grace expiry without waiting a week, then applies only the drop portion of that plan. It never changes the seven-day policy. The lock-contention test calls the real scheduled API while another worker holds the lock, so it cannot alter the fixed-date fixture.

The JSON archive is local, temporary, and small enough to load in memory. It is removed after the restoration assertions. This is a hook and recovery example, not a persistent backup service. The application must not write directly to detached tables between export and drop. A production archive needs durable storage, streaming for large tables, and its own recovery checks.

Expected warning messages are part of the foreign-key, lock, and archive failure scenarios. Success means all `PASS` lines and exit code 0. The container and temporary archive directory are cleaned up on exit.
