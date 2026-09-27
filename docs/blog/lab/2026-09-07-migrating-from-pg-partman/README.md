# Lab: adopting a pg_partman-managed table {#lab-adopting-a-pg_partman-managed-table}

A real PostgreSQL 17 container with **pg_partman 5.5.0** creates and maintains a monthly `events` table. The lab then hands it to **pg-partsmith 1.5.1**, verifying table identities and data throughout. See the [maintenance article](../../posts/2026-09-13-postgresql-partition-maintenance.md#migration).

The Dockerfile installs pg_partman from its fixed `v5.5.0` source tag, with no background worker. All maintenance calls belong to the lab, so no old job can race the handover. Python dependencies are pinned through the adjacent retention lab's requirements file. Keep both lab directories when copying the example.

With Docker and `uv` installed, run from this directory:

```bash
docker build -t pg-partman-lab:17 .
uv run --no-project --python 3.13 --with-requirements requirements.txt python partman_lab.py
```

The image build needs access to Debian/PostgreSQL package repositories and GitHub. The script uses a disposable container and checks:

- `partman.create_partition` works with the pinned extension version. Relative month boundaries use PostgreSQL's clock, matching pg_partman's own maintenance clock.
- Setting `automatic_maintenance='off'` stops general maintenance, while a targeted `run_maintenance('public.events')` can still create a needed partition. This is demonstrated before handover.
- Inspection and planning change no tables. Existing `events_p...` names are recognized by bounds, and pg_partman's unmarked detached tables are not adopted for deletion.
- Interval retention of `'3 months'` differs from `KeepNewest(count=3)`. The latter is an explicit new policy, not a lossless conversion. `DropNever()` preserves detached data.
- Removing the table's `part_config` row precedes applying pg-partsmith's plan. Existing OIDs and all rows survive; only the intended old partition detaches.
- Extending the creation horizon produces exactly one new partition. The following plan is empty and DEFAULT remains empty.

`adoption_flow.py` contains the article's policy and unregistration functions; `partman_lab.py` runs the assertions. It imports database helpers from the adjacent `2026-09-07-partition-retention` directory.

For a real handover, save the full configuration and inventory, stop both automatic and explicitly targeted jobs, and wait for active runs before unregistering the table. Compare timezone, interval, template, DEFAULT, publication, and retention settings separately. This example is deliberately limited to a simple monthly table; it is not a universal configuration converter.

Success means four `PASS` lines and exit code 0. The test container is removed on exit; the locally built Docker image remains available for subsequent runs.
